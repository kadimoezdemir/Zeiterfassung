from flask import Blueprint, render_template, flash, redirect, request, url_for, session
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash
from flask_login import current_user, login_user
from datetime import datetime, timedelta
from functools import reduce
from app.main.forms import LoginForm
from app.models.models import Mitarbeiter, Zeitstempel
from app.main.forms import role_req

main = Blueprint('main', __name__, template_folder='pages', static_folder='main-static')


@main.route('/', methods=['GET', 'POST'])
@role_req('Mitarbeiter', 'Personalsachbearbeiter')
def home():
    ma = Mitarbeiter.objects(username=current_user.username).first()

# letzter Zeitstempel wird herausgesucht
    if len(ma.zeitstempel) != 0:
        zt = reduce(lambda a, b: a if a.eingestempelt > b.eingestempelt else b, ma.zeitstempel)
    else:
        zt = False

# Ein- und Ausstempelfunktion
    iseingestempelt = False
    if request.method == "POST":
        if request.form["submitButton"] == 'Einstempeln':
            z = Zeitstempel()
            z.eingestempelt = datetime.now(tz=None)
            z.ausgestempelt = None
            z.set_id(ma)
            ma.zeitstempel.append(z)
            ma.save()
        elif request.form["submitButton"] == 'Ausstempeln':
            zt.ausgestempelt = datetime.now(tz=None)
            ma.save()
        return redirect(url_for("main.home"))

# Die Ermittlung der Zeitdifferenz zwischen Aufrufen der Seite und des letzten Einstempel-Zeitstempels
# So wird nachvollzogen, ob sich ein User vergessen hat auszustempeln
    if len(ma.zeitstempel) != 0:
        ztdelta = (datetime.now(tz=None) - zt.eingestempelt).total_seconds()
    else:
        ztdelta = False

# iseingestempelt wird True gesetzt, wenn zuvor eingestempelt wurde
    if zt:
        if zt.ausgestempelt is None:
            iseingestempelt = True

    return render_template("index.html", iseingestempelt=iseingestempelt, ztdelta=ztdelta, zt=zt, info=session)


@main.route("/login", methods=["GET", "POST"])
def login():
    print(current_user.is_authenticated) #Debugfunktion
    if current_user.is_authenticated:
        print(current_user.rolle)   #Debugfunktion
        return redirect(url_for(".home"))

    form = LoginForm()

    if form.validate_on_submit():
        user = Mitarbeiter.objects(username=form.username.data).first() #Mitarbeiterobjekt zuweisen
        print(current_user) #Debugfunktion
        login_user(user)
        print(current_user.username) #Debugfunktion
        next = request.args.get('next')
        return redirect(next or url_for(".home"))

    return render_template("login.html", form=form)


@main.route("/logout")
def logout():
    logout_user()
    return redirect(url_for(".home"))

#Route für Unit-Tests
@main.route("/test-mitarbeiter")
@role_req("Mitarbeiter")
def mitarbeitertest():
    return "You can only see this if you are logged in!", 200

#Route für Unit-Tests
@main.route("/test-personalsachbearbeiter")
@role_req("Personalsachbearbeiter")
def personalsachbearbeitertest():
    return "You can only see this if you are logged in!", 200
