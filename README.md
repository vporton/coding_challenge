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

Requests are done through GET to conform to REST. If the number
of organizations is big, the GET request would have a very long
URL and not work on very old browsers. It is very easy to change
the code to use POST (or even support both GET and POST).  

My code ideally should be multithreaded or asynchronous to handle
several GH/BB requests in parallel, but that would take too much
time to implement. Otherwise it is near to be most efficient
possible for a DRF project. It could be improved a little by
"summing" data from several requests at once rather than by pairs
but that improvement would be minor.

In the output the keywords are sorted to make requests
deterministic. This may also improve caching, what is however
currently unimportant because our responses are small.

## Other notes

I would make this repository private but in an non-understandable
reason GitHub does not allow private forks of public repositories.
I noticed other users made public forks too, so I am not the only
"insider".
