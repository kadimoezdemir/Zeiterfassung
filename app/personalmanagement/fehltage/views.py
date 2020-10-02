from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_required
from app.main.forms import role_req
from app.models.models import Mitarbeiter, Fehlzeit
from app.personalmanagement.fehltage.forms import FehlzeitForm, FilterForm
from app.personalmanagement.mitarbeiter.views import funktionen_eintragen


# define the blueprint
fehltage = Blueprint('fehltage', __name__, template_folder='pages')

# global variables
# speichert die aktuellen Fehlzeitergebnisse einer Filtersuchmaske
filter_ergebnisse = None
# gibt an ob die Fehlzeit-Uebersicht verlassen wurde
sitechange = None
# speichert die aktuellen Filtereingaben
current_filter = None

# all routes
@fehltage.route('/home')
@role_req("Personalsachbearbeiter")
def home():
    # setzt filter_ergebnisse zurück
    global filter_ergebnisse
    filter_ergebnisse = None

    # Auswählbare Funktion(en) für Mitarbeitersuche festlegen
    f = [
        {
            "route": "fehltage.uebersicht",
            "label": "Auswählen"
        }
    ]
    return redirect(url_for("mitarbeiter.suchen", funktionen=funktionen_eintragen(f)))


@fehltage.route('/uebersicht/<username>', defaults={'sortiere_absteigend': 'true', 'filtern': 'false'}, methods=["GET", "POST"])
@fehltage.route('/uebersicht/<username>/<sortiere_absteigend>/<filtern>', methods=["GET", "POST"])
@role_req("Personalsachbearbeiter")
def uebersicht(username=None, sortiere_absteigend=None, filtern=None):
    if username and sortiere_absteigend and filtern is not None:
        global sitechange
        global filter_ergebnisse
        global current_filter

        # gibt an welcher Filter-Zeitraum gewählt wurde
        filter_wahl = None
        # gibt an welche Checkboxes ausgewählt sind,
        # um die Daten im uebersicht.html dem entsprechend verarbeiten zu können
        checkboxes = {
            "erkrankung": "none",
            "home_office": "none",
            "urlaub": "none",
            "zeitausgleich": "none",
        }

        # suche den aktuell gewählten Mitarbeiter mithilfe des username
        mitarbeiter = Mitarbeiter.objects(username=username).first()
        if mitarbeiter is not None:
            # wähle alle zugehörigen Fehlzeiten des Mitarbeiters
            fehlzeiten = mitarbeiter.fehlzeiten.filter()
        else:
            flash("Kein Mitarbeiter gefunden", "danger")
            return redirect(url_for("main.home"))

        if sitechange is None:
            sitechange = False
        elif sitechange is True:
            # Wenn die Seite verlassen wurde die gefilterten Ergebnisse verwerfen und
            # alle (zuvor gefilterten) Fehlzeiten des Mitarbeiters anzeigen
            filter_ergebnisse = fehlzeiten
            sitechange = False

        if filter_ergebnisse is None:
            filter_ergebnisse = fehlzeiten

        form = FilterForm()

        # Wenn das Filter-Formular geöffnet wurde (URL parameter filtern == 'true')
        if filtern == 'true':
            # prüfe Gültikeit der Filtereingaben
            if form.validiere_filter():
                # speichere die Filterergebnisse
                filter_ergebnisse = form.use_filter(fehlzeiten)
                # speichere die getätigten Filtereingaben
                current_filter = form
                # zeige Filter-Formular nicht mehr an
                filtern = 'false'
                return render_template("uebersicht.html", mitarbeiter=mitarbeiter, fehlzeiten=filter_ergebnisse,
                                       sortiere_absteigend=sortiere_absteigend, filtern=filtern, form=form, info=session)

            # bei ungültiger Eingabe, Fehlermeldung je nach Auswahl anzeigen
            elif form.radio.data is not None:
                if form.radio.data == 'tag':
                    flash("Sie müssen ein Datum angeben", "danger")
                elif form.radio.data == 'woche':
                    flash("Sie müssen entweder ein Datum oder eine Kalenderwoche und ein Jahr angeben", "danger")
                elif form.radio.data == 'beliebig':
                    if form.datum_start.data and form.datum_ende.data is not None:
                        flash("Der angegebene Zeitraum ist ungültig", "danger")
                    else:
                        flash("Sie müssen ein Start- und Enddatum angeben", "danger")
                # gewählter Radiobutton und Checkboxes speichern
                filter_wahl = form.radio.data
                checkboxes = {
                    "erkrankung": form.erkrankung.data,
                    "home_office": form.home_office.data,
                    "urlaub": form.urlaub.data,
                    "zeitausgleich": form.zeitausgleich.data,
                }

            # beim Öffnen die aktuellen Filtereinstellungen im Filter-Formular anzeigen, sofern vorhanden
            else:
                if current_filter is not None:
                    form = current_filter
                    filter_wahl = form.radio.data
                    checkboxes = {
                        "erkrankung": form.erkrankung.data,
                        "home_office": form.home_office.data,
                        "urlaub": form.urlaub.data,
                        "zeitausgleich": form.zeitausgleich.data,
                    }

            return render_template("uebersicht.html", mitarbeiter=mitarbeiter, fehlzeiten=filter_ergebnisse,
                                   filter_wahl=filter_wahl,
                                   checkboxes=checkboxes, sortiere_absteigend=sortiere_absteigend, filtern=filtern,
                                   form=form, info=session)

        return render_template("uebersicht.html", mitarbeiter=mitarbeiter, fehlzeiten=filter_ergebnisse, filter_wahl=filter_wahl,
                               checkboxes=checkboxes, sortiere_absteigend=sortiere_absteigend, filtern=filtern, form=form, info=session)

    else:
        flash("Kein Mitarbeiter angegeben", "danger")
        return redirect(url_for("main.home"))


