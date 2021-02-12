#!/bin/sh

echo args are: "$@"

# start nebula
# add name
echo generating certificates
./nebula-cert ca -name "Oloi Cloud"
./nebula-cert sign -name "lighthouse" -ip "10.0.0.1/8"

# template IP and port for nebula config
echo starting Nebula lighthouse
./nebula -config ./nebula-lh-config.yaml &

# start flask
echo starting lighthouse API
cd ./lighthouse-api
exec gunicorn --bind :8080 --workers 1 --threads 8 --timeout 0 main:app