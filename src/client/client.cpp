#include <iostream>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <string.h>

const int PORT = 8080;
const int bufsize = 1024;
const int MAX_PEN = 4;

int main(void)
{
	int server_fd;
	int new_socket;
	int actually_read;
	int opt = 1;
	struct sockaddr_in address;
	int addrlen = sizeof(address);
	char buffer[bufsize + 1] = {0};
	std::string file;
	
	if((server_fd = socket(AF_INET, SOCK_STREAM,  0)) == 0){
		// handle error	
	}

	if(setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT, &opt, sizeof(opt) )){
		// handle error	
	}
	
	address.sin_family = AF_INET;
	address.sin_addr.s_addr = INADDR_ANY;
	address.sin_port = htons(PORT);

	if(bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0){
		// handle error	
	}

	if(listen(server_fd, MAX_PEN) < 0){
		// handle error	
	}

	if((new_socket = accept(server_fd, (struct sockaddr *)&address, (socklen_t*)&addrlen)) < 0){
		// handle error	
	}
	
	actually_read = read(new_socket, buffer, bufsize);

	while(actually_read > 0){
		printf("%s\n", buffer);
		file.append(buffer);
		memset(buffer, 0, bufsize); 
		actually_read = read(new_socket, buffer, bufsize);
		std::cout << "VALREAD WAS " << actually_read << std::endl;
	}
	std::cout << "BUFFER: " << file << std::endl;
	std::cout << "END";

	
} 	
