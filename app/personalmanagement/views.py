from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.main.forms import role_req
# define the blueprint
personalmanagement = Blueprint('personalmanagement', __name__, template_folder='pages')

# all routes
@personalmanagement.route('/')
@role_req("Personalsachbearbeiter")
def home():
    return render_template('personalmanagement.html', info=session)