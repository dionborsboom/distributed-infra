build-node:
	docker build -t oloi-node:latest ./oloi-node

run:
	docker run --privileged \
			--tmpfs "/run" \
			--tmpfs "/var/run" \
			oloi-node:latest 

test:
	docker run --privileged \
			--tmpfs "/run" \
			--tmpfs "/var/run" \
			-e K3S_URL='https://10.1.1.20:6443' \
			-e K3S_TOKEN='K10c2eff9f4993ed6eff46ab2a04553f7ba8048e7d9efcbc990d68b056e316f6d2f::server:325321618a19eb1deb19af3bec266e74' \
			rancher/k3s:v1.16.7-k3s1

go:
	go run ./oloi-node/oloi-svc/main.go