#!/bin/bash
pip install poetry 
poetry init -n

while read line; 
    do poetry add "$line" 
done < requirements.txt