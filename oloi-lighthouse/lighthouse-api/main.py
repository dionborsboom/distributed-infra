import os
import ruamel.yaml
import json
import subprocess

from ipaddress import IPv4Network

from flask import Flask
app = Flask(__name__)

NEBULA_CA_CERT = open("../ca.crt", "r").read()

# Create the network
network = IPv4Network('10.0.0.0/8')
used_addresses = ['10.0.0.1']
hosts_iterator = (host for host in network.hosts() if str(host) not in used_addresses)

# Join Nebula
# TODO: add token authentication
@app.route('/join/<host>')
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


# Health
# TODO: add token authentication
@app.route('/healthz')
def healthz():
    return "OK"


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(8080))