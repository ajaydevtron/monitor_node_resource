
import subprocess,os,time
def remove_taint_label(node):
    # Remove label
    label_command = f"kubectl label nodes {node} utilizationhigh-"
    # Remove taint
    taint_command = f"kubectl taint nodes {node} utilizationhigh=true:NoSchedule-"
    
    label_process = subprocess.Popen(label_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_label, stderr_label = label_process.communicate()
    taint_process = subprocess.Popen(taint_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_taint, stderr_taint = taint_process.communicate()
        
    if taint_process.returncode == 0 and label_process.returncode == 0 :
        print(f"\n Taint and label removed to node {node} successed \n ")
    else:
        print(f"\n Oops Error deleting taint or lable to node {node}: {stderr_taint.decode('utf-8').strip()}, {stderr_label.decode('utf-8').strip()}")
    
def get_labeled_nodes():
    command = "kubectl get nodes -l utilizationhigh=true --no-headers=true -o custom-columns=:.metadata.name"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode == 0:
        nodes = stdout.decode("utf-8").strip().split("\n")
        return nodes
    else:
        print(f"Error: {stderr.decode('utf-8').strip()}")
        return []
    
def low_resoucres_limit_nodes(remove_taint_limit_threshold):
    print(f"\nStarting the removal of taint from nodes which have less than {remove_taint_limit_threshold}% resource limit total and had taint .........")
    nodes=get_labeled_nodes()
    print(f"\nAll nodes which have less than {remove_taint_limit_threshold} % resource total limit ",nodes)
    for node in nodes:
        memory_limit=f"kubectl describe node {node} |grep -A3 Resource | grep memory |awk '{{print $5}}' | sed 's/[^0-9.]*//g'"
        cpu_limit=f"kubectl describe node {node} |grep -A3 Resource | grep cpu |awk '{{print $5}}'| sed 's/[^0-9.]*//g'"
        memory_process = subprocess.Popen(memory_limit, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_memory, stderr_memory = memory_process.communicate()
        cpu_process = subprocess.Popen(cpu_limit, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_cpu, stderr_cpu = cpu_process.communicate()
        stdout_memory=stdout_memory.decode("utf-8")
        stdout_cpu=stdout_cpu.decode("utf-8")
        if memory_process.returncode == 0 and cpu_process.returncode == 0 :
            print(f"\n {node} have memory limit: {stdout_memory} and cpu limit : {stdout_cpu} in %")
            if int(stdout_cpu)<remove_taint_limit_threshold and int(stdout_memory)<remove_taint_limit_threshold: 
                remove_taint_label(node)
        else:
            print(f"\n Oops Error to find the cpu and memory limit of node {node}: {stderr_cpu.decode('utf-8').strip()}, {stderr_memory.decode('utf-8').strip()}")
        
def add_taint_label_nodes(node):
    add_label_command = f"kubectl label nodes {node} utilizationhigh=true --overwrite"
    label_process = subprocess.Popen(add_label_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_label, stderr_label = label_process.communicate()
    taint_command = f"kubectl taint nodes {node} utilizationhigh=true:NoSchedule --overwrite"
    taint_process = subprocess.Popen(taint_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_taint, stderr_taint = taint_process.communicate()
    
    if taint_process.returncode == 0 and label_process.returncode == 0 :
        print(f"\n Taint and label added to node {node} successed \n ")
    else:
        print(f"\n Oops Error adding taint or lable to node {node}: {stderr_taint.decode('utf-8').strip()},{stderr_label.decode('utf-8').strip()}")
        
def check_limit_resources_nodes(add_taint_limit_threshold):
    command = "kubectl get nodes --no-headers | awk '{print $1}'"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    # print(stdout)
    if process.returncode == 0:
        nodes = stdout.decode("utf-8").split("\n")[:-1]
        labels_nodes=get_labeled_nodes()
        # final_node=
        final_nodes = [item for item in nodes if item not in labels_nodes]
        print("All nodes ",nodes)
        print("All label nodes", labels_nodes)
        print("Final node ",final_nodes)
        for node in final_nodes:
            # print("node name ", node)
            memory_limit=f"kubectl describe node {node} |grep -A3 Resource | grep memory |awk '{{print $5}}' | sed 's/[^0-9.]*//g'"
            cpu_limit=f"kubectl describe node {node} |grep -A3 Resource | grep cpu |awk '{{print $5}}'| sed 's/[^0-9.]*//g'"
            memory_process = subprocess.Popen(memory_limit, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout_memory, stderr_memory = memory_process.communicate()
            cpu_process = subprocess.Popen(cpu_limit, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout_cpu, stderr_cpu = cpu_process.communicate()
            stdout_memory=stdout_memory.decode("utf-8")
            stdout_cpu=stdout_cpu.decode("utf-8")
            if memory_process.returncode == 0 and cpu_process.returncode == 0 :
                print(f"\n {node} have memory limit: {stdout_memory} and cpu limit : {stdout_cpu} in %")
                if int(stdout_cpu)>=add_taint_limit_threshold or int(stdout_memory)>=add_taint_limit_threshold: 
                    add_taint_label_nodes(node)
            else:
                print(f"\n Oops Error to find the cpu and memory limit of node {node}: {stderr_cpu.decode('utf-8').strip()},{stderr_memory.decode('utf-8').strip()}")
    else:
        print(f"Error: {stderr.decode('utf-8').strip()}")
        return []

if __name__ == "__main__":
    add_taint_limit_threshold= int(os.environ.get("ADD_TAINT_LIMIT_THRESHOLD"))
    remove_taint_limit_threshold=int(os.environ.get("REMOVE_TAINT_LIMIT_THRESHOLD"))
    check_limit_resources_nodes(add_taint_limit_threshold)
    print(f"\n ****** Waiting for 1 min to recheck if any node which had total {add_taint_limit_threshold}% resource limit had exceeded , does it decrease under {remove_taint_limit_threshold} % ? if yes we will remove taint and label")
    time.sleep(60)
    low_resoucres_limit_nodes(remove_taint_limit_threshold)
