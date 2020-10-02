from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required
from app.models.models import Mitarbeiter, Zeitstempel
from app.personalmanagement.mitarbeiter.views import funktionen_eintragen
from app.personalmanagement.zeitstempel.forms import ZeitstempelForm
import calendar

# define the blueprint
zeitstempel = Blueprint('zeitstempel', __name__, template_folder='pages')

# all routes
@zeitstempel.route('/')
def home():
    f = [
        {
            "route": "zeitstempel.uebersicht",
            "label": "Auswählen"
        }
    ]
    return redirect(url_for("mitarbeiter.suchen", funktionen=funktionen_eintragen(f)))


@zeitstempel.route('/uebersicht/<username>', methods=["GET", "POST"])
def uebersicht(username=None):
    if username is not None:
        ma = Mitarbeiter.objects(username=username).first()
        zt = ma.zeitstempel.filter()
        ca = calendar
        funktionen = [
            {
                "route": "zeitstempel.bearbeiten",
                "label": "Bearbeiten"
            }
        ]
        return render_template("zeitstempel.html", ca=ca, ma=ma, zt=zt, funktionen=funktionen, info=session)
    else:
        return flash(f"Kein Mitarbeiter angegeben", "danger")


@zeitstempel.route('/bearbeiten/<username>/<zt_id>', methods=["GET", "POST"])
def bearbeiten(username=None, zt_id=None):
    if username and zt_id is not None:
        ma = Mitarbeiter.objects(username=username).first()
        zeitstempel = ma.zeitstempel.filter(id=zt_id).first()
        form = ZeitstempelForm()

        if form.validate_on_submit():
            zeitstempel.fill(form)
            zeitstempel_valid = zeitstempel.validate_zeitstempel(ma)

            if zeitstempel_valid == 'true':
                ma.save()
                flash("Zeizstempel erfolgreich bearbeitet", "success")
                return redirect(url_for("zeitstempel.uebersicht", username=username))

            elif zeitstempel_valid == 'belegt':
                flash("Es existieren bereits Zeitstempel in diesem Zeitrahmen" "danger")
                return render_template("zt_bearbeiten.html", form=form, ma=ma, zt_id=zeitstempel.id, info=session)

            elif zeitstempel_valid == 'hours_difference':
                flash("Die Stempelzeiten haben eine Differenz größer als 12 Stunden" "danger")
                return render_template("zt_bearbeiten.html", form=form, ma=ma, zt_id=zeitstempel.id, info=session)

            elif zeitstempel_valid == 'rahmen':
                flash("Der gewählte Zeitrahmen ist ungültig" "danger")
                return render_template("zt_bearbeiten.html", form=form, ma=ma, zt_id=zeitstempel.id, info=session)

        form.fill(zeitstempel)
        return render_template("zt_bearbeiten.html", form=form, ma=ma, zt_id=zeitstempel.id, info=session)

    flash("Username oder Fehlzeit ID nicht vorhanden")
    return redirect(url_for("main.home", username=username))


