import os
import sys

from binascii import hexlify

# import startup envs
CLOUD_NAME = os.environ.get('CLOUD_NAME')

# generate nebula certs
print('# Generating Nebula certs #')
os.system('./nebula-cert ca -name '+CLOUD_NAME)
os.system('./nebula-cert sign -name "lighthouse" -ip "10.41.0.1/16"')

# start Nebula VPN mesh
print('# Starting Nebula VPN mesh #')
os.system('./nebula -config ./nebula-lh-config.yaml &')

# generate auth token all nodes need to supply to join
auth_token = hexlify(os.urandom(64))
os.environ['OLOI_AUTH_TOKEN'] = auth_token.decode()
print('### LIGHTHOUSE AUTH TOKEN ###: '+auth_token.decode())

# start api
os.system('exec gunicorn --chdir ./lighthouse-api --bind :8080 --workers 1 --threads 8 --timeout 0 main:app')