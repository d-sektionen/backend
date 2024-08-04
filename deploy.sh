#!/usr/bin/env bash

arg=$1
# Change this to the account you have access with.
server_account="webbu"
# Add the webhooks from respective stack in container.
backend_dev_webhook="REPLACE_ME_WITH_WEBHOOK"
backend_prod_webhook="REPLACE_ME_WITH_WEBHOOK"

if [ "$arg" = "dev" ]; then
    webhook="$backend_dev_webhook"
elif [ "$arg" = "prod" ]; then
    webhook="$backend_prod_webhook"
else
    echo "First argument should be either 'dev' or 'prod'"
    exit
fi

set -x
# Assumes you have ssh keys to the server account.
ssh $server_account@ssh.new.d-sektionen.se "curl -X POST $webhook"
