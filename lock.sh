#!/bin/bash
poetry lock
poetry export -f requirements.txt > ./requirements.txt

