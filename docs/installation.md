# Installation
- [Install from Github](#install-from-github)
- [Start `sandpiper` PyWPS service](#start-sandpiper-pywps-service)
- [Run `sandpiper` as Docker container](#run-sandpiper-as-docker-container)
- [Use Ansible to deploy `sandpiper` on your System](#use-ansible-to-deploy-sandpiper-on-your-system)

## Install from GitHub

Check out code from the sandpiper GitHub repo and start the installation:
```
$ git clone https://github.com/pacificclimate/sandpiper.git
$ cd sandpiper
```

Create Python environment named `venv`:
```
$ python3 -m venv venv
$ source venv/bin/activate
```

Install requirements:
```
(venv)$ pip install -r requirements.txt
```

Install sandpiper app:
```
(venv)$ pip install -e .
# OR
$ make install
```

For development you can use this command:
```
$ pip install -e .[dev]
# OR
$ make develop
```

## Start `sandpiper` PyWPS service
After successful installation you can start the service using the `sandpiper` command-line.

```
(venv)$ sandpiper --help # show help
(venv)$ sandpiper start  # start service with default configuration

# OR

(venv)$ sandpiper start --daemon # start service as daemon
loading configuration
forked process id: 42
```
The deployed WPS service is by default available on:

http://localhost:5000/wps?service=WPS&version=1.0.0&request=GetCapabilities.

NOTE:: Remember the process ID (PID) so you can stop the service with `kill PID`.

You can find which process uses a given port using the following command (here for port `5000`):

```
$ netstat -nlp | grep :5000
```

Check the log files for errors:
```
$ tail -f  pywps.log
```
... or do it the lazy way

You can also use the `Makefile` to start and stop the service:
```
$ make start
$ make status
$ tail -f pywps.log
$ make stop
```

## Run `sandpiper` as Docker container
You can also run `sandpiper` as a Docker container.
```
$ docker-compose build
$ docker-compose up
```

`sandpiper` will be available on port `8101`.

## Use Ansible to deploy `sandpiper` on your System
Use the [Ansible playbook](http://ansible-wps-playbook.readthedocs.io/en/latest/index.html) for PyWPS to deploy `sandpiper` on your system.
