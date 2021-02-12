# Application builder
FROM golang:alpine AS builder

ENV GO111MODULE=on \
    CGO_ENABLED=0 \
    GOOS=linux \
    GOARCH=amd64

COPY oloi-server-helper/ /oloi-server-helper/

WORKDIR /oloi-server-helper

RUN go build -o main .

# k3s application container
FROM rancher/k3s:v1.18.9-k3s1

## Add google NS to /etc/resolv.conf
RUN echo "nameserver 8.8.8.8" > /etc/resolv.conf

COPY --from=builder /oloi-server-helper/main main

# install envoy

# Run the oloi-server-helper
#ENTRYPOINT ["/bin/sh", "-c"]
CMD ["server"]

