#!/bin/bash

# Assumed to be in PATH in the venv/bin folder
UWSGICMD=uwsgi
rm -fv uwsgi.pid ws.log
$UWSGICMD \
  --http 0.0.0.0:9550 \
  --wsgi-file covidqa_rest.py \
  --callable app \
  --pidfile uwsgi.pid \
  --master --processes 1 \
  --harakiri 100 \
  --socket-timeout 100 \
  --min-worker-lifetime 100 \
  --http-timeout 200 \
  --buffer-size 32768 \
  --post-buffering 32768 \
  --logto ws.log &
echo "Server started."
