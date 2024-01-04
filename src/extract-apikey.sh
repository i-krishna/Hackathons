#!/bin/sh

jq ".apikey" < $1 | tr -d '"'
