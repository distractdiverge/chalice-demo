# SBA Etran v2
This repository contains the code required to parse the JSON requests/responses sent to 'DataManagement' from the 'PPBL Services' team.

These files are then parsed and saved to ProdSwiftCore MSSQL database.


## Requirements
  * Local development makes use of a virtual environment for python, see [below](#Python_VirtualEnv) for steps on how to set it up.
  * Note: to make full use of 'pyre-check', make sure to install watchman (file watcher daemon)


## Actions

### Test
 * Just execute the tests
```sh
make test
```

 * Execute Tests & Coverage (simple report)
```sh
make test-cov-report
```

 * Execute the tests & produce HTML coverage report
```sh
make test-cov-html
```

## Deployment & AWS
This project makes use of [AWS Chalice](https://aws.github.io/chalice/index.html) to eliminate a lot of the boilerplate for creating lambdas.

TODO: Describe new Build/Package/Deploy process --- we have to reduce the package size before deploy,
and the only way to do that is to deploy via CloudFormation in a 3 step process.
```sh
make package-chalice # Package the Python Code & ALL libraries
make update-package # Remove Botocore & others (reduce size)
make package-cloudformation # Create the CloudFormation Package & Upload to S3
make deploy # Deploy to AWS
```
OR, just run the chained commands:
```sh
make package
make deploy
```


## Python VirtualEnv
The following tools are used to manage python versions & virtual environments. Make sure these are installed.
 * [pyenv](https://github.com/pyenv/pyenv) -- Used to Manage Python Versions
 * [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv) -- Connects Pyenv & traditional virtualenvs
 * FreeTDS - Used by 'pymssql', see [setup](https://docs.microsoft.com/en-us/sql/connect/python/pymssql/step-1-configure-development-environment-for-pymssql-python-development?view=sql-server-ver15)

### Create VirtualEnv
This only needs to be done once
```sh
pyenv virtualenv 3.7.9 ppp-sba_etran_v2
```

### Activate VirtualEnv
```sh
pyenv activate ppp-sba_etran_v2
```

### Using The VirtualEnv
Typical tasks would be:
 * Install dependencies via pip
  ```sh
  pyenv exec pip install <something>
  ```
 * Execute python scripts
  ```sh
  pyenv exec python ./some-file.py
  ```
 * Execute other installed binaries (that were installed via pip)
  ```sh
  pyenv exec sqlacodegen
  ```