import subprocess
import time

def remove_taint_label(node):
    # Remove label
    label_command = f"kubectl label nodes {node} utilizationhigh-"

    # Remove taint
    taint_command = f"kubectl taint nodes {node} utilizationhigh=true:NoSchedule-"
    
    label_process = subprocess.Popen(label_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = label_process.communicate()
    taint_process = subprocess.Popen(taint_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = taint_process.communicate()
        
    if taint_process.returncode == 0 and label_process.returncode == 0 :
        print(f"\n Taint and label removed to node {node} successed \n ")
    else:
        print(f"\n Oops Error deleting taint or lable to node {node}: {stderr.decode('utf-8').strip()}")
        
    
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


def add_taint_to_nodes(node):
    # print(node)
    # adding the taint and label to the nodes 
    add_label_command = f"kubectl label nodes {node} utilizationhigh=true"
    label_process = subprocess.Popen(add_label_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = label_process.communicate()
    taint_command = f"kubectl taint nodes {node} utilizationhigh=true:NoSchedule --overwrite"
    taint_process = subprocess.Popen(taint_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = taint_process.communicate()
    
    if taint_process.returncode == 0 and label_process.returncode == 0 :
        print(f"\n Taint and label added to node {node} successed \n ")
    else:
        print(f"\n Oops Error adding taint or lable to node {node}: {stderr.decode('utf-8').strip()}")


def low_utilization_nodes(node,threshold):
    # print(node,threshold)
    command = f"kubectl top node {node} --no-headers=true"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    # print(stdout,stderr)
    if process.returncode == 0:
        # print(stdout)
        # line = stdout.decode("utf-8").split("\n")
        lines = stdout.decode("utf-8").split("\n")
        # print(lines)
        for line in lines:
            if line.strip():
                columns = line.split()
                node_name = columns[0]
                # print(columns,node_name)
                cpu_utilization = float(columns[2].rstrip("%"))
                memory_utilization = float(columns[4].rstrip("%"))
                if cpu_utilization < threshold and memory_utilization < threshold:
                    remove_taint_label(node)
                else:
                    print("\n We are not removing taint and label of this node {} due to its ram and cpu utiization not under 70% ,Current CPU={} and Memory={}".format(node,cpu_utilization,memory_utilization))
    
    else:
        print("Denug")
        print(f"Error: {stderr.decode('utf-8').strip()}")


# return the nodes which have high utilization 
def get_high_utilization_nodes(threshold):
    command = "kubectl top node --no-headers=true"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    if process.returncode == 0:
        nodes = []
        lines = stdout.decode("utf-8").split("\n")
        # print(lines)
        for line in lines:
            if line.strip():
                columns = line.split()
                node_name = columns[0]
                # print(columns,node_name)
                cpu_utilization = float(columns[2].rstrip("%"))
                memory_utilization = float(columns[4].rstrip("%"))
                if cpu_utilization >= threshold or memory_utilization >= threshold:
                    nodes.append(node_name)
        return nodes
    else:
        print(f"Error: {stderr.decode('utf-8').strip()}")
        return []

def main():
    high_utilization_nodes = get_high_utilization_nodes(threshold=80)
    if high_utilization_nodes:
        print(" \n ********** Nodes with 80%+ CPU or Memory Utilization: ********** \n")
        print(high_utilization_nodes)
        for node in high_utilization_nodes:
            # print(node)
            add_taint_to_nodes(node)
    else:
        print("\n ******* No nodes with high CPU or Memory Utilization found. ******** \n")
    print("\n ****** Waiting for 2 min to recheck if any node which had utilization high , does this decrease under 70 % ? if yes we will remove taint and label ")
    time.sleep(10)
    labeled_nodes = get_labeled_nodes()
    if labeled_nodes:
        print("\n ******* Nodes with label utilizationhigh=true: *********")
        print(labeled_nodes)
        for node in labeled_nodes:
            low_utilization_nodes(node,threshold=70)
    else:
        print("\n *********No nodes with the specified label found. ******* \n")



if __name__ == "__main__":
    main()
