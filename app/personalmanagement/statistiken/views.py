from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.main.forms import role_req

# define the blueprint
statistiken = Blueprint('statistiken', __name__, template_folder='pages')

# all routes
@statistiken.route('/')
@role_req("Personalsachbearbeiter")
def home():
    return render_template('statistiken.html', info=session)