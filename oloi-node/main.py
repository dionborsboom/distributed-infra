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
# TODO: required envs
NODE_PREFIX = os.environ.get('NODE_PREFIX')
OLOI_LIGHTHOUSE_IP = os.environ.get('OLOI_LIGHTHOUSE_IP')
NODE_NAME = NODE_PREFIX+"-"+str(uuid.uuid4().hex)

# generate nebula certs at lighthouse api
print("Requesting mesh join certificates")
response = requests.get("http://"+OLOI_LIGHTHOUSE_IP+"/network/register/"+NODE_NAME)
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

# retrieve k3s cluster join data
print("Requesting cluster join information")
response = requests.get("http://"+OLOI_LIGHTHOUSE_IP+"/cluster/agent/join")

if response.status_code is not 200:
    print("No cluster server found. Exiting.")
    exit()

data = json.loads(response.text)

os.environ["K3S_URL"] = "https://"+data.get('server_ip')+":6443"
os.environ["K3S_TOKEN"] = data.get('join_token')

# start k3s agent
os.system('k3s agent &')

# Keep the container running
print("Cluster agent joined.")
while True:
    time.sleep(10)
