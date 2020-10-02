from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required

# define the blueprint
meine_statistiken = Blueprint('meine_statistiken', __name__, template_folder='pages')

# all routes
@meine_statistiken.route('/')
def home():
    return render_template('meine_statistiken.html', info=session)