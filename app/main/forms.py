from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms import validators
from werkzeug.security import check_password_hash
from flask import redirect, flash, url_for
from flask_login import current_user
from app.models.models import Mitarbeiter
from functools import wraps

ROLE_REQ_ON = True #Flag, welches den Decorator deaktivieren kann

def role_req(*arrrgs): #Decorator, welcher bei Routen den Zugriff beschränkt
    def required(f):
        @wraps(f)
        def wrap(*args, **kwargs):
            if not ROLE_REQ_ON: #Besagter Flag
                return f(*args, **kwargs) #Funktion wird verlassen -> keine Auswirkungen auf weiteren Verlauf
            if current_user.is_authenticated:
                for arrr in arrrgs:
                    if current_user.rolle == arrr: #Wenn User in args angegebene Rolle besitzt -> keine Auswirkungen auf weiteren Verlauf
                        return f(*args, **kwargs)
            else:
                flash("Sie sind nicht eingeloggt.", "warning") # Falls User nicht eingeloggt ist, Weiterleitung auf Login-Seite
                return redirect(url_for("main.login"))
            flash("Sie sind nicht autorisiert, die Seite zu sehen.", "warning") # Falls User nicht die benötigte Rolle hat, Weiterleitung auf Startseite
            return redirect(url_for("main.home"))
        return wrap
    return required

class LoginForm(FlaskForm):
    """
    The login form
    """
    #Inhalt der Name und PW Felder auslesen
    username = StringField(u'Username', validators=[validators.DataRequired()])
    password = PasswordField(u'Password', validators=[validators.optional()])

    def validate(self):
        check_validate = super(LoginForm, self).validate()

        # if our validators do not pass
        if not check_validate:
            return False

        # does our user exist?
        user = Mitarbeiter.objects(username=self.username.data)
        if not user:
            self.username.errors.append('Passwort oder Mitarbeiter ID falsch')
            return False

        # is the user active
        if not user.first().aktiv:
            self.username.errors.append('Dieser Account wurde deaktiviert. Wenden Sie sich an einen Personalsachbearbeiter.')
            return False

        # do the passwords match
        if not check_password_hash(user.first().passwort_hash, self.password.data):
            self.password.errors.append('Passwort oder Mitarbeiter ID falsch')
            return False

        return True



