#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
arg=$1
registry_url="registry.d-sektionen.se"
backend_dev_tag="development"
backend_prod_tag="latest"

if [ "$arg" = "dev" ]; then
    tag=$backend_dev_tag
elif [ "$arg" = "prod" ]; then
    tag=$backend_prod_tag
else
    echo "First argument should be either 'dev' or 'prod'"
    exit
fi

set -x
docker login https://$registry_url
docker build -t $registry_url/backend:$tag -f $SCRIPT_DIR/Dockerfile .
docker push $registry_url/backend:$tag