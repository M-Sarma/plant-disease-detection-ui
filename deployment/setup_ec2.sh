#!/bin/bash
sudo apt-get update
sudo apt-get install -y docker.io docker-compose nginx
sudo systemctl start docker
sudo systemctl enable docker
sudo docker-compose up -d