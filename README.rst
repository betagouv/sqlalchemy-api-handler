sqlalchemy-api-handler
==================

SQLAlchemy-Api-Handler is an extension that adds support for handling apis with sqlalchemy. It helps to handle models with
humanized ids once it is jsonified, throws api errors for some casting of value during the save time, and dictifies model objects into jsonified ones.

[![CircleCI](https://circleci.com/gh/betagouv/sqlalchemy-api-handler/tree/master.svg?style=svg)](https://circleci.com/gh/betagouv/sqlalchemy-api-handler/tree/master)
[![Coverage Status](https://coveralls.io/repos/github/betagouv/sqlalchemy-api-handler/badge.svg)](https://coveralls.io/github/betagouv/sqlalchemy-api-handler)

Installing
----------

Install and update using `pip`:

.. code-block:: text

  $ pip install -U SQLAlchemy-Api-Handler

A Simple Example
----------------

.. code-block:: python

    from flask import Flask
    from sqlalchemy_api_handler import ApiHandler

    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///example.sqlite"
    db = SQLAlchemy(app)
    ApiHandler.set_db(db)

    class User(ApiHandler, db.Model):
        id = db.Column(db.Integer, primary_key=True)
        email = db.Column(db.String, unique=True, nullable=False)
        name = db.Column(db.String, unique=True, nullable=False)

    user = User(firstName="Flask", lastName="Foo", email="example@example.com")
    ApiHandler.save(user)

Links
-----

-   Documentation: https://sqlalchemy-api-handler.betagouv.fr/
-   Releases: https://pypi.org/project/SQLAlchemy-Api-Handler/
-   Code: https://github.com/betagouv/sqlalchemy-api-handler
-   Issue tracker: https://github.com/betagouv/sqlalchemy-api-handler/issues
-   Test status: https://travis-ci.org/betagouv/sqlalchemy-api-handler
-   Test coverage: https://codecov.io/gh/betagouv/sqlalchemy-api-handler

- Flask: https://betagouvprojects.com/p/flask/
- SQLAlchemy: https://www.sqlalchemy.org
- pip: https://pip.pypa.io/en/stable/quickstart/

Deploy
----------

First, make sure that the deploy environment is started:

.. code-block:: text

  ./sqlaah start


In a second tab, then:

2. Change the __version__ into sqlalchemy_api_handler/__init__.py

3. Pre publish:

.. code-block:: text

  ./sqlaah prepublish

4. Publish:

.. code-block:: text

  ./sqlaah publish
