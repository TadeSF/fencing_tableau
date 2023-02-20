#!/bin/bash

echo "Deploying latest changes..."

# Wait 1 second
sleep 1

# Stop Gunicorn
echo "Stopping Gunicorn..."
sudo systemctl stop gunicorn

# Change to app directory
echo "Changing to app directory..."
cd /home/pi/fencing_tableau

# Pull latest changes from Git
echo "Pulling latest changes from Git..."
sudo git pull

# Start Gunicorn
echo "Starting Gunicorn..."
sudo systemctl start gunicorn

# Restart Nginx
echo "Restarting Nginx..."
sudo systemctl restart nginx

echo "Deployment complete."