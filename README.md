![Build Pipeline](https://github.com/projectpolygon/hypercube/workflows/Build%20Pipeline/badge.svg)

# hypercube
A network distributed graphics engine for an use with an array of independant machines

## Slave
To run, from the src directory `python -m slave.slave`

## Master
To run, from the src directory:
`python -m master.master`
All files specified in the jobfile must be contained in the 'src' directory

## Testing
Tests are run through [**pytest**](https://docs.pytest.org/en/latest/)

To install: `pip install pytest`

To run: `pytest`

## Docker  
Build and run docker images for Hypercube master and slave locally
### Build  
To build the Docker images navigate to the hypercube directory and run the following:
#### Master
`docker build --rm -f "master.Dockerfile" -t hypercube:master "."`
#### Slave
`docker build --rm -f "slave.Dockerfile" -t hypercube:slave "."`

### Run  
To run the built Docker images navigate to the hypercube directory and run the following:
#### Master
`docker run -it -p 5678:5678 hypercube:master`
#### Slave
`docker run -it hypercube:slave`

## Graphics Slave Application
### Configure
`cmake -H. -B[build_dir]`
### Build
`cmake --build [build_dir] --target app`
### Run
`./[build_dir]/app ./path/to/graphics_payload.json`
