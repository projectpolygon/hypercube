package main

import (
	"fmt"
	"net"
)

func main() {
	conn, err := net.Dial("tcp","192.168.1.71:14444")
	if err != nil {
		fmt.Println("ERR: connection not made")
		return
	}

	conn.Write([]byte("This is the message to send"))
	conn.Close()
}
