from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required
import calendar
from datetime import date

from app.main.forms import role_req
from app.models.models import Mitarbeiter
from flask import Markup
from datetime import *
from functools import reduce
from math import floor
from flask_login import current_user, login_user


# define the blueprint
meine_statistiken_ap5 = Blueprint('meine_statistiken_ap5', __name__, template_folder='pages')


# erstelle Liste mit allen Fehlzeiten eines Users
def fehlzeiten_liste(user, x_year):

    # tage_liste [einzelner Tag, Fehlzeit?, Grund fuer Fehlzeit, gearbeitet?]
    tage_liste = [(datetime(x_year, 1, 1).date(), False, "", False)]
    while tage_liste[-1][0].year == x_year:
        tage_liste.append((tage_liste[-1][0]+timedelta(days=1), False, "", False))
    # Ein Tag vom naechsten Jahr muss noch entfernt werden
    tage_liste.pop()
    # Fehlzeiten werden nach Jahr gefiltert
    fehlzeiten_von_jahr = list(filter(lambda a: a.datum_start.year == x_year, user.fehlzeiten))
    # Trage alle Tage in array (mit Fehlzeit Grund)
    for element in fehlzeiten_von_jahr:
        i = element.datum_start
        while i <= element.datum_ende:
            day_in_tage_list = i.timetuple().tm_yday-1
            tage_liste[day_in_tage_list] = (tage_liste[day_in_tage_list][0], True, element.grund, False)
            i = i + timedelta(days=1)

    # alle Arbeitstage rausfiltern
    gearbeitet = list(filter(lambda a: a.eingestempelt.year == x_year, user.zeitstempel))
    for element in gearbeitet:
        i = element.eingestempelt
        # Ueberpruefe ob ausgestempelt existiert
        if element.ausgestempelt is not None:
            while i <= element.ausgestempelt:
                day_in_tage_list = i.timetuple().tm_yday - 1
                # Fuege gearbeiteten Tag in tage_liste (alle Tage -> Fehlzeiten mit Grund, gearbeitet, oder nichts von beidem)
                tage_liste[day_in_tage_list] = (tage_liste[day_in_tage_list][0], tage_liste[day_in_tage_list][1], tage_liste[day_in_tage_list][2], True)
                i = i + timedelta(days=1)

    return tage_liste


# erstelle Liste gruppiert nach Monat
def group_month(liste):
    monthlist = [
        [] for i in range(12)
    ]

    for x in liste:
        y = x[0].month
        monthlist[y-1].append(x)

    return monthlist


def zeige_legende():
    legende_string = '<div class="row">' \
                      '<div class="col-sm-2 text-center table-danger"><b>Erkrankung</b></div>' \
                      '<div class="col-sm-2 text-center table-info"><b>Home-Office</b></div>' \
                      '<div class="col-sm-2 text-center table-secondary"><b>Urlaub</b></div>' \
                      '<div class="col-sm-2 text-center table-warning"><b>Zeitausgleich</b></div>' \
                      '<div class="col-sm-2 text-center light"><b>nichts</b></div>' \
                      '<div class="col-sm-2 text-center table-success"><b>gearbeitet</b></div>' \
                      '</div>' \
                      #'</li>'
    return Markup(legende_string)


def kalender(monthlist, year):
    html_string = ""
    # Monatliste
    m_l = ["Januar", "Februar", "März",
           "April", "Mai", "Juni", "Juli",
           "August", "September", "Oktober",
           "November", "Dezember"
           ]

    # parameter
    table_entry = '<td id="calendar_entry_'
    day = 1

    html_string += '<div class="row">'
    for monat in monthlist:
        month = monat[0][0].month
        if month < 3:
            year = year - 1

        html_string += '<div class="col-md-4">'
        html_string += '<table class="table table-bordered" id="kalender">'
        html_string += '<tr><td colspan=7 class="text-center">'
        html_string += str(m_l[month-1]) + '</td>' + '</tr><tr>'
        wochentage = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
        # Fuege Wochentage Beschriftng hinzu
        for t in wochentage:
            html_string += '<td class="calendar_day">' + t + '</td>'

        html_string += '</tr><tr>'
        #Berechne Schaltjahre und an welchem Wochentag der jeweilige Monat beginnt. (Formel aus dem Internet verwendet)
        w = ((day + floor(2.6 * ((month + 9) % 12 + 1) - 0.2) + year % 100 + floor(year % 100 / 4) + floor(year / 400) - 2 * floor(year / 100) - 1) % 7 + 7) % 7 + 1
        count = 1
        x = 1
        if 1 <= w <= 7:
            while x < w:
                html_string += table_entry + str(count) + '" /td>'
                x = x + 1
        else:
            return False
        # Erkrankung = "table-danger"
        # Home-Office = "table-info"
        # Urlaub = "table-secondary"
        # Zeitausgleich = "table-warning"
        # gearbeitet also "" = "table-success"
        grund_farbe_dictonary={'Erkrankung': 'table-danger', 'Home-Office': 'table-info', 'Urlaub': 'table-secondary', 'Zeitausgleich': 'table-warning', '': 'table-light'}
        # Fuege farbliche Markierung der Tage hinzu
        for tag_aus_monat in monat:
            if tag_aus_monat[3] == False:
                farbe = grund_farbe_dictonary[tag_aus_monat[2]]
            elif tag_aus_monat[3] == True:
                if tag_aus_monat[2] == "":
                    farbe = "table-success"
                else:
                    return "Fehler bei gearbeitet1"
            else:
                return "Fehler bei gearbeitet2"
            html_string += '<td class="' + farbe + '"' + 'id="calendar_entry_' + str(count) + '">' + str(count) + '</td>'
            # ende der Tabellenzeile (7 Wochentage) -> neue Zeile
            if (count+x-1) % 7 == 0:
                html_string += '</tr>'
            count = count + 1
        html_string += '</table></div>'
    html_string += '</div>'
    return Markup(html_string)


# all routes
@meine_statistiken_ap5.route('/meine_jahresarbeitstage_uebersicht/<int:year>')
@meine_statistiken_ap5.route('/meine_jahresarbeitstage_uebersicht', defaults={'year': datetime.now().year})
@role_req("Mitarbeiter", "Personalsachbearbeiter")
def meine_jahresarbeitstage_uebersicht(year):
    username = current_user.username
    user = Mitarbeiter.objects(username=username).first()

    min_year = year
    # finde das erste Jahr in dem Mitarbeiter gearbeitet hat
    for t in user.zeitstempel:
        eingestempelt_jahr = t.eingestempelt.year
        min_year = min(min_year, eingestempelt_jahr)

    return render_template("meine_jahresarbeitstage_uebersicht.html", info=session, legende=zeige_legende, user=user, min_year=min_year, year=year, fehl=fehlzeiten_liste, kalender=kalender, group_month=group_month, now_year=datetime.now().year)
