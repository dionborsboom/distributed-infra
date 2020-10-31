# Application builder
FROM golang:alpine AS builder

ENV GO111MODULE=on \
    CGO_ENABLED=0 \
    GOOS=linux \
    GOARCH=amd64

COPY oloi-svc/ /oloi-svc/

WORKDIR /oloi-svc

RUN go build -o main .

# k3s application container
FROM rancher/k3s:v1.16.7-k3s1

COPY --from=builder /oloi-svc/main main

# install envoy

# Run the oloi-svc
ENTRYPOINT ["/bin/sh", "-c"]
CMD ["./main"]