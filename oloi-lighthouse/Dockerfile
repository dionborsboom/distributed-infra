FROM debian:stretch-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y curl jq python3 python3-pip bash ca-certificates git openssl wget iputils-ping && \
    wget https://github.com/slackhq/nebula/releases/download/v1.3.0/nebula-linux-amd64.tar.gz && \
    tar -xf nebula-linux-amd64.tar.gz && \
    chown root:root nebula && \
    chown root:root nebula-cert && \
    rm nebula-linux-amd64.tar.gz

# Print logging directly
ENV PYTHONUNBUFFERED True

# Copy API
COPY . .

# Install api requirements
RUN pip3 install -r ./lighthouse-api/requirements.txt

# Start lighthouse script
ENTRYPOINT ["./start-lighthouse.sh"]