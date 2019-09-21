sqlalchemy-api-handler
======================

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

Suppose a request POST /users {"email": "marx.foo@plop.fr", name: "Marx Foo"} :

.. code-block:: python

    from flask import Flask, jsonify, request
    from sqlalchemy_api_handler import ApiHandler

    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///example.sqlite"
    db = SQLAlchemy(app)
    ApiHandler.set_db(db)

    class User(ApiHandler, db.Model):
        email = db.Column(db.String, unique=True, nullable=False)
        name = db.Column(db.String, unique=True, nullable=False)

    @app.route('/users', methods=['POST'])
    def post_user():
      user = User(**request.form)
      ApiHandler.save(user)
      return jsonify(as_dict(user))

The success result will have stored a user object at, let's say id = 32,
and so will fetch an object at humanized id = humanize(32), ie

.. code-block:: text

  {"id": "EA", "email": "marx.foo@plop.fr", name: "Marx Foo"}

Playing with nesting data
-------------------------

Suppose a request GET /offers

.. code-block:: python

    from flask import Flask, jsonify, request
    from sqlalchemy.orm import relationship
    from sqlalchemy_api_handler import ApiHandler

    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///example.sqlite"
    db = SQLAlchemy(app)
    ApiHandler.set_db(db)

    class Venue(ApiHandler, db.Model):
        address = db.Column(db.String, unique=True, nullable=False)
        name = db.Column(db.String, unique=True, nullable=False)

    class Offer(ApiHandler, db.Model):
        name = db.Column(db.String, unique=True, nullable=False)
        venueId = db.Column(db.BigInteger,
                     db.ForeignKey("venue.id"),
                     nullable=False,
                     index=True)
        venue = relationship('Venue',
                             foreign_keys=[venueId],
                             backref='offers')

    class Stock(ApiHandler, db.Model):
        available = db.Column(db.Integer, nullable=False)
        offerId = db.Column(db.BigInteger,
                         db.ForeignKey('offer.id'),
                         index=True,
                         nullable=False)
        offer = relationship('Offer',
                             foreign_keys=[offerId],
                             backref='stocks')

    venue = Venue(address="Somewhere I belong", name="MyVenue")
    offer = Offer(name="MyOffer")
    stock = Stock(available=10)
    stock.offer = offer
    offer.venue = venue
    ApiHandler.save(stock)

    offer_includes = [
      'stocks',
      {
        "key": 'venue',
        "includes": [
          '-address'
        ]
      }
    ]

    @app.route('/offers', methods=['GET'])
    def get_offers():
      offers = Offer.query.all()
      return jsonify(as_dict(offers, includes=offer_includes))

The success will return

.. code-block:: text

  [
    {
      "id": "AE",
      "name": "MyOffer",
      "stocks": [
        {
          "available": 10,
          "id": "AE"
        }
      ],
      "venue": {
        "name": "MyVenue"
      }
    }
  ]

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
------

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
