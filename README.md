# Coding Challenge App

A Django app for a solution to a coding challenge.

## Install:

TODO

You can use a virtual environment created by virtualenv:
```
conda env create -f environment.yml
source activate user-profiles
```

Or just pip install from the requirements file
``` 
pip install -r requirements.txt
```

## Running the code

TODO

### Spin up the service

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

## Other notes

I would make this repository private but in an non-understandable
reason GitHub does not allow private forks of public repositories.
I noticed other users made public forks too, so I am not the only
"insider".
