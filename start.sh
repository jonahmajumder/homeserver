#!/bin/bash

# run this from ssh (and detach, but show window) session by:
# 1. export DISPLAY=:0
# 2. lxterminal -e $HOME/code/homeserver/start.sh &

source $HOME/.virtualenvs/flask/bin/activate

cd $HOME/code/homeserver

echo "Starting flask server -- production version"
gunicorn -b 0.0.0.0:5000 server:app
