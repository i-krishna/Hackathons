#!/usr/bin/env python3
"""
Author: Mihai Criveti
Description: JWT Tokens for watsonx.ai using Python
Usage: ./watsonx-jwt.py ${JWT_TOKEN} --payload
Usage: ./watsonx-jwt.py ${JWT_TOKEN} --exp
ENV: IAM_URL, API_KEY
"""

import argparse
import base64
import json
import os
import time
import logging

import requests


# -----------------------------------------------------------------------------
# Process JWT
# -----------------------------------------------------------------------------
def pad_jwt(input_str: str) -> str:
    """Pad JWT token (Base64Url)

    Args:
        input_str (str): JWT token

    Returns:
        str: Padded JWT token
    """
    input_str = input_str.encode()
    input_characters_number = len(input_str)

    while input_characters_number % 4 != 0:
        input_str += b'='
        input_characters_number = len(input_str)

    return input_str

def jwt_decode(input_token: str) -> str:
    """Decode padded JWT token

    Args:
        input_token (str): Padded JWT token

    Returns:
        str: header and payload in JSON format
    """
    input_token = input_token.translate(str.maketrans('-_', '+/'))
    header, payload, secret = input_token.split('.')

    jwt_header = pad_jwt(header)
    jwt_payload = pad_jwt(payload)

    header = base64.urlsafe_b64decode(jwt_header).decode()
    payload = base64.urlsafe_b64decode(jwt_payload).decode()

    header = json.loads(header)
    payload = json.loads(payload)

    return header, payload

def calculate_exp_time(payload: str) -> int:
    """Calculate token expiration time in seconds

    Args:
        payload (str): token

    Returns:
        int: expiration time in seconds
    """
    exp_time = payload.get('exp', None)
    if exp_time is not None:
        return exp_time - int(time.time())
    return None

# -----------------------------------------------------------------------------
# TODO: renew token via IBM Cloud IAM
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Generate JWT token using the IAM token
# -----------------------------------------------------------------------------
def generate_jwt_token(api_key: str) -> str:
    IAM_URL = os.getenv("IAM_URL")
    response = requests.post(IAM_URL, headers={"Content-Type": "application/x-www-form-urlencoded"}, data=f"grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey={api_key}")
    return response.json()["access_token"]

# -----------------------------------------------------------------------------
# Check if token renewal needed
# -----------------------------------------------------------------------------
def token_renewal_needed(payload: str) -> int:
    """Check if token renewal is needed

    Args:
        payload (str): _description_

    Returns:
        int: _description_
    """
    exp_time = calculate_exp_time(payload)
    if exp_time is not None:
        print("Exp time (unix time):", exp_time)
        if exp_time > 60:
            return False
        else:
            return True
    else:
        print("Exp time not found in payload.")
        return True


# -----------------------------------------------------------------------------
# Renew token via IBM Cloud IAM
# -----------------------------------------------------------------------------
def renew_token(iam_token: str) -> str:
    jwt_token = generate_jwt_token(iam_token)
    #log.debug(f"{jwt_token}")
    _, payload = jwt_decode(jwt_token)

    while token_renewal_needed(payload):
        jwt_token = generate_jwt_token(iam_token)
        _, payload = jwt_decode(jwt_token)

    return jwt_token

# -----------------------------------------------------------------------------
# TODO: Call REST API
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Parse arguments
# -----------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description='Call watsonx on IBM Cloud using IAM / JWT')
    parser.add_argument('--iam-token', help='IBM Cloud IAM Token used to generate the JWT token', required=False)
    parser.add_argument('--exp', action='store_true', help='Return expiration time in seconds')
    parser.add_argument('--decoded', action='store_true', help='Return decoded token', default=True)
    parser.add_argument('--header', action='store_true', help='Return header')
    parser.add_argument('--payload', action='store_true', help='Return payload')

    args = parser.parse_args()

    # Read the IAM token from the environment variables
    api_key = os.environ.get("API_KEY")

    if not api_key:
        raise ValueError("API_KEY environment variable not found")

    # Renew the JWT token if needed
    new_jwt_tokeninp = renew_token(api_key)

    header, payload = jwt_decode(new_jwt_tokeninp)

    if args.exp:
        exp_time = calculate_exp_time(payload)
        if exp_time is not None:
            print("Exp time (unix time):", exp_time)
        else:
            print("Exp time not found in payload.")
    elif args.decoded:
        print("Decoded Token:")
        print("Header:", header)
        print("Payload:", payload)
    elif args.header:
        print("Header:", header)
    elif args.payload:
        print("Payload:", payload)
    else:
        print("Please provide an option to display the desired information.")


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    main()
