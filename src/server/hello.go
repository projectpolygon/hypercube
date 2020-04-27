package main

import (
	"fmt"
	"net"
)

func main() {
	conn, err := net.Dial("tcp","127.0.0.1:8080")
	if err != nil {
		fmt.Println("ERR: connection not made")
		return
	}

	conn.Write([]byte("This is the message to send"))
	conn.Close()
}
