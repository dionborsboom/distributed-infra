import os
import sys
import requests
import json
import uuid
import yaml
import time

def non_quoted_key(self, data):
   if isinstance(data, ruamel.yaml.compat.string_types):
       data = ruamel.yaml.scalarstring.PlainScalarString(data)
   return self.represent_data(data)

# Set required oloi node envs
NODE_PREFIX = os.environ.get('NODE_PREFIX', 'oloi')
OLOI_AUTH_TOKEN = os.environ.get('OLOI_AUTH_TOKEN', 'none')
OLOI_LIGHTHOUSE_IP = os.environ.get('OLOI_LIGHTHOUSE_IP', '192.168.0.1')
NODE_NAME = NODE_PREFIX+"-"+str(uuid.uuid4().hex)

# generate nebula certs at lighthouse api
print("Requesting mesh join certificates")
auth_header = {'Authorization': OLOI_AUTH_TOKEN}
response = requests.get("http://"+OLOI_LIGHTHOUSE_IP+"/network/register/"+NODE_NAME, headers=auth_header)

if response.status_code == 401:
    print("Invalid auth token. Exiting.")
    exit()

data = json.loads(response.text)

# Store the certificates and keys
print("Storing mesh certificates")
ca_crt_file = open("ca.crt", "w")
ca_crt_file.write(data.get('ca-cert'))
ca_crt_file.close()

host_crt_file = open("host.crt", "w")
host_crt_file.write(data.get('host-cert'))
host_crt_file.close()

host_key_file = open("host.key", "w")
host_key_file.write(data.get('host-key'))
host_key_file.close()

# generate nebula yaml
print("generating mesh configuration")
nebula_node_config = data.get('nebula-config')
nebula_node_yaml = yaml.safe_dump(nebula_node_config, default_flow_style=False)
config_file = open("host-config.yaml", "w")
config_file.write(nebula_node_yaml)
config_file.close()

# start nebula in the background
print("Joining mesh")
os.system('./nebula -config ./host-config.yaml &')
time.sleep(10)

# retrieve k3s cluster join data
print("Requesting cluster join information")
auth_header = {'Authorization': OLOI_AUTH_TOKEN}
response = requests.get("http://10.41.0.1:8080/cluster/agent/join", headers=auth_header)

if response.status_code != 200:
    print("No cluster server found. Exiting.")
    exit()

data = json.loads(response.text)

os.environ["K3S_URL"] = "https://"+data.get('server_ip')+":6443"
os.environ["K3S_TOKEN"] = data.get('join_token')

# Retrieve IP of this node in the mesh
print("Retrieving node IP in mesh")
auth_header = {'Authorization': OLOI_AUTH_TOKEN}
response = requests.get("http://10.41.0.1:8080/network/ip", headers=auth_header)

if response.status_code == 401:
    print("Invalid auth token. Exiting.")
    exit()

ip_data = json.loads(response.text)

# start k3s agent
print("Joining cluster as node")
os.system('k3s agent --flannel-iface nebula1 --node-ip '+ip_data.get('ip_address')+' &')

# Keep the container running
print("Cluster agent joined.")
while True:
    time.sleep(10)
