=========
Gitserver
=========
---------------------------------------------------------------------
A simple Flask-based webserver for querying git commit parent lineage
---------------------------------------------------------------------

This is a very simple-minded service to advertise git history through HTTP, originally written for [teuthology](http://github.com/ceph/teuthology) to use in its scheduling command ``teuthology-suite``.

============
Requirements
============

Python 2.7 and [flask](http://flask.pocoo.org/).

You probably also want to think about some sort of WSGI deployment methodology (Apache with mod_wsgi, nginx with gunicorn, nginx native, you pick the method).  


==========
Deployment
==========

For testing, you can simply execute the gitserver.py file, and it will start a server on localhost:5000.  You probably don't want to use that in production, however.

Here's a very simple .wsgi file for [mod_wsgi](http://flask.pocoo.org/docs/0.11/deploying/mod_wsgi/)::: 

        import sys
        sys.path.insert(0, <path holding gitserver.py>)
        from gitserver import app as application

You'll want to verify/update REPOBASE near the top of the gitserver.py file.  You'll also want to populate REPOBASE with git clone --mirror (i.e.  you want bare repos that also track the remote branches). 

See [flask](http://flask.pocoo.org/) for other [deployment](http://flask.pocoo.org/docs/0.11/deploying) options and details.

====
URLs
====

Requests are GETs, and respond with JSON.

* /               
       Return:
               * 'repos' is a list of available repo names

* <repo>/refresh/
        Issue ``git fetch -p`` on <repo>.  Returns 500 if error.

        Return:
                * 'out': stdout of fetch 
                * 'err': stderr of fetch

* <repo>/history/?committish=C&count=N

        Issue ``git rev-list --first-parent`` starting from C (a branch,
        tag, or sha1).

        Query params:
                * committish (optional): branch, tag, or sha1;
                  default 'master'
                * count (optional): number of sha1s to return;
                  default 10

        Return:
                * 'sha1s': list of N parent commit ids
                * 'err': stderr from rev-list
                * 'committish': copy of input

* <repo>/sha1/?sha1=sha1&shortmsg
       
        Validate a (possibly-short) sha1; return full sha1.
        If 'shortmsg' is present, return short commit message as well

        Query params:
                * sha1 (required): possibly short sha1 to validate/expand
                * shortmsg (optional): include if return should include short commit msg

        Return:
                * 'sha1': full sha1
                * 'shortmsg': if requested, ``rev-list --pretty=oneline``
                * 'err': stderr from ``rev-list``

* <repo>/contains/?sha1=sha1
        
        Find branches and/or tags that contain sha1

        Query params:
                * sha1 (required) Possibly short sha1 to search for

        Return:
                * 'branches': list of branches that contain sha1
                * 'tags': list of tags that contain sha1
                * 'sha1': expanded/validated input parameter
                * 'err': Combined stderr from ``git branch/git tag --contains``

