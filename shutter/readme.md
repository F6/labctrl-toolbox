# Shutter Toolbox

This toolbox is part of the labctrl-toolbox project, which is a submodule of labctrl project.

## Packages

- [`generic`](#generic): FastAPI server and hardware API for a generic shutter controlled via serial / USB serial interface.
- [`api`](#api): Reference API implementation in different languages.
- [`tests`](#tests): All unit tests and integration tests.

## generic

This package includes a template project that provides a python based web API for a shutter.

`shutter.py` is the hardware API for the shutter, and other files are used to setup the FastAPI server.

To run the server, first copy & paste the `default-config.json` file and name it `config.json`, then run

    (base) $ python register.py

to add a new user for the server.
Or if you know how to hash a password, you can manually add a user by editing the json file directly.

Then, generate a reliable random number,such as `68b90e6f46e3509ffae879b24bd9a3fed14c51a156eed73c9306eb45455b244b` 
(Don't actually use this one! This is only an example to show you the accepted format of the number. 
You can get a random number like this with something like `openssl rand -hex 32` on a trusted computer), 
and fill it in the `auth - jwt - secret` field in `config.json`.
This secret key is used to sign JWTs used to authorize the clients, so keep it safe.

Finally, install the dependencies of the server in a virtualenv.
You can do this with

    $ pip install fastapi[all]

or

    $ pip install fastapi uvicorn[standard]

Suppose you have all dependencies installed in a conda env "`fastapi-dev`", 
run a conda shell in root directory of labctrl:

    (base) $ conda activate fastapi-dev
    (fastapi-dev) $ uvicorn toolbox.shutter.generic.main:app

labctrl recommands using anaconda distribution of python, 
because it comes with a lot of scientific calculation packages we need.
However, using a vanilla python distribution also works well.
Simply follow FastAPI's requirements to setup the dependencies.

If you do not intend to use a network server to control your device, 
and your application is also constructed with python, you can also directly import the hardware API by

    >>> import toolbox.shutter.generic as hardware

**NOTE:** If you plan to use a web browser to directly access the web API, such as the demo apps in labctrl WidgetBox, you must also add your frontend application's origin to the `CORS - origins` list in `config.json`.
For example, if you are serving your frontend application from `http://yourowndomain.org:8080`, and your web API is served at `http://localhost:8000`, then your browser prevents js to send requests to your web API because they are from different origins, unless the web API server tells the browser that this is okay. Thus you need to add `http://yourowndomain.org:8080` to your CORS origins list, so that our web API server can do the rest stuff for you.

## api

This directory contains library files to be included in other applications that intend to use this toolbox.

For python libraries, just copy and paste the needed file in your project and you are good to go.
For a simple application or script, you can use the package in `api/python` directory by

    >>> from toolbox.shutter.api.python import RemoteShutter
    >>> r = RemoteShutter()
    >>> r.turn_on()

Another option is to use the package in `api/python_openapi` directory, 
this is the full RESTful client for the toolbox, 
and has all the data validation and type checks, 
so it is more suitable for integrating into larger project.

For C++ libraries, just copy and paste the source files (.cpp and .h) to your project and you are good to go.
You can also build the library seperately and dynamically link the library.

## tests

This directory contains unit tests and integration tests for this whole project.

You can find what the tests are for in their file header.

To run the python unit tests, take the hardware API test as an example, simply do

    (base) $ python -m unittest toolbox.shutter.tests.test_generic_hardware

Some of the tests are integration tests for testing the whole API server.
To run the integration tests, take the raw server test as an example:

First, we need to setup the server and put it in test mode. Set meta parameter `IS_TESTING` in main.py of the server to `True` and start the server as normal.

Then, fill correct connection information and authentication information in `test_generic_server.config.json`, and run

    (base) $ python -m unittest toolbox.shutter.tests.test_generic_server
