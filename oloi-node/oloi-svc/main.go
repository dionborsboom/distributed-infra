package main

import (
	"fmt"
	"encoding/json"
	"io/ioutil"
	"net/http"
	"os/exec"
	"os"
  )

type Settings struct {
    Master string `json:"master"`
    Token  string `json:"token"`
}

func main() {
	// Retrieve infra settings from API
	var settings Settings
	resp, err := http.Get("https://storage.googleapis.com/test_dion/api.json")
	if err != nil {
		fmt.Println(err)
	}
	byteValue, _ := ioutil.ReadAll(resp.Body)
	json.Unmarshal(byteValue, &settings)

	// set the k3s values as env vars
	fmt.Printf("master: %s, token: %s", settings.Master, settings.Token)
	os.Setenv("K3S_URL", settings.Master)
	os.Setenv("K3S_TOKEN", settings.Token)

	// configure envoy proxy

	// run envoy proxy

	// configure inlet

	// run inlet

	// run k3s agent
	cmd := exec.Command("/bin/k3s", "agent")
    stdout, err := cmd.Output()

    if err != nil {
        fmt.Println(err.Error())
        return
    }

    fmt.Print(string(stdout))
}