[![Build Pipeline](https://github.com/projectpolygon/hypercube/workflows/Build%20Pipeline/badge.svg)](https://github.com/projectpolygon/hypercube/actions)
[![codecov](https://codecov.io/gh/projectpolygon/hypercube/branch/master/graph/badge.svg)](https://codecov.io/gh/projectpolygon/hypercube)

# hypercube
A generic network distributed system for an use with an array of independent machines. This allows for a 
normally very heavy task to be broken down into small task that can be distributed over many devices. An 
example that has made use of this distribution is offline ray tracing due to its high cost of system 
resources.

## Slave
Slave nodes require very little setup, simply ensure the compiled app you want to execute a task with is in
the slave machines source directory and run the slave. Any number of slave nodes can be started and each one
will scan the LAN to find and connect to your master node.

To run a slave node, from the src directory:  
`python3 -m slave.slave`

## Master
In order to create the master node you must import its functionality into your application.
Within this app you must set the path to your job directory, list your job files, create the tasks to be executed,
and then start up the master. An example user application can be found [Here](/src/master_app_ex/app.py).

To run the example app, from the src directory:  
`python3 -m master_app_ex.app`  
All files specified in the user app must be contained in your 'job' directory

## Testing
Tests are run through [**pytest**](https://docs.pytest.org/en/latest/)

To install:  
`pip install pytest`

To run:  
`pytest`  
Or to get coverage report run:  
`coverage run -m pytest`

## Docker  
Build and run docker images for Hypercube slave locally
### Build  
To build Docker images navigate to the hypercube directory and run the following:  
`docker build --rm -f "slave.Dockerfile" -t hypercube:slave "."`

### Run  
To run the built Docker images navigate to the hypercube directory and run the following:  
`docker run -it hypercube:slave`
