from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from os import path


db = SQLAlchemy()
DB_NAME = "FinderDatabase.db"

def create_app():
    """Function that creates Flask application and sets initializes database, blueprints, 
    login manager, and keys.


    Returns:
        Flask: App under Flask Class.
    """
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '8snve89s0e 2ou4nb249v'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User
    
    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        """
        Function that loads user into the webapp or keeps user logged in.

        Args:
            id (any): id argument to verify if user is loggged in.

        Returns:
            Flask: returns application.
            int: returns users id from database.
        """
        return User.query.get(int(id))
    return app

def create_database(app) -> None:
    """Creates database for app if a database is not already created.

    Args:
        app (Flask): Takes argument to create database within.
    """
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')