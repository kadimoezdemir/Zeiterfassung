from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models.models import Mitarbeiter
from .forms import MitarbeiterForm, MitarbeiterSuchen, MitarbeiterBearbeitenForm, MitarbeiterAktivierenForm, \
    MitarbeiterDeaktivierenForm
import json
from app.main.forms import role_req


mitarbeiter = Blueprint('mitarbeiter', __name__, template_folder='pages')


# Seite zum Anlegen eines neuen Mitarbeiters
@mitarbeiter.route('/neu', methods=["GET", "POST"])
@role_req("Personalsachbearbeiter")
def neu():
    form = MitarbeiterForm()
    # Eingabeformular anzeigen, falls die initiale GET-Anfrage gesendet wird,
    # noch fehlerhafte Eingaben existieren bzw. nicht alle Felder ausgefüllt sind
    if not form.validate_on_submit():
        return render_template("neu.html", form=form, info=session)
    # Mitarbeiter erstellen und zur Startseite weiterleiten, falls alle Eingaben in Ordnung
    else:
        # Neues Mitarbeiterobjekt anlegen und mit den Formulardaten initialisieren
        ma = Mitarbeiter()
        ma.fill(form)
        ma.set_password(form.passwort.data)
        # Erstellten Mitarbeiter persistent speichern
        ma.save()
        flash(f"Mitarbeiter {form.username.data} erfolgreich angelegt", "success")
        return redirect(url_for('main.home'))


# Stammdaten-Menü, von dem aus zu Mitarbeiter Bearbeiten/Aktivieren/Deaktivieren navigiert werden kann
# Leitet zur Mitarbeitersuche weiter und stellt dort die Navigationslinks zur Verfügung
@mitarbeiter.route('/stammdaten')
@role_req("Personalsachbearbeiter")
def stammdaten():
    # Navigationslinks, die zu jedem Mitarbeiter zur Verfügung gestellt werden
    links = [
        {
            "route": "mitarbeiter.aktivieren",
            "label": "Aktivieren"
        },
        {
            "route": "mitarbeiter.deaktivieren",
            "label": "Deaktivieren"
        },
        {
            "route": "mitarbeiter.bearbeiten",
            "label": "Bearbeiten"
        }
    ]
    return redirect(url_for("mitarbeiter.suchen", funktionen=funktionen_eintragen(links)))


# Seite zum Bearbeiten eines bestehenden Mitarbeiters
@mitarbeiter.route('/bearbeiten/<username>', methods=["GET", "POST"])
@role_req("Personalsachbearbeiter")
def bearbeiten(username=None):
    # Sicherstellen, dass mit der URL ein Mitarbeitername übergeben wurde
    if username:
        # Den per URL angeforderten Mitarbeiter aus der Datenbank laden
        ma = Mitarbeiter.objects(username=username).first()
        # Sicherstellen, dass der angeforderte Mitarbeiter existiert und kein
        # nicht vergebener Username übergeben wurde
        if ma is None:
            flash("Der Mitarbeiter, den Sie bearbeiten wollen, existiert nicht", "danger")
            return redirect(url_for("main.home"))
        # Bearbeitungsformular initialisieren
        form = MitarbeiterBearbeitenForm()
        # Erste GET-Anfrage oder falsch/unvollständig ausgefülltes Formular
        # -> Preset-Daten aus dem Mitarbeiterobjekt ins Formular eintragen und dieses rendern
        if not form.validate_on_submit():
            form.fill(ma)
            return render_template("bearbeiten.html", form=form, info=session, ma=ma)
        # POST-Anfrage und korrekt ausgefülltes Formular
        # -> Mitarbeiterobjekt mit Formulardaten aktualisieren und persistent speichern
        else:
            username = ma.username
            aktiv = ma.aktiv
            ma.fill(form)
            ma.username = username
            ma.aktiv = aktiv
            if form.passwort.data != "":
                ma.set_password(form.passwort.data)
            ma.save()
            flash("Mitarbeiterdaten erfolgreich geändert", "success")
            return redirect(url_for("main.home"))
    else:
        flash("Kein Username angegeben", "danger")
        return redirect(url_for("main.home"))


