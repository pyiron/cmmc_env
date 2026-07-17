ARG ROOT_IMAGE=quay.io/jupyter/base-notebook:82d322f00937 AS root_image
FROM $ROOT_IMAGE

LABEL org.opencontainers.image.authors="Niklas Siemer <n.siemer@mpi-susmat.de>"

ARG DOCKER_UID="1000"
ARG DOCKER_GID="100"

# Configure environment
ENV CONDA_DIR=/opt/conda \
    SHELL=/bin/bash \
    LC_ALL=en_US.UTF-8 \
    LANG=en_US.UTF-8 \
    LANGUAGE=en_US.UTF-8 \
    DOCKER_UID=$DOCKER_UID \
    DOCKER_GID=$DOCKER_GID \
    HOME=/home/$NB_USER \
    OMPI_MCA_plm=isolated \
    OMPI_MCA_rmaps_base_oversubscribe=yes \
    OMPI_MCA_btl_vader_single_copy_mechanism=none

# apt installation as root
USER root

# copy list of apt packages to be installed  
COPY apt.txt /tmp/

# install the packages and clean up
RUN apt-get update -y &&\
    xargs -a /tmp/apt.txt apt-get install -y &&\
    apt-get clean &&\
    rm /tmp/apt.txt 

# install conda packages as $DOCKER_USER
USER ${DOCKER_UID}
WORKDIR ${HOME}
ARG PYTHON_VERSION=default

COPY . ${HOME}/
RUN python - <<'PY'
from pathlib import Path

path = Path("/home/jovyan/environment.yml")
target = Path("/tmp/environment.yml")
lines = path.read_text().splitlines()
filtered = []
skip_pip_block = False

for line in lines:
    if line in {"- pip", "- pip:"}:
        skip_pip_block = True
        continue
    if skip_pip_block and line.startswith("  - "):
        continue
    skip_pip_block = False
    filtered.append(line)

target.write_text("\n".join(filtered) + "\n")
PY
RUN mamba env update -n base -f /tmp/environment.yml && \
    pip install --no-cache-dir marimo-jupyter-extension==0.3.0 && \
    mamba clean --all -f -y && \
    mamba list

# Fix permissions on /etc/jupyter as root
USER root
RUN fix-permissions /etc/jupyter/ &&\
    fix-permissions ${HOME} && \
    fix-permissions ${CONDA_DIR}

# switch back to DOCKER_USER
USER $DOCKER_UID
WORKDIR $HOME
