package main

import (
	"fmt"
	"net"
)

func main() {
	handle, handle_err := net.Listen("tcp","192.168.1.71:14444")
	if handle_err != nil {
		fmt.Println("ERR: handle not valid")
		return
	}

	for {
		conn, acc_err := handle.Accept()
		if acc_err != nil {
			fmt.Println("ERR: connection not made")
			continue
		}
		
		buffer := make([]byte, 1024)
		_, conn_err := conn.Read(buffer)
		for conn_err == nil {
			fmt.Println(string(buffer))
			_, conn_err = conn.Read(buffer)
		}
	}
}
