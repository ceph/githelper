#!/bin/bash
set -ex
cd /opt/githelper
source ./venv/bin/activate
exec tini -- gunicorn --workers=10 --bind 0.0.0.0:8080 githelper:app
