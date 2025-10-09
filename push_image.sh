#!/usr/bin/env bash

set -e

arg=$1
# Change these if necessary.
registry_fqdn="registry.d-sektionen.se"
image_name="backend"
backend_dev_tag="development"
backend_prod_tag="latest"

RED="\e[91m"
ENDCOLOR="\e[0m"
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

prompt_yes_no() {
    while true; do
        echo -en "$1 [y/n]: "
        read yn
        case $yn in
            [Yy]* ) break;;
            [Nn]* ) exit;;
        esac
    done
}

if [ "$arg" = "dev" ]; then
    image_tag=$backend_dev_tag

elif [ "$arg" = "prod" ]; then
    prompt_yes_no "Do you really want to push to ${RED}PRODUCTION${ENDCOLOR}?"
    image_tag=$backend_prod_tag

else
    echo -e "First argument should be either ${RED}dev${ENDCOLOR} or ${RED}prod${ENDCOLOR}"
    exit
fi

docker_image="$registry_fqdn/$image_name:$image_tag"

set -x
# Get login credentials from webmaster
docker login https://$registry_fqdn
docker build -t $docker_image -f $SCRIPT_DIR/Dockerfile .
docker push $docker_image