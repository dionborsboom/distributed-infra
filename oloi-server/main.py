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
time.sleep(5)

# Start k3s server
os.system('k3s server &')
# Give the server some time to start before registering
time.sleep(60)

# Retrieve k3s token
with open('/var/lib/rancher/k3s/server/node-token', 'r') as file:
    token = file.read().replace('\n', '')

# Register as cluster server at lighthouse
auth_header = {'Authorization': OLOI_AUTH_TOKEN}
registration_data = {'join_token': token}
response = requests.post("http://"+OLOI_LIGHTHOUSE_IP+"/cluster/server/register", json=registration_data, headers=auth_header)

if response.status_code != 201:
    print("Cluster server registration failed. Shutdown.")
    exit()

# Keep the container running
print("Cluster server registration succeeded.")
while True:
    time.sleep(10)