# Bestätigungsdialog zum Reaktivieren eines Mitarbeiters
@mitarbeiter.route('/aktivieren/<username>', methods=["GET", "POST"])
@role_req("Personalsachbearbeiter")
def aktivieren(username=None):
    # Sicherstellen, dass ein Username übergeben wurde
    if username:
        # Den per URL angeforderten Mitarbeiter aus der Datenbank laden
        ma = Mitarbeiter.objects(username=username).first()
        # Sicherstellen, dass der angeforderte Mitarbeiter existiert und kein
        # nicht vergebener Username übergeben wurde
        if ma is None:
            flash("Der Mitarbeiter, den Sie aktivieren wollen, existiert nicht", "danger")
            return redirect(url_for("main.home"))
        form = MitarbeiterAktivierenForm()
        # Reaktion auf "Bestätigen"-POST-Anfrage -> Status des Mitarbeiters persistent auf aktiv setzen
        if form.validate_on_submit():
            ma.aktivieren()
            ma.save()
            flash(f"Mitarbeiter {username} aktiviert", "success")
        # Unzulässige Anfrage -> sollte nie auftreten, da das Formular nur einen einzigen Button enthält
        else:
            return render_template("aktivieren.html", info=session, ma=ma, form=form)
    else:
        flash("Kein Mitarbeiter angegeben", "danger")
    # Weiterleitung auf Startseite unabhängig von Bestätigung/Abbruch des Vorgangs
    return redirect(url_for('main.home'))


# Bestätigungsdialog zum Deaktivieren eines Mitarbeiters
@mitarbeiter.route('/deaktivieren/<username>', methods=["GET", "POST"])
@role_req("Personalsachbearbeiter")
def deaktivieren(username=None):
    # Sicherstellen, dass ein Username übergeben wurde
    if username:
        # Den per URL angeforderten Mitarbeiter aus der Datenbank laden
        ma = Mitarbeiter.objects(username=username).first()
        # Sicherstellen, dass der angeforderte Mitarbeiter existiert und kein
        # nicht vergebener Username übergeben wurde
        if ma is None:
            flash("Der Mitarbeiter, den Sie deaktivieren wollen, existiert nicht", "danger")
            return redirect(url_for("main.home"))
        form = MitarbeiterDeaktivierenForm()
        # Reaktion auf "Bestätigen"-POST-Anfrage -> Status des Mitarbeiters persistent auf inaktiv setzen
        if form.validate_on_submit():
            ma.deaktivieren()
            ma.save()
            flash(f"Mitarbeiter {username} deaktiviert", "success")
        # Unzulässige Anfrage -> sollte nie auftreten, da das Formular nur einen einzigen Button enthält
        else:
            return render_template("deaktivieren.html", info=session, ma=ma, form=form)
    else:
        flash("Kein Mitarbeiter angegeben", "danger")
    # Weiterleitung auf Startseite unabhängig von Bestätigung/Abbruch des Vorgangs
    return redirect(url_for('main.home'))


# Mitarbeitersuche: Wird von anderen Use Cases verwendet und jeweils mit einer Liste von Menüpunkten in Form von
# Links parametrisiert (einzutragen mit Hilfe der Funktion funktionen_eintragen), die für jedes Suchergebnis zur
# Verfügung gestellt werden sollen
@mitarbeiter.route('/suchen', methods=["GET", "POST"])
@role_req("Personalsachbearbeiter")
def suchen():
    # Übergebene Links für die Suchergebnisse aus der URL auslesen
    funktionen = json.loads(request.args.get("funktionen"))["funktionen"]
    form = MitarbeiterSuchen()
    if form.validate_on_submit():
        # Alle Mitarbeiter aus der Datenbank suchen, zu denen die Anfrage passt
        ma = Mitarbeiter.suchen(form.suche.data)
        if ma.first() is None:
            flash("Kein Mitarbeiter zu Ihrer Suche gefunden", "danger")
        else:
            # Suchergebnisse rendern und letzte Suchanfrage als Preset ins Suchfeld eintragen
            return render_template(
                "suche.html", ma=ma, info=session, funktionen=funktionen,
                form=form, letzte_suche=form.suche.data)
    # Noch keine Suchanfrage bzw. letzte Suche hat kein Ergebnis geliefert
    # -> mit leerem Suchfeld und leerer Ergebnisliste rendern
    return render_template("suche.html", ma=[], info=session, funktionen=funktionen, form=form, letzte_suche="")


# wandelt eine Liste von Dictionaries mit den Keys "route" und "label" in einen JSON-String um,
# der beim Redirect auf die Mitarbeitersuche als Parameter "funktionen" übergeben werden muss
# Der JSON-String wird im HTML-Template geparsed und in entsprechende Links umgesetzt
def funktionen_eintragen(f: list):
    f2 = {
        "funktionen": f
    }
    return json.dumps(f2)
