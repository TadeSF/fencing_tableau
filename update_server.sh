#!/bin/bash

echo "Deploying latest changes..."

# Wait 1 second
sleep 1

# Stop Gunicorn
echo "Stopping Gunicorn..."
sudo systemctl stop fencing_tableau

# Change to app directory
echo "Changing to app directory..."
cd /home/pi/fencing_tableau

# Wait 1 second
sleep 1

# Pull latest changes from Git
echo "Pulling latest changes from Git..."
sudo git pull

# echo "Building documentation..."
# sphinx-build -b html docs docs/build

# Wait 5 second
sleep 5

# Start Gunicorn
echo "Starting Gunicorn..."
sudo systemctl start fencing_tableau

# Wait 5 second
sleep 5

# Restart Nginx
echo "Restarting Nginx..."
sudo systemctl restart nginx

echo "Deployment complete."
