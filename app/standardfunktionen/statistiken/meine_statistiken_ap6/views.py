# Flask imports
from flask import Blueprint, render_template, session
from flask_login import current_user

# Python imports
import datetime

# Custom imports
from app.models.models import Mitarbeiter
from app.main.forms import role_req


# define the blueprint
meine_statistiken_ap6 = Blueprint('meine_statistiken_ap6', __name__, template_folder='pages')


# months
month_to_string = [
    "Januar", "Februar", "März", "April",
    "Mai", "Juni", "Juli", "August",
    "September", "Oktober", "November", "Dezember"
]


# all routes
@meine_statistiken_ap6.route('/meine_jahresstunden_uebersicht/<int:year>')
@meine_statistiken_ap6.route('/meine_jahresstunden_uebersicht', defaults={'year': datetime.datetime.now().year})
@role_req("Mitarbeiter" , "Personalsachbearbeiter")
def meine_jahresstunden_uebersicht(year):
    """
    Endpoint der Meine Jahres-Stunden Übersicht. Diese Funktion zeigt die Jahres-Stunden-Übersicht
    des aktuell eingeloggten Users an

    :param year: Jahr der Jahres-Stunden-Übersicht
    :return: Gerendertes Template und HTTP Status Code
    """
    # Mitarbeiter Daten abfragen
    user = current_user

    return zeige_jahres_stunden_uebersicht_von_mitarbeiter(user, year, False)


# Hilfsfunktionen für Jahres-Stunden-Übersicht Ansicht

def zeige_jahres_stunden_uebersicht_von_mitarbeiter(mitarbeiter, jahr, personalsachbearbeiter_view):
    """
    Zeigt die Jahres Stunden Uebersicht für den angegebenen Mitarbeiter an

    :param mitarbeiter: Mitarbeiter Model, dessen Jahres-Stunden-Übersicht Daten angezeigt werden sollen
    :param jahr: Jahr der Jahres-Stunden-Übersicht
    :param personalsachbearbeiter_view: Boolean, der angibt, ob es sich hierbei um eine Unterfunktion
        der Personalsachbearbeiter Funktionalitäten handelt. Falls True wird zusätzlich noch der Vor- und Nachname
        des Mitarbeiters angezeigt, dessen Daten gerade angezeigt werden. (Ja, das ist leider echt unschön gelöst :D)
    :return: Gerendertes Template und HTTP Status Code
    """

    min_jahr = get_erstes_jahr_des_einstempelns(mitarbeiter)

    zeitstempel_dieses_jahr = get_zeitstempel_von_jahr(jahr, mitarbeiter)
    monate_uebersicht = jahres_stunden_uebersicht_zusammenstellen(mitarbeiter, jahr, zeitstempel_dieses_jahr)

    return render_template(
        "mitarbeiter_jahresstunden_uebersicht.html",
        year=jahr,
        months=monate_uebersicht,
        min_year=min_jahr,
        now_year=datetime.datetime.now().year,
        info=session,
        personalsachbearbeiter_view=personalsachbearbeiter_view,
        username=mitarbeiter.username,
        name=mitarbeiter.vorname + " " + mitarbeiter.nachname,
    )


def jahres_stunden_uebersicht_zusammenstellen(user, year, zeitstempel):
    """
    Funktion, welche die Daten der Jahres Stunden Uebersicht von einem angegebenen Mitarbeiter zusammenstellt

    :param user: Mitarbeiter Model, dessen Jahres Stunden Uebersicht erstellt werden soll
    :param year: Jahr der Jahres Stunden Übersicht
    :param zeitstempel: Liste aller Zeitstempel aus dem Jahr
    :return: Daten, die von dem "mitarbeiter_jahresstunden_uebersicht.html"-Template benötigt werden
    """

    monate_uebersicht = []
    for monats_nr in range(1, 13):
        gesamt = 0  # Gesamt stunden die gearbeitet wurden

        for z in zeitstempel:
            if z.eingestempelt.month == monats_nr:
                # Berechnung der Stunden, die in dem Monat gearbeitet wurden
                if hasattr(z, "ausgestempelt") and (z.ausgestempelt is not None):
                    differenz = z.ausgestempelt - z.eingestempelt
                    gesamt += differenz.seconds / 60 / 60

        soll_stunden = berechne_anzahl_arbeitstage_fuer_monat(31, monats_nr, year) * (user.stunden_pro_woche / 5)

        # Abspeichern der Daten, um sie an das Template weiter zu geben
        monate_uebersicht.append(
            {
                "name": month_to_string[monats_nr - 1],
                "gesamt": round(gesamt, 1),
                "soll": round(soll_stunden, 1),
                "saldo": round(gesamt - soll_stunden, 1)
            }
        )

    return monate_uebersicht


