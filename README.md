# hypercube
A network distributed graphics engine for an use with an array of independant machines

## Slave
To run, from the src directory `python -m slave.slave`

## Master
To run, from the src directory `python -m master.master <jobfile>`
All files specified in the jobfile must be contained in the 'src' directory

## Testing
Tests are run throuhg *pytest*
To install: `pip install pytest`
To run: `$ src/pytest`

## Docker  
A ubuntu based container with support for opengl and python.
### Build  
To build the Docker container navigate to the hypercube directory and run the following command.  
`sudo docker build -t hypercube .`  

### Run  
To Run the Docker container without a specific task to run use the following command.  
`sudo docker run -it hypercube`  
Otherwise if you wish to run a specific command use the following command.  
`sudo docker run -it hypercube <my app>`  
Example to run the slave application: `sudo docker run -it hypercube python3 -m slave.slave`  

