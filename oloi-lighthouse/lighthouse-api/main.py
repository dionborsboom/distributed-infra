import os
import ruamel.yaml
import json
import subprocess

from ipaddress import IPv4Network

from flask import Flask, Response
from flask import request

app = Flask(__name__)

NEBULA_CA_CERT = open("../ca.crt", "r").read()

# Create the network
network = IPv4Network('10.0.0.0/8')
used_addresses = ['10.0.0.1']
hosts_iterator = (host for host in network.hosts() if str(host) not in used_addresses)

# Cluster server info
cluster_server_ip = None
cluster_join_token = None


# Join Nebula
# TODO: add token authentication
@app.route('/network/register/<host>', methods = ['GET'])
def connect_configuration(host):
    print("Generating node certificates")

    # IP allocation
    global used_addresses
    address = next(hosts_iterator)
    used_addresses.append(address)

    # generate host cert and key
    subprocess.run(["../nebula-cert", "sign", 
                    "-ca-crt", "../ca.crt", 
                    "-ca-key", "../ca.key", 
                    "-name", host,
                    "-ip", str(address)+"/8",
                    "-out-crt", "../"+host+".crt",
                    "-out-key", "../"+host+".key"])

    # Load generated certificates
    host_cert = open("../"+host+".crt", "r").read()
    host_key = open("../"+host+".key", "r").read()

    host_config = {
        "pki": {
            "ca": "ca.crt",
            "cert": "host.crt",
            "key": "host.key"
        },
        "static_host_map": {
			"10.0.0.1": ["172.17.0.2:4242"]
		},
        "tun": {
			"dev": "nebula1",
			"disabled": False,
			"drop_local_broadcast": False,
			"drop_multicast": False,
			"mtu": 1300,
			"routes": None,
			"tx_queue": 500,
			"unsafe_routes": None
		},
        "punchy": {
			"punch": True
		},
        "firewall": {
			"conntrack": {
				"default_timeout": "10m",
				"max_connections": 100000,
				"tcp_timeout": "12m",
				"udp_timeout": "3m"
			},
			"inbound": [{
				"host": "any",
				"port": "any",
				"proto": "any"
			}],
			"outbound": [{
				"host": "any",
				"port": "any",
				"proto": "any"
			}]
		},
        "listen": {
			"host": "0.0.0.0",
			"port": 0
		},
        "lighthouse": {
			"am_lighthouse": False,
			"interval": 60,
            "hosts": ["10.0.0.1"]
		},
    }

    node_config = {
        "nebula-config": host_config,
        "ca-cert": NEBULA_CA_CERT,
        "host-cert": host_cert,
        "host-key": host_key
    }

    return node_config


# Register cluster server node
@app.route('/cluster/server/register', methods = ['POST'])
def register_server():
    request_data = request.get_json()

    global cluster_server_ip
    global cluster_join_token
    
    cluster_server_ip = request.remote_addr
    cluster_join_token = request_data['join_token']

    print("Registered "+cluster_server_ip+" as server.")

    if cluster_join_token is None or cluster_server_ip is None:
        status_code = Response(status=400)
    else:
        status_code = Response(status=201)

    return status_code


# Get cluster join info
@app.route('/cluster/agent/join', methods = ['GET'])
def register_agent():
    global cluster_server_ip
    global cluster_join_token

    if cluster_server_ip is None or cluster_join_token is None:
        status_code = Response(status=404)
        return status_code

    response = {
        "server_ip": cluster_server_ip,
        "join_token": cluster_join_token
    }

    return response


# Health
# TODO: add token authentication
@app.route('/healthz')
def healthz():
    return "OK"


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(8080))