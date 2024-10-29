#!/bin/bash
source venv/bin/activate
nohup python -u -m App.main > ./server.log 2>&1 &  
echo $! > ./.pid
deactivate
echo "API Started"
