import os
from sqlalchemy import Column, String, Integer
from flask_sqlalchemy import SQLAlchemy
import json

database_filename = "database.db"
project_dir = os.path.dirname(os.path.abspath(__file__))
database_path = "sqlite:///{}".format(os.path.join(project_dir, database_filename))

db = SQLAlchemy()


def setup_db(app):
    '''
    Binds a flask application and a SQLAlchemy service.
    '''
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)


def db_drop_and_create_all():
    '''
    Drops the database tables and starts a fresh database.

    Can be used to initialize a clean the database.

    A dummy drink is inserted to the drink table for testing.

    !!NOTE you can change the database_filename variable to have
    multiple versions of a database
    '''
    db.drop_all()
    db.create_all()

    # insert a dummy drink for testing
    drink = Drink(
        title='White Coffee',
        recipe='[{"name": "coffee", "color": "black", "parts": 1},{"name": "milk", "color": "white", "parts": 3}]'
    )
    drink.insert()
    drink2 = Drink(
        title='White Coffee2',
        recipe='[{"name": "coffee2", "color": "black2", "parts": 2},{"name": "milk2", "color": "white2", "parts": 4}]'
    )
    drink2.insert()

def db_rollback():
    '''
    Rollbacks the database in the event of an error while updating/deleting
    '''
    db.session.rollback()


class Drink(db.Model):
    '''
    Drink - a persistent drink entity, extends the base SQLAlchemy Model.
    '''
    # Autoincrementing, unique primary key
    id = Column(Integer().with_variant(Integer, "sqlite"), primary_key=True)
    # String Title
    title = Column(String(80), unique=True)
    # the ingredients blob - this stores a lazy json blob
    # the required datatype is [{'color': string, 'name':string, 'parts':number}]
    recipe =  Column(String(180), nullable=False)


    def short(self):
        '''
        Short form representation of the Drink model
        '''
        # print(json.loads(self.recipe))
        short_recipe = [{'color': r['color'], 'parts': r['parts']} for r in json.loads(self.recipe)]
        return {
            'id': self.id,
            'title': self.title,
            'recipe': short_recipe
        }

    def long(self):
        '''
        Long form representation of the Drink model
        '''
        return {
            'id': self.id,
            'title': self.title,
            'recipe': json.loads(self.recipe)
        }


    def insert(self):
        '''
        Inserts a new model into a database.

        The model must have a unique name.

        The model must have a unique id or null id

        EXAMPLE
            drink = Drink(title=req_title, recipe=req_recipe)
            drink.insert()
        '''
        db.session.add(self)
        db.session.commit()


    def delete(self):
        '''
        Deletes a new model into a database.

        The model must exist in the database.

        EXAMPLE
            drink = Drink(title=req_title, recipe=req_recipe)
            drink.delete()
        '''
        db.session.delete(self)
        db.session.commit()


    def update(self):
        '''
        Updates a new model into a database.

        The model must exist in the database.

        EXAMPLE
            drink = Drink.query.filter(Drink.id == id).one_or_none()
            drink.title = 'Black Coffee'
            drink.update()
        '''
        db.session.commit()


    def __repr__(self):
        return json.dumps(self.short())