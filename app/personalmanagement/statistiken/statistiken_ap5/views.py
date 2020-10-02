import json

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required

from app.main.forms import role_req
from app.models.models import Mitarbeiter
from app.models.models import Fehlzeit
from datetime import *
from functools import reduce
from app.personalmanagement.mitarbeiter.views import funktionen_eintragen
from app.standardfunktionen.statistiken.meine_statistiken_ap5.views import kalender, group_month, fehlzeiten_liste, zeige_legende

# define the blueprint
statistiken_ap5 = Blueprint('statistiken_ap5', __name__, template_folder='pages')


def anwesend(mitarbeiter):
    # finde den neusten Zeitstempel
    if len(mitarbeiter.zeitstempel) == 0:
        return False
    else:
        neuster_zeitstempel = reduce(lambda a, b: a if a.eingestempelt > b.eingestempelt else b, mitarbeiter.zeitstempel)
    # Wenn kein Austempel zu neustem Einstemepl gibt, ist MA anwesend
    if neuster_zeitstempel.ausgestempelt is None:
        return True
    else:
        return False #MA ist abwesend


def grund_fehlzeit(mitarbeiter):
    heute = date.today()
    if len(mitarbeiter.fehlzeiten) == 0:
        return ""
    else:
        aktuelste_fehlzeit = reduce(lambda a, b: a if a.datum_start > b.datum_start else b, mitarbeiter.fehlzeiten)
    # MA hat eingetragene Fehlzeit
    if aktuelste_fehlzeit.datum_start <= heute <= aktuelste_fehlzeit.datum_ende:
        return aktuelste_fehlzeit.grund
    else:
        return ""


# all routes
@statistiken_ap5.route('/anwesenheitstableau')
@role_req("Personalsachbearbeiter")
def anwesenheitstableau():
    mitarbeiter = Mitarbeiter.objects(aktiv=True)

    return render_template("anwesenheitstableau.html", info=session, mitarbeiter=mitarbeiter, anwesend=anwesend, grund=grund_fehlzeit)


@statistiken_ap5.route('/jahresarbeitstage_uebersicht')
@role_req("Mitarbeiter", "Personalsachbearbeiter")
def jahresarbeitstage_uebersicht():
    f = [
        {
            "route": "statistiken_ap5.jahresarbeitstage",
            "label": "Arbeitstage-Übersicht"
        }
    ]
    return redirect(url_for("mitarbeiter.suchen", funktionen=funktionen_eintragen(f)))


@statistiken_ap5.route('/jahresarbeitstage/<username>/<int:year>')
@statistiken_ap5.route('/jahresarbeitstage/<username>', defaults={'year': datetime.now().year})
@statistiken_ap5.route('/jahresarbeitstage', defaults={'username': None, 'year': None})
@role_req("Personalsachbearbeiter")
def jahresarbeitstage(username, year):
    user = Mitarbeiter.objects(username=username).first()

    min_year = datetime.now().year
    # erstes Arbeitsjahr herausfinden
    for t in user.zeitstempel:
        eingestempelt_jahr = t.eingestempelt.year
        min_year = min(min_year, eingestempelt_jahr)

    return render_template("jahresarbeitstage.html", username=username, info=session,legende=zeige_legende, user=user, kalender=kalender, group_month=group_month, fehlzeiten_liste=fehlzeiten_liste, min_year=min_year, now_year=datetime.now().year, year=year)
