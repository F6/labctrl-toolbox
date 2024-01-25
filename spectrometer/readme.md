# Spectrometer Toolbox

This toolbox is part of the labctrl-toolbox project, which is a submodule of labctrl project.

## Packages

- [`FX2000`](#FX2000): FastAPI server and hardware API for IdeaOptics FX2000 spectrometer.
- [`api`](#api): Reference API implementation in different languages.
- [`tests`](#tests): All unit tests and integration tests.

## FX2000

This package includes a template project that provides a python based web API for a single point sensor.

`spectrometer.py` is the hardware API for the spectrometer, and other files are used to setup the FastAPI server.

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
    (fastapi-dev) $ uvicorn toolbox.spectrometer.FX2000.main:app --log-config logging_helper/uvicorn_log.config.yaml --host 0.0.0.0

labctrl recommands using anaconda distribution of python,
because it comes with a lot of scientific calculation packages we need.
However, using a vanilla python distribution also works well.
Simply follow FastAPI's requirements to setup the dependencies.

If you do not intend to use a network server to control your device,
and your application is also constructed with python, you can also directly import the hardware API by

    >>> import toolbox.spectrometer.FX2000 as hardware

**NOTE:** If you plan to use a web browser to directly access the web API, such as the demo apps in labctrl WidgetBox, you must also add your frontend application's origin to the `CORS - origins` list in `config.json`.
For example, if you are serving your frontend application from `http://yourowndomain.org:8080`, and your web API is served at `http://localhost:8000`, then your browser prevents js to send requests to your web API because they are from different origins, unless the web API server tells the browser that this is okay. Thus you need to add `http://yourowndomain.org:8080` to your CORS origins list, so that our web API server can do the rest stuff for you.

## api

[TODO]

## tests

[TODO]
