#!/usr/bin/env bash

set -e

arg=$1
# Change this to the account you have access with.
server_account="webbu"
server_fqdn="ssh.new.d-sektionen.se"
# Add the webhooks from respective stack in container.
backend_dev_webhook_url="REPLACE_ME_WITH_WEBHOOK"
backend_prod_webhook_url="REPLACE_ME_WITH_WEBHOOK"

RED="\e[91m"
ENDCOLOR="\e[0m"

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
    webhook_url=$backend_dev_webhook_url

elif [ "$arg" = "prod" ]; then
    prompt_yes_no "Do you really want to deploy to ${RED}PRODUCTION${ENDCOLOR}?"
    webhook_url=$backend_prod_webhook_url

else
    echo -e "First argument should be either ${RED}dev${ENDCOLOR} or ${RED}prod${ENDCOLOR}"
    exit
fi

set -x
# Assumes you have ssh keys to the server account.
ssh $server_account@$server_fqdn "curl -X POST $webhook_url"
