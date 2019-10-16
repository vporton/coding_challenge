# Coding Challenge App

A Django app for a solution to a:
[coding challenge](https://drive.google.com/file/d/0B6y8e6-LG84naElFcTlkcHQ1bU1qUkM1Y2VhbXpMdnE4ZjJz/view).

## Install:

Download from GitHub and chdir into the project
directory.

You can use a virtual environment created by virtualenv:
```
virtualenv -p python3 ~/.virtualenv/coding_challenge-porton
source ~/.virtualenv/coding_challenge-porton/bin/activate
```

Or just pip install from the requirements file
``` 
pip install -r requirements.txt
```

You must create the file `local_settings.py` in the
project folder containing your GitHub API token like:
```python
GITHUB_API_TOKEN = 'XXX'
```

You can create this token using "Developer settings" /
"Personal access tokens" in GitHub settings. It must
have `public_repo` permission.

You can also configure maxiumum number of threads
separately for the main API requests and for
BitBucket watchers info API requests.

## Running the code

First you need to run once to create the DB (by default it is
SQLite):
```
python manage.py migrate
```

Probably all Django database drivers are supported.

Moreover, probably it will work without creating the DB as it is
not used in my code, but for greater reliability I advise to
create the DB, because the Django workflow requires it. You could
reconfigure it to hold the SQLite file in /tmp/.

### Spin up the service

Then you can start the project in debug mode by
```
# start up local server
python manage.py runserver 
```

You can do unittests:
```
python manage.py test 
```

### Making Requests

```
curl -i "http://127.0.0.1:8000/health-check?url=https://github.com/mailchimp&url=https://bitucket.org/mailchimp"
```
(You can provide any number of GitHub and BitButcket URLs in the request.)

Alternatively you can enter one URL at a line in the
form at `http://127.0.0.1:8000/from-git/test`.

The format of the reponse can be viewed with this
`http://127.0.0.1:8000/from-git/test`.

## Implementation and performance notes

It was tested only with Python 3.7 instead of Python 3.6 because
the task was done in hurry (before traveling to Africa) and I
had not enough time to install 3.6. Almost surely will work with
3.6, too.

It is used Django and Django REST Framework (DRF).

It can be easily done without DRF but DRF enhances debugging
and maintainability, especially as the project would grow more
complex.

DRF takes very little CPU resources and more importantly some
memory and startup time.

Requests are done through GET to conform to REST. (It should be GET
because does not change the server state.) If the number
of organizations is big, the GET request would have a very long
URL and not work on very old browsers. It is very easy to change
the code to use POST (or even support both GET and POST).  

Multithreading with `ThreadPool` is used to reduce
network transfer time from the source servers.

It is rather near to be most efficient
possible for a DRF project (however see code comments). Memory usage can be reduced by eliminating
`python-graphql-client` dependency,

In the output the keywords are sorted to make requests
deterministic. This may also improve caching, what is however
currently unimportant because our responses are small.

The main Django app of the project is `from_git`.

I use a global `ThreadPool` variable rather than creating it for every request, because this allows to lower server load under normal circumstances, but we have no way to interrupt requests in the case of an error. TODO: Cancel loading BitBucket watchers in the case of an error.

## Other notes

I would make this repository private but in an non-understandable
reason GitHub does not allow private forks of public repositories.
I noticed other users made public forks too, so I am not the only
"insider".

In the case if a repository is missing, we return it in the list
of missing repositories (check if it is empty to ensure not errors)
and ignore this repo in the statistics.

Followers and topics are missing on BitBucket, so I return zero for them.

If GitHub or BitBucket does not respond OK at least once, we
return an error response, because otherwise the statistics would
be wrong. Should have to retry if the possible number of queried
repos would be big, but this is not implemented (TODO).

Data is returned in `"data"` subobject to be differentiated from
errors.

I used GraphQL GitHub API (v4) instead of REST API (v4) to reduce the transfered
data amount.

TODO: Check if a profile in request provided more than once. 

TODO: handling gh/bb errors.

We have separate thread pools for GitHub and BitBucket
because: 1. One could have for example 1 thread on
BitBucket and 1 thread on GitHub on a low end system
but even in this case we need to run them in parallel.
Also so it is easier to implement because we use
different functions to peform downloading for GH and BB.

We use a separate thread pool for downloading watcher counters. It would be better to have a common thread pool, but that's not easy to implement, for example because of deadlocks.

The numbers of threads allocated are configurable in `local_settings.py`, as explained in `settings.py`.

I do not do HTTP caching, because it was not asked in the project spec and it can be easily and
automatically be done with a proxy server like Squid.
Moreover, using Squid would easily allow a persistent
cache. So I avoid work duplication and complication
of the code. We could also add caching if our
calculated results, but that seems not very imporant,
because most of the time is spend in network requests,
and that caching of calculated results would make
the code more complex reducing maintainability.

Ideally we should add ETag and last mod time to our
responses, but that's would be not easy and error-prone.

TODO: logging