@meine_statistiken_ap6.route('/mein_stundensaldo')
@role_req("Mitarbeiter" , "Personalsachbearbeiter")
def mein_stundensaldo():
    """
    Endpoint, an dem das Stundensaldo, das Arbeitstagesaldo und das Urlaubsaldo des
    aktuell eingeloggten Users angezeigt wird

    :return: Die Daten die benötigt werden, um die mein_stundensaldo Ansicht zu bauen
    """

    # Mitarbeiter Daten abfragen
    mitarbeiter = current_user

    # Berechnungen der aktuellen Sollstunden diesen Jahres bis zum aktuellen Monat
    return zeige_stundensaldo_von_mitarbeiter(mitarbeiter, datetime.datetime.now().year, False)


# Hilfsfunktionen für Stundensaldo Ansicht

def zeige_stundensaldo_von_mitarbeiter(mitarbeiter, jahr, show_name):
    """
    Diese Funktion rendert ein Template, um das Stundensaldo, Arbeitssaldo und Urlaubsaldo
    eines beliebigen Mitarbeiter anzuzeigen

    :param mitarbeiter: Mitarbeiter Model des gewünschten Mitarbeiters
    :return: Gerendertes Template und Status Code
    """

    if jahr == datetime.datetime.today().year:
        monat = datetime.datetime.today().month
    else:
        monat = 12

    arbeitstage, saldo = erstelle_stundensaldo_und_arbeitstage_daten(monat, jahr, mitarbeiter)
    urlaub = erstelle_urlaub_daten(jahr, mitarbeiter)
    # Auszählung der Anzahl der Fehltage
    anzahl_fehltage = len(mitarbeiter.fehlzeiten)


    return render_template(
        "mitarbeiter_stundensaldo.html",
        saldo=saldo,
        urlaub=urlaub,
        arbeitstage=arbeitstage,
        anzahl_fehltage=anzahl_fehltage,
        name=mitarbeiter.vorname + " " + mitarbeiter.nachname,
        show_name=show_name,
        username=mitarbeiter.username,
        now_year=datetime.datetime.now().year,
        min_year=get_erstes_jahr_des_einstempelns(mitarbeiter),
        year=jahr
    )


def erstelle_stundensaldo_und_arbeitstage_daten(monat, jahr, mitarbeiter):
    """
    Diese Funktion erstellt das Stundensaldo und die Arbeitstage Daten, die vom "mitarbeiter_stundensaldo.html"
    Template erwartet werden

    :param monat: Bis zu welchem Monat das Stundensaldo und die Arbeitstage ausgewertet werden sollen
    :param jahr: Jahr, dessen Stundensaldo und Arbeitstage ausgewertet werden sollen
    :param mitarbeiter: Mitarbeiter Model, dessen Stundensaldo und Arbeitstage ausgewertet werden sollen
    :return: Arbeitstage und Saldo Dictionairy mit den Daten, welche das "mitarbeiter_stundensaldo.html"
            Template benötigt
    """
    # Soll stunden und offene Arbeitstage berechnen bis zum aktuellen Tag für dieses Jahr
    soll_stunden, arbeitstage_offen = \
        berechne_sollstunden_und_arbeitstage(monat, jahr, mitarbeiter.stunden_pro_woche)
    zeitstempel_dieses_jahr = get_zeitstempel_von_jahr(jahr, mitarbeiter)

    # Berechnung der erfassten stundensaldo
    arbeitstage_erfasst, stundensaldo_erfasst = \
        berechne_erfasste_stunden_und_arbeitstage(zeitstempel_dieses_jahr)

    # Berechnung des Stundensaldo
    stundensaldo = stundensaldo_erfasst - soll_stunden

    # Berechnung der offenen Arbeitstage
    arbeitstage_saldo = arbeitstage_erfasst - arbeitstage_offen

    # Erstellen der Saldostunden Daten, die ans Template weitergegeben werden sollen
    saldo = {
        "offen": round(soll_stunden, 1),
        "erfasst": round(stundensaldo_erfasst, 1),
        "saldo": round(stundensaldo, 1)
    }

    # Erstellung der Arbeitstage Daten, die ans Template weitergegeben werden sollen
    arbeitstage = {
        "offen": arbeitstage_offen,
        "erfasst": arbeitstage_erfasst,
        "saldo": arbeitstage_saldo
    }

    return arbeitstage, saldo


