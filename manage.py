#!/usr/bin/env python3

import os, sys, random

from werkzeug.security import generate_password_hash
from flask_script import Manager
from flask_script.commands import ShowUrls, Clean, Command, prompt_bool
from app.factory import create_app, assets_env
from app.config import *
from flask_login import LoginManager

from app.models.models import *
from manage_funcs.fill_db import FillDB
from datetime import timedelta
import flask


# default to dev config because no one should use this in
# production anyway
env = os.environ.get('APPNAME_ENV', 'dev')
app = create_app(TestingConfig())

login = LoginManager(app)

@login.user_loader
def load_user(aidi):
    return Mitarbeiter.objects(id=aidi).first()
#automatic logout
@app.before_request
def before_request():
    flask.session.permanent = True
    app.permanent_session_lifetime = timedelta(hours = 12)
    flask.session.modified = True


manager = Manager(app)

manager.add_command("fill-db", FillDB())
manager.add_command("show-urls", ShowUrls())
manager.add_command("clean", Clean())

from flask_assets import ManageAssets
manager.add_command("assets", ManageAssets(assets_env))

@manager.shell
def make_shell_context():

    return dict(app=app)


if __name__ == "__main__":
    manager.run()
