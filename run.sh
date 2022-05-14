#!/bin/bash

cd "$(dirname "$0")"
. .venv/bin/activate
.venv/bin/python -m pip install --upgrade pip
pip3 install -e .

cd ct_bot

python3 main.py
echo "The program has been safely terminated."