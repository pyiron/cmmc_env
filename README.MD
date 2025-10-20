# Conda Environment for the CMMC cluster

This conda environment is made available on the cmmc clyser. The environment is built using a [Github Action](https://docs.github.com/en/actions). 

## Keep the environments up to date
This repository uses the [dependabot](https://github.com/dependabot) from Github, to receive automatic pull request when one of the dependencies in the `requirements.txt` file changes. 

Currently, [dependabot](https://github.com/dependabot) does not support conda `environment.yml` files itself, so the conda `environment.yml` are updated by an additional github action based on the changes due to the dependabot PR. 

When updating, adding or removing a dependency it is important to modify both the `requirements.txt` file and the `environment.yml` file. 

There are automated releases each monday and on demand.
