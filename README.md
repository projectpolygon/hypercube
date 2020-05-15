# hypercube
A network distributed graphics engine for an use with an array of independant machines

##Docker  
A ubuntu based container with support for opengl and python.
###Build  
To build the Docker container navigate to the hypercube directory and run the following command.
`sudo docker build -t hypercube .`

###Run  
To Run the Docker container without a specific task to run use the following command.
`sudo docker run -it hypercube`
Otherwise if you wish to run a specific command use the following command.
`sudo docker run -it hypercube <my app>` 
Example to run the slave application: `sudo docker run -it hypercube python3 -m slave.slave`

