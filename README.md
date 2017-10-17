Simple blockchain based on github/dvf's [post](https://hackernoon.com/learn-blockchains-by-building-one-117428612f46)

### Setup (using pipenv)
pip install pipenv
pipenv --python 3.6
pipenv install Flask==0.12.2 requests==2.18.4

### Testing
pipenv run python server.py 1111
pipenv run python server.py 2222
sh test.sh 1111 2222

### Running
pipenv run python server.py
