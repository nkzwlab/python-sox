#!/bin/sh

# create nodes
python create_genova_santander.py

# generate genova meta post commands
python genova_meta_post.py

# generate santande meta post commands
python santander_meta_post.py
