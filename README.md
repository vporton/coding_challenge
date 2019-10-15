# Coding Challenge App

A Django app for a solution to a:
[coding challenge](https://drive.google.com/file/d/0B6y8e6-LG84naElFcTlkcHQ1bU1qUkM1Y2VhbXpMdnE4ZjJz/view).

## Install:

TODO

You can use a virtual environment created by virtualenv:
```
virtualenv -p python3 ~/.virtualenv/coding_challenge-porton
source ~/.virtualenv/coding_challenge-porton/bin/activate
```

Or just pip install from the requirements file
``` 
pip install -r requirements.txt
```

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

TODO: local_settings.py

### Spin up the service

Then you can start the project in debug mode by
```
# start up local server
python manage.py runserver 
```

### Making Requests

TODO

```
curl -i "http://127.0.0.1:8000/health-check"
```

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

My code ideally should be multithreaded or asynchronous to handle
several GH/BB requests in parallel, but that would take too much
time to implement. Otherwise it is near to be most efficient
possible for a DRF project (however see code comments). It could be
improved a little by "summing" data from several requests at once
rather than by pairs but that improvement would be minor. (It is
minor, I note it only because I was specifically asked about
efficiency.)

In the output the keywords are sorted to make requests
deterministic. This may also improve caching, what is however
currently unimportant because our responses are small.

The main Django app of the project is from_git,

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

Data is returned in "data" subobject to be differentiated from
errors.

Should have used GraphQL GitHub API (v4) to reduce the transfered
data amount, but sadly I do not yet know GraphQL and this is a
quick project. If I'd worked on a serious project, I'd first
study GraphQL.

TODO: ETag and date

TODO: Check if a profile in request provided more than once. 

TODO: github3.py and otherwise caching.

TODO: handling gh/bb errors.