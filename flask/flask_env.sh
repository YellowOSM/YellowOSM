#!/bin/bash

virtualenv -p /usr/bin/python3.6 ./env || exit -1

. ./env/bin/activate
pip3 install -r requirements.txt

