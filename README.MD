# Conda Environment for the CMMC cluster

This conda environment is made available on the cmmc cluster. The environment is built using a [Github Action](https://docs.github.com/en/actions). 

## Keep the environments up to date
This repository uses the [dependabot](https://github.com/dependabot) from Github, to receive automatic pull request when one of the dependencies in the `requirements.txt` file changes. 

Currently, [dependabot](https://github.com/dependabot) does not support conda `environment.yml` files itself, so the conda `environment.yml` are updated by an additional github action based on the changes due to the dependabot PR. 

When updating, adding or removing a dependency it is important to modify both the `requirements.txt` file and the `environment.yml` file. 

## Scheduled releases

There are automated releases each monday evening and on demand.

## Installation on the cluster

The installation on the cluster happens with a cron job in the night to Tuesday (3 a.m.):
- The `env-linux-x64-${DATE}.yml` file of the latest release is downloaded.
- The `_x86_64-microarch-level` dependency is removed from the environment.yml file.
- The environment 
  - is `mamba env create`d
  - and compiled
- Finally, the environment is exposed via a shared kernel and module files.

