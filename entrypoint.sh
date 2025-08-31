#!/bin/sh

# Start Gunicorn
# The 'exec' command is important, it replaces the shell process with the Gunicorn process
exec gunicorn --workers 4 --bind 0.0.0.0:3000 --preload app:app