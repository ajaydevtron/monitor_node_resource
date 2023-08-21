FROM ubuntu:20.04
RUN apt update && apt install curl git -y  && apt-get install -y python3-pip python3-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 --no-cache-dir install --upgrade pip \
  && rm -rf /var/lib/apt/lists/*
WORKDIR /app
RUN curl -LO https://storage.googleapis.com/kubernetes-release/release/v1.15.1/bin/linux/arm64/kubectl
RUN chmod u+x kubectl && mv kubectl /bin/kubectl
COPY . .
