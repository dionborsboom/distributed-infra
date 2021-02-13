FROM rancher/k3s:v1.20.2-k3s1 as k3s

FROM debian:stretch-slim

# Install Nebula and Python
RUN apt-get update && \
    apt-get install -y curl jq python3 python3-pip bash ca-certificates git openssl wget iputils-ping && \
    wget https://github.com/slackhq/nebula/releases/download/v1.3.0/nebula-linux-amd64.tar.gz && \
    tar -xf nebula-linux-amd64.tar.gz && \
    chown root:root nebula && \
    chown root:root nebula-cert && \
    rm nebula-linux-amd64.tar.gz

# Install k3s
COPY --from=k3s / /
RUN mkdir -p /etc && \
    echo 'hosts: files dns' > /etc/nsswitch.conf
RUN chmod 1777 /tmp
VOLUME /var/lib/kubelet
VOLUME /var/lib/rancher/k3s
VOLUME /var/lib/cni
VOLUME /var/log
ENV PATH="$PATH:/bin/aux"
ENV CRI_CONFIG_FILE="/var/lib/rancher/k3s/agent/etc/crictl.yaml"

# Print logging directly
ENV PYTHONUNBUFFERED True

# Copy files
COPY . .

# Install requirements
RUN pip3 install -r ./requirements.txt

# Start join script
CMD ["python3", "main.py"]