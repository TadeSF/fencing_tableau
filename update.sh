#!/bin/bash

# Quit the Flask server
sudo killall python

# Pull the latest changes from Git
git pull

# Reopen the Flask server
sudo nohup python main.py &