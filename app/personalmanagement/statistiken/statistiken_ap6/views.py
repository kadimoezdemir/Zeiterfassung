# Flask imports
from flask import Blueprint, redirect, url_for

# Python imports
import datetime

# Custom imports
from app.personalmanagement.mitarbeiter.views import funktionen_eintragen
from app.models.models import Mitarbeiter
from app.standardfunktionen.statistiken.meine_statistiken_ap6.views import zeige_stundensaldo_von_mitarbeiter
from app.standardfunktionen.statistiken.meine_statistiken_ap6.views import zeige_jahres_stunden_uebersicht_von_mitarbeiter
from app.main.forms import role_req


# define the blueprint
statistiken_ap6 = Blueprint('statistiken_ap6', __name__, template_folder='pages')


# all routes
@statistiken_ap6.route('/stundensaldo/<username>/<int:year>')
@statistiken_ap6.route('/stundensaldo/<username>', defaults={'year': datetime.datetime.now().year})
@statistiken_ap6.route('/stundensaldo', defaults={'username': None, 'year': None })
@role_req("Personalsachbearbeiter")
def stundensaldo(username, year):
    # Prüfen ob Mitarbeiter ausgewählt wurde
    if username is None:
        return zeige_suche('statistiken_ap6.stundensaldo')

    return zeige_stundensaldo_von_mitarbeiter(get_mitarbeiter_by_username(username), year, True)


@statistiken_ap6.route('/jahresstunden_uebersicht/<username>/<int:year>')
@statistiken_ap6.route('/jahresstunden_uebersicht/<username>', defaults={'year': datetime.datetime.now().year})
@statistiken_ap6.route('/jahresstunden_uebersicht', defaults={'username': None, 'year': None})
@role_req("Personalsachbearbeiter")
def jahresstunden_uebersicht(username, year):
    # Prüfen, ob ein Mitarbeiter ausgewählt wurde
    if username is None:
        return zeige_suche('statistiken_ap6.jahresstunden_uebersicht')

    return zeige_jahres_stunden_uebersicht_von_mitarbeiter(get_mitarbeiter_by_username(username), year, True)


def zeige_suche(route):
    f = [
        {
            "route": route,
            "label": "Auswählen"
        }
    ]
    return redirect(url_for("mitarbeiter.suchen", funktionen=funktionen_eintragen(f)))


def get_mitarbeiter_by_username(username):
    return Mitarbeiter.objects.filter(username=username).first()

