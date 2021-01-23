sqlalchemy-api-handler
======================

SQLAlchemy-Api-Handler is an extension that adds support for handling apis with sqlalchemy. It helps to handle models with :
   - humanized ids once it is jsonified,
   - throwing api errors for some casting of value during the save time,
   - dictification of the model objects into jsonified ones.
   - It also gives an activate method to help you better handle offline operational transforms, based on the PostgreSQL-Audit Activity model.

[![CircleCI](https://circleci.com/gh/betagouv/sqlalchemy-api-handler/tree/master.svg?style=svg)](https://circleci.com/gh/betagouv/sqlalchemy-api-handler/tree/master)


Installing
----------

Install and update using `pip`:

```bash
  $ pip install -U SQLAlchemy-Api-Handler
```

A Simple Example
----------------

Suppose a request POST /users {'email': 'marx.foo@plop.fr', name: 'Marx Foo'} :

```python
    from flask import Flask, jsonify, request
    from sqlalchemy_api_handler import ApiHandler

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.sqlite'
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
```

The success result will have stored a user object at, let's say id = 32,
and so will fetch an object at humanized id = humanize(32), ie

```
  {'id': 'EA', 'email': 'marx.foo@plop.fr', name: 'Marx Foo'}
```

Playing with nesting data
-------------------------

Suppose a request GET /offers

```python
    from flask import Flask, jsonify, request
    from sqlalchemy.orm import relationship
    from sqlalchemy_api_handler import ApiHandler

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.sqlite'
    db = SQLAlchemy(app)
    ApiHandler.set_db(db)

    class Venue(ApiHandler, db.Model):
        address = db.Column(db.String, unique=True, nullable=False)
        name = db.Column(db.String, unique=True, nullable=False)

    class Offer(ApiHandler, db.Model):
        name = db.Column(db.String, unique=True, nullable=False)
        venueId = db.Column(db.BigInteger,
                     db.ForeignKey('venue.id'),
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

    venue = Venue(address='Somewhere I belong', name='MyVenue')
    offer = Offer(name='MyOffer')
    stock = Stock(available=10)
    stock.offer = offer
    offer.venue = venue
    ApiHandler.save(stock)

    offer_includes = [
      'stocks',
      {
        'key': 'venue',
        'includes': [
          '-address'
        ]
      }
    ]

    @app.route('/offers', methods=['GET'])
    def get_offers():
      offers = Offer.query.all()
      return jsonify(as_dict(offers, includes=offer_includes))
```

The success will return

```
  [
    {
      'id': 'AE',
      'name': 'MyOffer',
      'stocks': [
        {
          'available': 10,
          'id': 'AE'
        }
      ],
      'venue': {
        'name': 'MyVenue'
      }
    }
  ]
```


Activity
-----

If you need to manage operation transforms of your entities (typically with a collaborative app working offline) :


```python
    from flask import Flask, jsonify, request
    from sqlalchemy.orm import relationship
    from sqlalchemy_api_handler import ApiHandler
    from sqlalchemy_api_handler.mixins import ActivityMixin, \
                                              HasActivitiesMixin

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.sqlite'
    db = SQLAlchemy(app)
    ApiHandler.set_db(db)

    versioning_manager.init(db.Model)
    class Activity(ActivityMixin,
                   ApiHandler,
                   versioning_manager.activity_cls):
        __table_args__ = {'extend_existing': True}

        id = versioning_manager.activity_cls.id
    ApiHandler.set_activity(Activity)

    class Venue(ApiHandler,
                db.Model,
                HasActivitiesMixin):
        address = db.Column(db.String, unique=True, nullable=False)
        name = db.Column(db.String, unique=True, nullable=False)

    @app.route('/__activities__', methods=['POST'])
    def create_activities():
        activities = [Activity(**a) for a in request.json]
        ApiHandler.activate(*activities)
        return jsonify([as_dict(activity) for activity in activities]), 201
```

The request POST /__activities__ helps you to sync your backend with the last state of pushed activities. For example, if the data posted is :
```
[
  {
    "dateCreated": "2020-08-05T08:34:06.415000Z" ,
    "entityIdentifier": "4039fb61-f085-43c4-a2ed-e5e97c5dcebc",
    "modelName": "Venue",
    "patch": { "address": "22 rue de la Loire", "name": "MyVenue" }
  },
  {
    "dateCreated": "2020-08-06T09:34:06.415000Z" ,
    "entityIdentifier": "4039fb61-f085-43c4-a2ed-e5e97c5dcebc",
    "modelName": "Venue",
    "patch": { "name": "MyVenueChanged" }
  }
]
```

It will then end to create a venue instance:
```python
venue = Venue.query.filter_by(name='MyVenueChanged').first()
print(as_dict(venue, includes=['__activities__']))
```

```
{
  '__activities__': [
    {
      'dateCreated': '2020-08-05T08:34:06.415000Z',
      'entityIdentifier': '4039fb61-f085-43c4-a2ed-e5e97c5dcebc',
      'id': 'BA',
      'modelName': 'Venue',
      'patch': {
        'address': '22 rue de la Loire',
        'name': 'MyVenue'
      },
      'verb': 'insert'
    },
    {
      'dateCreated': '2020-08-06T09:34:06.415000Z',
      'entityIdentifier': '4039fb61-f085-43c4-a2ed-e5e97c5dcebc',
      'id': 'BF',
      'modelName': 'Venue',
      'patch': {
        'name': 'MyVenueChanged'
      },
      'verb': 'update'
    }
  ],
  'activityIdentifier': '2020-08-05T08:34:06.415000Z',
  'address': "22 rue de la Loire",
  'id': 'AE',
  'name': 'MyVenueChanged'
}
```


Celery
-----
Sometimes it's hard to track celery tasks from the celery cli itself.
And you may not want use flower when you have one exposed port by application, like in scalingo classic services. Therefore, ApiHandler can also synchronise the tasks to be stored in your postgres db, then you can build your Tasks Manager Dashboard front easy as you want, querying from classic postgres api routes. See how the example is build in the api folder.


Links
-----

-   Releases: https://pypi.org/project/SQLAlchemy-Api-Handler/
-   Code: https://github.com/betagouv/sqlalchemy-api-handler
-   Issue tracker: https://github.com/betagouv/sqlalchemy-api-handler/issues

- Flask: https://betagouvprojects.com/p/flask/
- SQLAlchemy: https://www.sqlalchemy.org
- pip: https://pip.pypa.io/en/stable/quickstart/

Deploy
------

First, make sure that the deploy environment is started:

```bash
  ./sqlaah start
```

In a second tab, then:

2. Change the __version__ into sqlalchemy_api_handler/__init__.py

3. Pre publish:

```bash
  ./sqlaah prepublish
```

4. Publish:

```bash
  ./sqlaah publish
```
