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
OLOI_TOKEN = os.environ.get('OLOI_TOKEN')
NODE_NAME = NODE_PREFIX+"-"+str(uuid.uuid4().hex)

# generate nebula certs at lighthouse api
print("Requesting mesh join certificates")
response = requests.get("http://"+OLOI_LIGHTHOUSE_IP+"/join/"+NODE_NAME)
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

# TODO: start k3s agent
# print('Pinging Lighthouse healthz endpoint on mesh network')
# response = requests.get("http://10.0.0.1:8080/healthz")
# print(response.text)
while True:
    time.sleep(10)