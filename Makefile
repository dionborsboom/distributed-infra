build-lighthouse:
	docker build -t gcr.io/incentro-oss/oloi-lighthouse:latest ./oloi-lighthouse

build-node:
	docker build -t gcr.io/incentro-oss/oloi-node:latest ./oloi-node

build-server:
	docker build -t gcr.io/incentro-oss/oloi-server:latest ./oloi-server

run-lighthouse:
	docker run --privileged \
				-p 4242:4242/udp \
				-p 8080:8080/tcp \
				gcr.io/incentro-oss/oloi-lighthouse:latest eyyyy

run-node:
	docker run --privileged \
			-p 80:80 \
			--tmpfs "/run" \
			--tmpfs "/var/run" \
			-e NODE_PREFIX="local" \
			-e OLOI_LIGHTHOUSE_IP="172.17.0.2:8080" \
			gcr.io/incentro-oss/oloi-node:latest

run-server:
	docker run --privileged \
			-p 6443:6443 \
			--tmpfs "/run" \
			--tmpfs "/var/run" \
			-e NODE_PREFIX="server" \
			-e OLOI_LIGHTHOUSE_IP="172.17.0.2:8080" \
			gcr.io/incentro-oss/oloi-server:latest

push-node:
	docker push gcr.io/incentro-oss/oloi-node:latest

push-server:
	docker push gcr.io/incentro-oss/oloi-server:latest

go-node:
	go run ./oloi-node/oloi-svc/main.go