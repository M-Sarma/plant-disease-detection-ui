#!/bin/bash

# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip -y

# Install Streamlit dependencies
pip install -r /path/to/plant_disease_detection/requirements.txt

# Start Streamlit app
nohup streamlit run /path/to/plant_disease_detection/app/main.py --server.port 8080 --server.address 0.0.0.0 &
