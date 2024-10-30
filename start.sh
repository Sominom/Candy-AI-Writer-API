#!/bin/bash
source venv/bin/activate
nohup python -u -m App.main > ./server.log 2>&1 &  
deactivate
echo "API Started"
