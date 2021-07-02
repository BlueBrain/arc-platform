# Arc v2

## Requirements

* Docker

All the runtime environment is based on the _docker-compose_ file.
It contains a _postgres_ container and the python runtime.

The containers `/code` directory is the project home. This allows the developers to see
 their changes in live.

## Basic commands

### Run in development mode

To run the project simply run

```
$ docker-compose up --build
```

in the project root directory.

The API is available on `localhost:8000`

Note that on the first launch
the database is empty so we have to create the tables. To do so we use Django's CLI:

```
$ docker-compose run web python manage.py migrate
```

### Maintenance on the container

1. Connect to the Django docker container: `docker-compose exec web bash`
1. Apply database migrations: `python manage.py migrate`
1. Create a superuser to connect to the administration interface: `python manage.py createsuperuser`
1. Optionally populate the database for development by running `python manage.py runscript seed`
1. You can now connect to the administration interface at `/admin` and to the platform

### Seed & administration srcipts

Scripts are located in the `scripts` folder. They are run with the
[runscript](https://django-extensions.readthedocs.io/en/latest/runscript.html)
library. An utility shell script is available in `bin/run` to avoid the verbose
calling of runscript. It is added to the `PATH` **of the image**. You can use it
with

```
run <script_name> <script args>
```

E.g.

```
run seed_all
```

### Populate the database

You can run `python manage.py runscript seed` in the docker container to create a few entries in the database.

### Run the tests

```
$ docker-compose run web ./manage.py test
```

### Adding a python package

To add a pypi package simply add it to `requirements.txt` and run
```
docker-compose build web
```
Don'tforget to specify the exact version of the package to prevent changes in the
library from breaking your code !

### JS & SCSS assets packaging

For convenience a docker service watching and compiling assets source files
(in `arcv2_platform/static/src`) is configured for development (in `docker-compose.override.yml`).
To add an npm package, you can edit the `package.json` file and rebuild the watcher service
with
```
docker-compose build web-parcel
```
To extract the updated `package-lock.json` to commit it you can run
```
docker cp $(docker-compose ps -q web-parcel):/code/package-lock.json package-lock.json
```

### Linter

Run the linter:

```
$ docker-compose run web flake8
```

Fix (some) of your bad style...

```
$ docker-compose run web autopep8 -iraa .
```

### Environments

The web container runs with `SERVER_ENV=local` by default.

You can change the environment using

```
$ docker-compose up -e SERVER_ENV=dev --build
```

Which is probably not a good idea,
but you might want to override a specific setting using env vars

```
$ docker-compose up -e APP_LOGLEVELS_APP=INFO --build
```

## Configuration

Environments other then `local` require additional configuration to be set via environment variables.

This is a list of env vars a deployment might require:
* global:
    * SERVER_ENV
    * HTTP_PROXY
    * HTTPS_PROXY
    * APP_DEPLOYMENT_BASE_URL
* email:
    * EMAIL_HOST
    * EMAIL_PORT
    * EMAIL_USE_SSL
    * EMAIL_HOST_USER
    * EMAIL_HOST_PASSWORD
    * DEFAULT_FROM_EMAIL
    * APP_EMAIL_DEFAULT_SUBJECT_PREFIX
* db:
    * APP_DB_HOST
    * APP_DB_PORT
    * APP_DB_NAME
    * APP_DB_USER
    * APP_DB_PASSWORD
* monitoring:
    * APP_SENTRY_DSN
* other:
    * APP_REQUEST_EXPIRATION_HOLD_DAYS

See [config.py](arcv2_platform/config/config.py) for more details.

## CI - Dev

* Open a pull request on a branch

=> Trigger test on CircleCI

* Merge pull request or push on `master` branch

=> Build, test, and deploy on `arcv2-dev.appti.ch`

## CI - Release

To release a new version on _uat_ / _prd_ :

```
$ git checkout master
$ git pull
$ docker-compose run web fullrelease
<answer the questions>
$ git push origin master
$ git push origin <the new tag>
```

Pushing a new tag on github triggers the _tagged workflow_ on CircleCI. This will deploy this
a new version on `arcv2-uat.appti.ch`. Then, an _hold_ button is available on _CircleCI_
which triggers the deployment on `arcv2-prd.appti.ch`.

Therefore, the above commands will result in the following:
* Update minor version number in setup.py
* git commit that change
* git tag the repo with the new version number
* git push the tag and the develop branch
* New version deployed on `arcv2-dev.appti.ch`
* New version deployed on `arcv2-uat.appti.ch`
* _Hold_ button available on CircleCI to deploy on _prd_ after a reasonable testing phase on _uat_.

## Logger level recommendations

- **CRITICAL** - The system is about to stop. Log the reason. After that the process should end with a non zero exit code
- **ERROR** - Something went wrong. Default level for all caught / rejected Errors front the main event loop. Also to be used for errors during to third party components calls (remote service, db...)
- **WARNING** - Need to catch the attention of a DevOp. But the system is able to deal with that. (e.g. inconsistencies in the db)
- **INFO** - What is happening in the system. Frequency of message is suitable for production.
- **DEBUG** - What is happening in the system. Help dev to follow the flow of the code, and to understand the cases. Useful for development, but disabled in production to avoid to flood the log.

### Create a pull request (PR) process

1. commit new changes
2. if linter in place : ```docker-compose run web autopep8 -iraa .``` before push
3. add in previews commit instead of create a new commit :
   1. ```git add -u```
   2. ```git commit --amend```
4. push to repository : ```git push origin <branchName>```

(!) branch must be ready to merge, pull master in the branch. ```git pull origin master```

(!) As Reviewer, you have the responsibility to check if the developer respects the guidelines


## IDE - PyCharm

- Use venv for your own good
- Ensure you enable .editorconfig support

## Custom scripts

To run python scripts within the Django context we use the `runscript` library from `django-extensions`.
To add a new script simply create a file named after the command (e.g. `example.py`) in the `scripts` folder. The file must contain a function called `run` which can then be executed by running

```
python manage.py runscript example
```

in the `web` container (accessible with `docker-compose exec web bash`).

## Funding & Acknowledgment
 
The development of this software was supported by funding to the Blue Brain Project,
a research center of the École polytechnique fédérale de Lausanne (EPFL), from the
Swiss government’s ETH Board of the Swiss Federal Institutes of Technology.
