#!/bin/bash

./run_display.sh

source /opt/openfoam7/etc/bashrc

python3 manage.py runserver 0.0.0.0:8000