#!/bin/bash

# Quit the Flask server
curl http://fencewithfriends.online/server/quit

# Pull the latest changes from Git
git pull

# Reopen the Flask server
nohup python3 main.py &