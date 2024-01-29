# acapycontroller
Aca-Py Agent Controller 

## Introduction
This repository hosts the ACA-Py Controller, a critical component for managing and controlling the Hyperledger Aries Cloud Agent - Python (ACA-Py). It provides the necessary tools and interfaces to interact with the ACA-Py, facilitating the creation and management of decentralized identity solutions.

## Features
- Interface for interacting with deployed Agents 
- Management of connection invitations and responses.
- Handling of credential issuance and verification for Multitenant Holder

## Instructions to Run project 

- Clone Von-Network repository: https://github.com/bcgov/von-network
run 
```bash
$ ./manage build
``` 
and then 
```bash
$ ./manage up
``` 
in the root folder 
You can see the network is running on localhost:9000

- Clone Tails-Server if you would like to support revocation: https://github.com/bcgov/indy-tails-server and then follow the instructions to run it. You can see the server is running on localhost:6543

- Run docker agents from docker folder in this repo, or separately. 
```bash 
$ docker compose up 
``` 
### Running the Controller

1. Setup python virtual environment & activate it
```bash 
$ python3 -m venv venv
```
```bash
$ source venv/bin/activate
``` 
2. Install poetry & add it path
```bash
$ curl -sSL https://install.python-poetry.org | python3 -
```
Optional (instead of adding to path)
```bash
$ /Users/<profile>/.local/bin/poetry install
``` 
==> or add poetry to path and do poetry install (don't do requirements.txt).

3. Run any necessary django commands: 

```bash 
$ python manage.py makemigrations
```

```bash 
$ python manage.py migrate
```

```bash 
$ python manage.py createsuperuser
```

etc. 


4. Run the application, it will run on port 8000
```bash 
$ $python manage.py runserver
```

## License
This project is licensed under the Apache 2.0 License.