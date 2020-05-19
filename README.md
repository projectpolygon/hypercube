# hypercube
A network distributed graphics engine for an use with an array of independant machines

## Slave
To run, from the src directory `python -m slave.slave`

## Master
To run, from the src directory `python -m master.master <jobfile>`
All files specified in the jobfile must be contained in the 'src' directory

## Testing
Tests are run throuhg *pytest*
To install: pip install pytest
To run: `$ src/pytest`
