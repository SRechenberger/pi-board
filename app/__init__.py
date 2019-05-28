import os

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_uploads import configure_uploads, UploadSet, IMAGES
from flask_babel import Babel
from flask_moment import Moment

from config import Config


images = UploadSet(
    'images',
    IMAGES,
    default_dest=lambda app:
        os.path.join(app.instance_path, 'profile_pics')
)

bootstrap = Bootstrap()
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
babel = Babel()
moment = Moment()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)


    bootstrap.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    babel.init_app(app)
    moment.init_app(app)
    configure_uploads(app, (images,))

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    app.jinja_env.globals.update(image_url=images.url)
    app.jinja_env.globals.update(len=len)
    app.jinja_env.globals.update(MAX_DEPTH=app.config['MAX_DEPTH'])
    app.jinja_env.globals.update(VERSION=app.config['VERSION'])

    return app

from app import models
