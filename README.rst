sqlalchemy-handler
==================

SQLAlchemy-Handler is an extension that still like Flask-SQLAlchemy adds more support for SQLAlchemy to your application. It helps to handle models with
humanized ids once it is jsonified, throws api errors for some casting of value during the save time.

[![CircleCI](https://circleci.com/gh/betagouv/sqlalchemy-handler/tree/master.svg?style=svg)](https://circleci.com/gh/betagouv/sqlalchemy-handler/tree/master)
[![Coverage Status](https://coveralls.io/repos/github/betagouv/sqlalchemy-handler/badge.svg)](https://coveralls.io/github/betagouv/sqlalchemy-handler)

Installing
----------

Install and update using `pip`:

.. code-block:: text

  $ pip install -U SQLAlchemy-Handler

A Simple Example
----------------

.. code-block:: python

    from flask import Flask
    from sqlalchemy_handler import Handler

    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///example.sqlite"
    db = SQLAlchemy(app)

    class User(Handler, db.Model):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String, unique=True, nullable=False)
        email = db.Column(db.String, unique=True, nullable=False)

    user = User(username="Flask", email="example@example.com")
    Handler.save(user)

Links
-----

-   Documentation: https://sqlalchemy-handler.betagouv.fr/
-   Releases: https://pypi.org/project/SQLAlchemy-Handler/
-   Code: https://github.com/betagouv/sqlalchemy-handler
-   Issue tracker: https://github.com/betagouv/sqlalchemy-handler/issues
-   Test status: https://travis-ci.org/betagouv/sqlalchemy-handler
-   Test coverage: https://codecov.io/gh/betagouv/sqlalchemy-handler

- Flask: https://betagouvprojects.com/p/flask/
- SQLAlchemy: https://www.sqlalchemy.org
- pip: https://pip.pypa.io/en/stable/quickstart/

Deploy
----------

First, make sure that the deploy environment is started:

.. code-block:: text

  ./sqlah start


In a second tab, then:

2. Change the __version__ into sqlalchemy_handler/__init__.py

3. Pre publish:

.. code-block:: text

  ./sqlah prepublish

4. Publish:

.. code-block:: text

  ./sqlah publish
