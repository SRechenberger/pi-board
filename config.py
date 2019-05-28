import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    VERSION = "0.19.1"

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-neve-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_DEPTH = int(os.environ.get('MAX_ANSWER_DEPTH')) or 5