@fehltage.route('/bearbeiten/<username>/<fehlzeit_id>', methods=["GET", "POST"])
@role_req("Personalsachbearbeiter")
def bearbeiten(username=None, fehlzeit_id=None):
    if username and fehlzeit_id is not None:
        global sitechange
        # speichern, dass die Übersichtseite verlassen wurde
        sitechange = True

        # suche den aktuellen Mitarbeiter und die gewählte Fehlzeit anhand der übergebenen URL parameter
        mitarbeiter = Mitarbeiter.objects(username=username).first()
        fehlzeit = mitarbeiter.fehlzeiten.filter(id=fehlzeit_id).first()

        form = FehlzeitForm()

        if form.validate_on_submit():
            # übernehme Änderungen
            fehlzeit.fill(form)
            # prüfe ob der angegebene Zeitraum gültig ist
            validate_fehlzeit = mitarbeiter.validate_fehlzeit(fehlzeit)

            if validate_fehlzeit == 'valid':
                mitarbeiter.save()
                flash("Fehlzeit erfolgreich bearbeitet", "success")
                return redirect(url_for("fehltage.uebersicht", username=username))

            elif validate_fehlzeit == 'occupied':
                flash("Es existiert bereits ein Eintrag in diesem Zeitrahmen", "danger")
                return render_template("fz_bearbeiten.html", form=form, mitarbeiter=mitarbeiter, fehlzeit_id=fehlzeit.id, info=session)

            elif validate_fehlzeit == 'time_frame':
                flash("Der gewählte Zeitrahmen ist ungültig", "danger")
                return render_template("fz_bearbeiten.html", form=form, mitarbeiter=mitarbeiter, fehlzeit_id=fehlzeit.id, info=session)

        # trage die bestehenden Fehlzeitdaten in das Formular ein
        form.fill(fehlzeit)
        return render_template("fz_bearbeiten.html", form=form, mitarbeiter=mitarbeiter, fehlzeit_id=fehlzeit.id, info=session)

    flash("Username oder Fehlzeit ID nicht vorhanden", "danger")
    return redirect(url_for("main.home", username=username))


@fehltage.route('/eintragen/<username>', methods=["GET", "POST"])
@role_req("Personalsachbearbeiter")
def eintragen(username=None):
    if username is not None:
        global sitechange
        # speichern, dass die Übersichtseite verlassen wurde
        sitechange = True

        fehlzeit = Fehlzeit()
        # suche den aktuellen Mitarbeiter anhand des übergebenen URL parameters
        mitarbeiter = Mitarbeiter.objects(username=username).first()

        form = FehlzeitForm()
        if form.validate_on_submit():
            # übernehme Eingaben
            fehlzeit.fill(form)
            # prüfe ob der angegebene Zeitraum gültig ist
            validate_fehlzeit = mitarbeiter.validate_fehlzeit(fehlzeit)

            if validate_fehlzeit == 'valid':
                # speichere die neue Fehlzeit bei dem zugehörigen Mitarbeiter
                mitarbeiter.fehlzeiten.append(fehlzeit)
                mitarbeiter.save()
                flash("Fehlzeit erfolgreich angelegt", "success")
                return redirect(url_for("fehltage.uebersicht", username=username))

            elif validate_fehlzeit == 'occupied':
                flash("Es existiert bereits ein Eintrag in diesem Zeitrahmen", "danger")
                return render_template("eintragen.html", form=form, mitarbeiter=mitarbeiter, info=session)

            elif validate_fehlzeit == 'time_frame':
                flash("Der gewählte Zeitrahmen ist ungültig", "danger")
                return render_template("eintragen.html", form=form, mitarbeiter=mitarbeiter, info=session)

        mitarbeiter.set_fehlzeit_id(fehlzeit)
        # fülle die Fehlzeit ID automatisch und versteckt aus
        form.id.data = fehlzeit.id
        return render_template("eintragen.html", form=form, mitarbeiter=mitarbeiter, info=session)

    flash("Username nicht vorhanden", "danger")
    return redirect(url_for("main.home", username=username))


@fehltage.route('/loeschen/<username>/<fehlzeit_id>', methods=["GET", "POST"])
@role_req("Personalsachbearbeiter")
def loeschen(username=None, fehlzeit_id=None):
    if username and fehlzeit_id is not None:
        global sitechange
        # speichern, dass die Übersichtseite verlassen wurde
        sitechange = True

        # suche den aktuellen Mitarbeiter und die gewählte Fehlzeit anhand der übergebenen URL parameter
        mitarbeiter = Mitarbeiter.objects(username=username).first()
        fehlzeit = mitarbeiter.fehlzeiten.filter(id=fehlzeit_id).first()

        # entferne die gewählte Fehlzeit und speichere die Änderung
        mitarbeiter.fehlzeiten.remove(fehlzeit)
        mitarbeiter.save()

        flash("Fehlzeit erfolgreich gelöscht", "success")
        return redirect(url_for("fehltage.uebersicht", username=username))

    flash("Username oder Fehlzeit ID nicht vorhanden", "danger")
    return redirect(url_for("fehltage.uebersicht", username=username))