def erstelle_urlaub_daten(jahr, mitarbeiter):
    """
    Diese Funktion erstellt die Daten, die an das Template so weitergegeben werden müssen,
    um Informationen über die Urlaubstage anzuzeigen

    :param jahr: Jahr, aus welchem die Urlaubstage ausgewertet werden sollen
    :param mitarbeiter: Mitarbeiter Model des Mitarbeiters, dessen Urlaubstage ausgewertet werden sollen
    :return: Dictionairy, so wie es das Template "mitarbeiter_stundensaldo.html" erwartet
    """
    # Herausfinden wie viele Urlaubstage genommen wurden
    urlaub_genommen = get_anzahl_genommer_urlaub(jahr, mitarbeiter)

    # Herausfinden, wie viel Urlaub der Mitarbeiter pro Jahr hat
    urlaub_gesamt = mitarbeiter.urlaubstage

    # Berechnung des Resturlaubs
    urlaub_rest = urlaub_gesamt - urlaub_genommen

    # Erstellung der Urlaub Daten, die ans Template weitergegeben werden sollen
    urlaub = {
        "gesamt": urlaub_gesamt,
        "genommen": urlaub_genommen,
        "rest": urlaub_rest
    }

    return urlaub


def berechne_sollstunden_und_arbeitstage(monat, jahr, wochenstunden):
    """
    Diese Funktion berechnet die Sollstunden und die Arbeitstage, die ein Jahr bis zum angegebenen Monat hat

    :param monat: Monat bis wann die Arbeitstage/Sollstunden berechnet werden sollen
    :param jahr: Jahr in dem die Arbeitstage/Sollstunden berechnet werden soll
    :param wochenstunden: Anzahl der Stunden, die ein Mitarbeiter arbeitet
    :return: Tupel, mit Sollstunden und Anzahl der Arbeitstage
    """

    arbeitstage_offen = 0

    for i in range(1, monat + 1):
        tage = 31
        if i == monat:
            # Wird benötigt damit die berechnung der offenen Arbeitstage nur bis zum aktuellen Tag geht
            # und nicht bis zum Ende des aktuellen Monats
            tage = datetime.datetime.today().day

        arbeitstage_offen += berechne_anzahl_arbeitstage_fuer_monat(tage, i, jahr)

    soll_stunden = arbeitstage_offen * (wochenstunden / 5)

    return soll_stunden, arbeitstage_offen


def berechne_anzahl_arbeitstage_fuer_monat(tag, monat, jahr):
    """
    Diese Funktion berechnet die Anzahl der Arbeitstage für einen angegebenen Monat

    :param tag: Tag bis zu welchem, die Arbeitstage berechnet werden soll. Falls der Tag >= 31, dann werden auf jeden
                Fall alle Arbeitstage in diesem Monat berechnet unabhängig von der tatsächlichen Anzahl der Tage in dem
                Monat (Ja, das ist leider nicht allzu schön gelöst)
    :param monat: Monat für den die Anzahl der Arbeitstage berechnet werden soll. Sollte zwischen 1 und 12 sein
    :param jahr: Jahr des Monats für den die Anzahl der Arbeitstage berechnet werden soll
    :return: Anzahl der Arbeitstage für den Monat
    """

    datum = datetime.datetime(year=jahr, month=monat, day=1)

    anzahl_arbeitstage = 0
    for i in range(tag+1):
        if datum.weekday() >= 0 and datum.weekday() <= 4:
            # Es wird davon ausgegangen, dass nur von einschließlich Montag
            # bis einschließlich Freitag gearbeitet wird
            anzahl_arbeitstage += 1

        datum += datetime.timedelta(days=1)

        if datum.month != monat:
            # Wird benötigt, falls für Parameter "tag" ein größerer Wert angegeben wurde,
            # als dieser Monat Tage hat
            break

    return anzahl_arbeitstage


