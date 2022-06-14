#!/usr/bin/python

'''
Provide simple git history queries for use in
deciding about CI build status
'''

from flask import Flask, request, json
app = Flask(__name__)

import os
import subprocess
import logging

app.logger.addHandler(logging.StreamHandler())
app.logger.setLevel(logging.WARN)

# should contain *.git bare repos
REPOBASE = "/home/cephgit/gitserver/git"
JSONHDR = {"content-type": "application/json"}

def run_command(cmd, repodir):
    ''' subprocess helper '''
    proc = subprocess.Popen(
        args=cmd.split(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=repodir
    )

    out, err = proc.communicate()
    return out, err, proc.returncode


@app.route('/')
def root():
    ''' /: List repos '''
    retval = list()
    for p in os.listdir(REPOBASE):
        if (
            os.path.isdir(os.path.join(REPOBASE, p, '.git')) or
            os.path.isfile(os.path.join(REPOBASE, p, 'config'))
        ):
            retval.append(p.replace('.git', ''))

    return json.jsonify(dict(repos=retval))


@app.route('/<repo>/refresh/')
def refresh(repo):
    ''' /<repo>/refresh/: git fetch -p the repo '''
    cmd = 'git fetch -p'
    repodir = '/'.join((REPOBASE, repo))
    out, err, rc = run_command(cmd, repodir)
    if rc:
        return err + '\nreturn code: %d' % rc, 500, {'content-type': 'text/plain'}
    return json.jsonify(dict(out=out, err=err))


@app.route('/<repo>/history/')
def history(repo):
    '''
    /<repo>/history/: Return <count> (default 10) most-recent commit ids from
    <committish> (default: main)
    '''
    committish = request.args.get('committish', 'main')
    count = request.args.get('count', 10)
    cmd = 'git rev-list --first-parent --max-count %s %s' % (count, committish)
    repodir = '/'.join((REPOBASE, repo))
    out, err, rc = run_command(cmd, repodir)
    d = dict(sha1s=list(out.split()), err=err, committish=committish)
    return json.jsonify(d)


def validate_sha1(repo, sha1):
    ''' validate sha1 against repo; return expanded sha1 or None'''
    cmd = 'git rev-list --first-parent --max-count 1 %s' % sha1
    repodir = '/'.join((REPOBASE, repo))
    out, err, rc = run_command(cmd, repodir)
    sha1 = None
    if out:
        sha1 = out.split()[0]
    return sha1


@app.route('/<repo>/sha1/')
def sha1(repo):
    '''
    /<repo>/sha1/: Validate a (maybe-short) sha1; return full sha1
     optional arg 'shortmsg' returns short commit msg as well
    '''
    cmd = 'git rev-list --first-parent'
    sha1 = request.args.get('sha1', None)
    if not sha1:
        return 'sha1 required', 400
    shortmsg = request.args.get('shortmsg', None)
    extra = ''
    if shortmsg is not None:
        extra = '--pretty=oneline'
    cmd = ' '.join((cmd, '--max-count 1 %s %s' % (extra, sha1)))
    repodir = '/'.join((REPOBASE, repo))
    out, err, rc = run_command(cmd, repodir)
    sha1 = msg = None
    if out:
        sha1 = out.split()[0]
        if shortmsg is not None:
            msg = ' '.join(out.split()[1:])
    d = dict(sha1=sha1, err=err, shortmsg=msg)
    return json.jsonify(d)


@app.route('/<repo>/contains/')
def contains(repo):
    '''
    /<repo>/contains: Return lists of branches and/or tags containing <sha1>
    Also, expand sha1 to full 40-char and return
    If any branches are "local -> remote", return as one list item
    '''
    sha1 = request.args.get('sha1', None)
    if not sha1:
        return 'sha1 required', 400
    repodir = '/'.join((REPOBASE, repo))
    cmd = 'git branch -a --color=never --contains %s' % sha1
    branchout, brancherr, rc = run_command(cmd, repodir)
    cmd = 'git tag --contains %s' % sha1
    tagout, tagerr, rc = run_command(cmd, repodir)
    err = ''
    if brancherr or tagerr:
        err = 'branch --contains errors:\n' + brancherr
        err += 'tag --contains errors:\n' + tagerr

    branches = branchout.replace('* ', '').strip().split()
    while '->' in branches:
        index = branches.index('->')
        branches[index - 1] = ' '.join(branches[index - 1:index + 2])
        del branches[index:index + 2]
    d = dict(
        branches=branches,
        tags=tagout.strip().split(),
        sha1=validate_sha1(repo, sha1),
        err=err
    )
    return json.jsonify(d)


if __name__ == '__main__':
    app.run(debug=True)
