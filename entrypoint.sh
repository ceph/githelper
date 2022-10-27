#!/bin/bash
set -ex
REPOS=${REPOS:-"https://github.com/ceph/ceph https://github.com/ceph/teuthology"}
REPO_AGE=${REPO_AGE:-"1 month"}
cd /git
for repo in $REPOS; do
  git clone --mirror --shallow-since "$REPO_AGE" --shallow-submodules --no-single-branch $repo || true
done
cd /opt/gitserver
source ./venv/bin/activate
exec tini -- gunicorn --workers=10 --bind 0.0.0.0:8080 gitserver:app
