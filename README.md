# EEEE3114-Machine-CW1

Coursework 1 for EEEE3114 machine coursework 1. This repository is split into two section, python and MATLAB. They store the same code but in different programming language.

## Introduction

This repository contains code to simulate a permanent magnet synchronous motor (PMSM). This is down by performing FEA (finite element analysis) using the [FEMM](https://www.femm.info/wiki/Download) software. The simulations are split into task specified in the `EEEE3114- Design Exercise Handout.pdf`.

Two report is also written to analyse the results of the simulation. The first report (part 1) analyse the results from task 1 to task 6. The second report (part 2) analyse the rest of the task. The report is written in LaTeX. The source code for the LaTeX documents can be found [here](https://github.com/ecyht2/EEEE3114-Electrical-Machines-Drive-Systems-and-Applications-CW1.git).

## Requirements

FEMM is required to be installed on your system. The download can be found [here](https://www.femm.info/wiki/Download).

A Makefile is used to run the python scripts. Make sure that GNUMake is also installed. It can be downloaded [here](https://www.gnu.org/software/make/)

### Python

Each task is split into their own scripts. The scripts can be run individually using the `Makefile`.

The scripts have a total of 3 dependencies:

- [pyfemm](https://pypi.org/project/pyfemm)
- [numpy](https://pypi.org/project/numpy)
- [matplotlib](https://pypi.org/project/matplotlib)

There are also developer dependencies:

- [python-lsp-server](https://pypi.org/project/python-lsp-server)
- [pylint](https://pypi.org/project/pylint)
- [pylsp-mypy](https://pypi.org/project/pylsp-mypy)
- [python-lsp-black](https://pypi.org/project/python-lsp-black)

This project uses [Pipenv](https://pipenv.pypa.io/en/latest/) to manage the dependencies. After installing it, simply change to the `python` directory and run `pipenv install`. This will install all the dependencies required. To enter the virtual environment do `pipenv shell`.

### Matlab

All the functions used are defined in MATLAB. No other requirements are needed except for the latest version of [MATLAB](https://www.mathworks.com/products/matlab.html).
