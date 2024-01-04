#!/bin/bash

for i in *.py
do
    if [ "$i" != "getpass.py" ] && [ "$i" != "docx2.py" ]
    then
	python3 "$i"
    fi
done > outputs.txt
