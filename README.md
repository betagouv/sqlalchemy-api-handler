sqlalchemy-manager
================

SQLAlchemy-Manager is

[![CircleCI](https://circleci.com/gh/betagouv/sqlalchemy-manager/tree/master.svg?style=svg)](https://circleci.com/gh/betagouv/sqlalchemy-manager/tree/master)
[![Coverage Status](https://coveralls.io/repos/github/betagouv/sqlalchemy-manager/badge.svg)](https://coveralls.io/github/betagouv/sqlalchemy-manager)

Installing
----------

Install and update using `pip`_:

.. code-block:: text

  $ pip install -U SQLAlchemy-Manager


A Simple Example
----------------

.. code-block:: python

    from flask import Flask
    from sqlalchemy_manager import Manager

    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///example.sqlite"
    db = SQLAlchemy(app)

    class User(Manager, db.Model):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String, unique=True, nullable=False)
        email = db.Column(db.String, unique=True, nullable=False)

    user = User(username="Flask", email="example@example.com")
    Manager.save(user)


Links
-----

-   Documentation: https://sqlalchemy-manager.betagouv.fr/
-   Releases: https://pypi.org/project/SQLAlchemy-Manager/
-   Code: https://github.com/betagouv/sqlalchemy-manager
-   Issue tracker: https://github.com/betagouv/sqlalchemy-manager/issues
-   Test status: https://travis-ci.org/betagouv/sqlalchemy-manager
-   Test coverage: https://codecov.io/gh/betagouv/sqlalchemy-manager

.. _Flask: https://betagouvprojects.com/p/flask/
.. _SQLAlchemy: https://www.sqlalchemy.org
.. _pip: https://pip.pypa.io/en/stable/quickstart/
