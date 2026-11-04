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
import os
from pathlib import Path

path = Path(os.environ["HOME"]) / "environment.yml"
target = Path("/tmp/environment.yml")
requirements = Path("/tmp/pip-requirements.txt")
lines = path.read_text().splitlines(keepends=True)
pip_start = next(
    (index for index, line in enumerate(lines) if line.rstrip("\r\n") == "- pip:"),
    None,
)
if pip_start is None:
    raise SystemExit("expected pip block not found in environment.yml")

pip_end = pip_start + 1
pip_packages = []
while pip_end < len(lines):
    line = lines[pip_end]
    if not line.strip():
        pip_end += 1
        continue
    if not line[0].isspace():
        break
    package = line.strip()
    if not package.startswith("- "):
        raise SystemExit("unsupported entry in environment.yml pip block")
    pip_packages.append(package[2:])
    pip_end += 1

if not pip_packages:
    raise SystemExit("expected packages in environment.yml pip block")

target.write_text("".join(lines[:pip_start] + lines[pip_end:]))
requirements.write_text("\n".join(pip_packages) + "\n")
PY
RUN mamba env update -n base -f /tmp/environment.yml && \
    pip install --no-cache-dir -r /tmp/pip-requirements.txt && \
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
