# -*- coding: utf-8 -*-
import os
import sys

from flask.ext.rq import RQ
from flask.ext.assets import Environment
from flask import Flask, render_template, send_from_directory

from hive_client.views import base_blueprint
from hive_client.views import blueprint as api_blueprint
from hive_client.views import IndexView

app = Flask(__name__)
app.config.from_object('config')


########################
# Configure Secret Key #
########################


def install_secret_key(app, filename='secret_key'):
    """Configure the SECRET_KEY from a file
    in the instance directory.

    If the file does not exist, print instructions
    to create it from a shell with a random key,
    then exit.
    """
    filename = os.path.join(app.instance_path, filename)

    try:
        app.config['SECRET_KEY'] = open(filename, 'rb').read()
    except IOError:
        print('Error: No secret key. Create it with:')
        full_path = os.path.dirname(filename)
        if not os.path.isdir(full_path):
            print('mkdir -p {filename}'.format(filename=full_path))
        print('head -c 24 /dev/urandom > {filename}'.format(filename=filename))
        sys.exit(1)

if not app.config['DEBUG']:
    install_secret_key(app)

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

assets = Environment()
assets.init_app(app)

app.register_blueprint(base_blueprint)
app.register_blueprint(api_blueprint)

IndexView.register(app, route_base='/')

# Later on you'll import the other blueprints the same way:
#from app.comments.views import mod as commentsModule
#from app.posts.views import mod as postsModule
#app.register_blueprint(commentsModule)
#app.register_blueprint(postsModule)
RQ(app)  # tasks


@app.route('/media/<path:filename>')
def media(filename):
    return send_from_directory(app.config['MEDIA_PATH'], filename)
