#!/bin/bash
set -ex
DEFAULT_REPOS=(
  "https://github.com/ceph/autobuild-ceph"
  "https://github.com/ceph/ceph"
  "https://github.com/ceph/ceph-ansible"
  "https://github.com/ceph/ceph-build"
  "https://github.com/ceph/ceph-ci"
  "https://github.com/ceph/ceph-client"
  "https://github.com/ceph/ceph-cm-ansible"
  "https://github.com/ceph/ceph-cookbooks"
  "https://github.com/ceph/ceph-deploy"
  "https://github.com/ceph/ceph-object-corpus"
  "https://github.com/ceph/cephmetrics"
  "https://github.com/ceph/googletest"
  "https://github.com/ceph/jerasure"
  "https://github.com/ceph/keys"
  "git://git.kernel.org/pub/scm/linux/kernel/git/firmware/linux-firmware.git"
  "https://github.com/ceph/qemu-iotests"
  "https://github.com/ceph/radosgw-agent"
  "https://github.com/ceph/ragweed"
  "https://github.com/ceph/remoto"
  "https://github.com/ceph/rocksdb"
  "https://github.com/ceph/s3-tests"
  "git://git.kernel.org/pub/scm/fs/xfs/xfstests-dev.git"
  "git://git.kernel.org/pub/scm/fs/xfs/xfsprogs-dev.git"
  "https://github.com/ceph/teuthology"
)
REPOS=${REPOS:-${DEFAULT_REPOS[@]}}
REPO_AGE=${REPO_AGE:-"1 month"}
cd /git
for repo in $REPOS; do
  git clone --mirror --shallow-since "$REPO_AGE" --shallow-submodules --no-single-branch $repo || true
done
cd /opt/githelper
source ./venv/bin/activate
exec tini -- gunicorn --workers=10 --bind 0.0.0.0:8080 githelper:app
