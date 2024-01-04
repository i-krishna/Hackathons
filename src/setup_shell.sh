#!/bin/bash

# You'll want to run this script with "source", i.e.
#
#     source ./setup_shell.sh
#

#
# NOTE: Use "return" rather than "exit" so you don't exit the shell!
#

#
# Assume API key is in apikey.json. If you can't find it,
#
if [ -f apikey.json ]
then
    export API_KEY=$(jq ".apikey" < apikey.json | tr -d '"')
else
    echo "Please download apikey.json" >&2
    return 1
fi

export PROJECT_ID="34868e5b-6aed-4730-a8a9-a367fb3c82d1"

pip3 install --upgrade jupyter ibm-cloud-sdk-core python-docx requests

# Put getpass.py into same directory as notebooks
cp $HOME/watsonx-jwt-auth/getpass.py $HOME

export PATH=$PATH:$HOME/.local/bin

return 0
