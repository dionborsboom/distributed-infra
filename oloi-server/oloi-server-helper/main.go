package main

import (
	"fmt"
	"os/exec"
	"os"
  )

func main() {
	//var serverDB string = os.Getenv("SERVER_DB")
	var advertiseAddress string = os.Getenv("ADVERTISE_ADDRESS")
	var tlsSan string = os.Getenv("TLS_SAN")

	// run k3s server
	cmd := exec.Command("/bin/k3s", "server", "--advertise-address", advertiseAddress, "--tls-san", tlsSan)
    stdout, err := cmd.Output()

    if err != nil {
        fmt.Println(err.Error())
        return
    }

    fmt.Print(string(stdout))
}