## This is a proof of concept

# Oloi distributed private cloud
Oloi distributed private cloud is a distributed Kubernetes cluster on a VPN Network mesh allowing true independant private hybrid cloud implementation without complicated setup.
The goal is make the deployment and operation of the cluster as hassle free as possible. Production ready distributed cloud within minutes!

**NOTE: The network stack has trouble routing between pods on different nodes**

## Concepts
This setup works with some core concepts that are useful to read to understand the implications.

### VPN Network mesh
The stack runs on the Nebula VPN mesh overlay, connecting all containers into a single private network. The VPN mesh overlay used has been build by the Slack team and uses UDP hole punching to allow machines behind firewalls to connect to a Lighthouse without a complicated networking setup.

### Oloi Lighthouse
The core component in the stack and the only component that needs a direct routable IP address. The Lighthouse provides an API that allows server and nodes to connect and join the Nebula VPN mesh. The Lighthouse generates an authentication token that all other nodes need to provide in order to connect.

Future developments:
- [] HA Lighthouse setup
- [] Registration/eviction node management
- [] API leader election in HA setup
- [] Generate self-signed certificate for Lighthouse API and use HTTPS for endpoints

### Oloi Server
The K3s master server. It registers itself at the Lighthouse with its IP address and K3s token, which in turn can be used by the K3s nodes to join the K3s cluster.

Future developments:
- [] HA K3s server setup using embedded etcd
- [] Distributed etcd backup
- [] Routable Kubernetes API with authentication
- [] OIDC configuration

### Oloi Node
The K3s agent nodes. After joining the VPN mesh using the Lighthouse authentication token, it retrieves the K3s server information from the Lighthouse API and joins the K3s cluster. Each node can route traffic from port 80 and 443 to the relevant kubernetes services further in the mesh. So depending on the scale required, only a single public routable node should be necessary to route traffic. Alternativly multiple private nodes can be placed behind a public loadbalancer to achieve an HA setup for web traffic routing.

Future developments:
- [] Use the node name generation as both vpn mesh hostname and Kubernetes hostname
- [] Node grouping using Kubernetes taint and/or affinity functionality to give Kubernetes resource grouping options

## Requirements
- At least 1 machine with a routable IP
- Docker
- Thats it. Pretty neat.

## Deploying Oloi Cloud
Deploying an Oloi Cloud environment use the following steps:

### Lighthouse setup
- First deploy the Lighthouse on a machine with a routable IP address (can be internal or external). Make sure UDP port 4242 is open for the VPN mesh and TCP port 8080 for the API.
- Start Lighthouse:
```
docker run --privileged -p 4242:4242/udp -p 8080:8080/tcp -e CLOUD_NAME="<NAME>" gcr.io/incentro-oss/oloi-lighthouse:latest
```
- The Lighthouse generates an authentication token, store it somewhere safe. You need it when deploying the other nodes.

### Server setup
- The machine must be able to route traffic to the Lighthouse API. If the Lighthouse is not reachable, the server cannot start.
- Start server:
```
docker run --privileged -p 6443:6443 && \
        --tmpfs "/run" && \
        --tmpfs "/var/run" && \
        -e NODE_PREFIX="<NODE_NAME_PREFIX>" && \
        -e OLOI_AUTH_TOKEN="<AUTH_TOKEN>" && \
        -e OLOI_LIGHTHOUSE_IP="<LIGHTHOUSE_IP>:8080" && \
        gcr.io/incentro-oss/oloi-server:latest
```
- The server will automatically join the vpn mesh and register its join data at the Lighthouse

### Node setup
- The machine must be able to route traffic to the Lighthouse API. If the Lighthouse is not reachable, the node cannot start.
- Start node:
```
docker run --privileged && \
        -p 80:80 && \
        -p 443:443 && \
        --tmpfs "/run" && \
        --tmpfs "/var/run" && \
        -e NODE_PREFIX="<NODE_NAME_PREFIX>" && \
        -e OLOI_AUTH_TOKEN="<AUTH_TOKEN>" && \
        -e OLOI_LIGHTHOUSE_IP="<LIGHTHOUSE_IP>:8080" && \
        gcr.io/incentro-oss/oloi-node:latest
```
- The node will automatically join the vpn mesh, request Kubernetes join information and join the Kubernetes cluster.

## Running Oloi Cloud locally
Oloi Private Cloud is portable. So all commands above can be executed on a single machine. Use the docker IP of the Lighthouse container as your Oloi Lighthouse IP. If this is the first docker container you start, it is typically 172.17.0.2

## Other future developments
- [] Toggable "cloud" interface for easy management and usage of Kubernetes in corporate environmets.
- [] Go commandline utility to simplify deployment, upgrades and graceful shutdown of components.