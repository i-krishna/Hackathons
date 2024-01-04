#!/bin/bash

jupyter nbconvert --to python *.ipynb
for i in *.py
do
    if [ "$i" != "getpass.py" ]
    then
	# Print the input and generated output. The Generated code doesn't
	# print anything.
	sed -e '/^prompt.generate/s/.*/print(prompt_input, &)/' "$i" > "$i".NEW
	mv "$i".NEW "$i"
    fi
done