def get_zeitstempel_von_jahr(jahr, mitarbeiter):
    """
    Durchsucht alle Zeitstempel des Mitarbeiters und gibt die zurück, welche aus dem angegebenen Jahr sind.
    Zudem werden die Zeitstempel in aufsteigender Datums-Reihenfolge sortiert.

    :param jahr: Wunschjahr der Zeitstempel
    :param mitarbeiter: Mitarbeiter model
    :return: Alle Zeitstempel des angegebenen Jahres in aufsteigender Reihenfolge, sortiert nach dem Datumu
    """

    # Zeitstempel vom aktuellen Jahr rausfiltern
    zeitstempel_dieses_jahr = []
    for t in mitarbeiter.zeitstempel:
        eingestempelt_jahr = t.eingestempelt.year

        if eingestempelt_jahr == jahr:
            # Zeitstempel diesen Jahres zwischenspeichern
            zeitstempel_dieses_jahr.append(t)

    # Zeitstempel sortieren, da sie in der Datenbank unsortiert sein können
    zeitstempel_dieses_jahr = sorted(zeitstempel_dieses_jahr,
                                     key=lambda z: z.eingestempelt.month)

    return zeitstempel_dieses_jahr


def berechne_erfasste_stunden_und_arbeitstage(zeitstempel_dieses_jahr):
    """
    Berechnet die erfassten gearbeiteten Stunden und Arbeitstage

    :param zeitstempel_dieses_jahr: Zeitstempel aus diesem Jahr
    :return: Tupel aus erfassten Arbeitstagen und den abgearbeiteten Stunden
    """

    stunden_erfasst = 0
    arbeitstage_erfasst = 0

    for zeitstempel in zeitstempel_dieses_jahr:
        arbeitstage_erfasst += 1  # Mitzählen der erfassten Arbeitstage

        # Berechnung der erfassten Stunden
        if hasattr(zeitstempel, "ausgestempelt") and (zeitstempel.ausgestempelt is not None):
            diff = zeitstempel.ausgestempelt - zeitstempel.eingestempelt
            stunden_erfasst += diff.seconds / 60 / 60

    return arbeitstage_erfasst, stunden_erfasst


def get_anzahl_genommer_urlaub(jahr, mitarbeiter):
    """
    Gibt die Anzahl der genommenen Urlaubstage eines bestimmten Mitarbeiters zurück

    :param jahr: Gewünschtes Jahr an dem die genommenen Urlaubstage berechnet werden soll
    :param mitarbeiter: Mitarbeiter Model, des Mitarbeiters, dessen genommer Urlaub zurück gegeben werden soll
    :return: Anzahl der genommenen Urlaubstage
    """

    urlaub_genommen = 0

    for fehlzeit in mitarbeiter.fehlzeiten:
        if (fehlzeit.grund == "Urlaub") and (fehlzeit.datum_start.year == jahr):
            # Tage berechnen, wenn Urlaub aus gegebenen Jahr
            tage = fehlzeit.datum_ende - fehlzeit.datum_start
            tage = tage.days
            urlaub_genommen += tage

    return urlaub_genommen

def get_erstes_jahr_des_einstempelns(mitarbeiter):
    min_jahr = datetime.datetime.now().year

    for zeitstempel in mitarbeiter.zeitstempel:
        eingestempelt_jahr = zeitstempel.eingestempelt.year
        min_jahr = min(eingestempelt_jahr, min_jahr)

    return min_jahr

