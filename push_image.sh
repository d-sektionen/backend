#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
arg=$1
backend_dev_tag="development"
backend_prod_tag="latest"

if [ "$arg" = "dev" ]; then
    tag="$backend_dev_webhook"
elif [ "$arg" = "prod" ]; then
    tag="$backend_prod_webhook"
else
    echo "First argument should be either 'dev' or 'prod'"
    exit
fi

set -x
# Credentials are given by webmaster
docker login https://registry.d-sektionen.se
docker build --push -t registry.d-sektionen.se/backend:$tag -f $SCRIPT_DIR/Dockerfile