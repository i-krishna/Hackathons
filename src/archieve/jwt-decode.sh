#!/bin/bash

# Author: Mihai Criveti
# Description: CLI for WatsonX.AI GA on IBM Cloud (Cloud Pak for Data) using JWT
# Reference: https://cloud.ibm.com/docs/appid?topic=appid-token-validation
# Notes: alg: RS256

# You need to configure the following Variables in your env:

# export IAM_URL="https://iam.test.cloud.ibm.com/identity/token" # DEV
# export IAM_URL="https://iam.cloud.ibm.com/identity/token" # PROD
# export API_KEY=your_ibm_cloud_key_get_this_from_iam # IBM Cloud IAM API Key
# export WML_URL="https://wml-fvt.ml.test.cloud.ibm.com/ml/v1-beta/generation/text?version=2023-05-29" # URL, this depends on what you called your service
# export PROJECT_ID="your_project_id_here"
# export MODEL="google/flan-ul2"
# export INPUT_TEXT="1+1" # input for the query...


# ------------------------------------------------------------------------------
# Functions
# ------------------------------------------------------------------------------

# Get JWT token using IBM Cloud API Key
function get-token() {
  curl -q \
    -X POST "${IAM_URL}" \
    -H 'Content-Type: application/x-www-form-urlencoded' \
    -d "grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey=${API_KEY}" \
    | jq '.access_token' | tr -d '"'
}

# Pad Base64, as JWT is base64url with no signature
pad_jwt() {
  input=$1
  input_characters_number=$(echo -n $input | wc -c)
  while [ $(expr ${input_characters_number} % 4) -ne 0 ]
  do
    input="${input}="
    input_characters_number=$(echo -n ${input} | wc -c)
  done
  echo "${input}"
}

# Decode JWT Token - TODO: add padding..
function jwt-decode() {
  INPUT_TOKEN=$1
  read header payload secret <<< $(echo ${INPUT_TOKEN} | tr [-_] [+/] | sed 's/\./ /g')

  jwt_header=$(pad_jwt ${header})
  jwt_payload=$(pad_jwt ${payload})

  # Format with JQ
  header=$(echo ${jwt_header} | base64 -d | jq)
  payload=$(echo ${jwt_payload} | base64 -d | jq)

  echo "${header}"
  echo "${payload}"
}


# Query
function query_text() {
  curl "${WML_URL}" \
    -H 'Content-Type: application/json' \
    -H 'Accept: application/json' \
    -H "Authorization: Bearer ${JWT}" \
    -d $"{
    \"model_id\": \"${MODEL}\",
    \"input\": \"${INPUT_TEXT}\",
    \"parameters\": {
      \"decoding_method\": \"greedy\",
      \"max_new_tokens\": 20,
      \"min_new_tokens\": 0,
      \"stop_sequences\": [],
      \"repetition_penalty\": 1
    },
    \"project_id\": \"${PROJECT_ID}\"
  }"
}

# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------
JWT=$(get-token)
decoded_token=$(jwt-decode ${JWT})
echo ${JWT}
echo "${decoded_token}"

current_date=$(date +%s)
echo "Current date: ${current_date}"

token_date=$(jwt-decode ${JWT} | jq '.exp' | tail -1)
echo "Token date: ${token_date}"

remaining_time=$((${token_date}-${current_date}))
echo "Remaining time: ${remaining_time} seconds"

query_text
