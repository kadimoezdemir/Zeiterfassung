import pytest
from app.models.models import Mitarbeiter
from app.personalmanagement.mitarbeiter.views import funktionen_eintragen
import json


# Login-Hack in Funktion verpackt
def set_user(app, username):
    user = Mitarbeiter.objects(username=username).first()

    @app.login_manager.request_loader
    def load_user_from_request(request):
        return user


# Legt einen Mitarbeiter mit username "ulrich25" in der Datenbank an, mit dem App-Funktionen
# reproduzierbar getestet werden können
def create_ulrich25():
    Mitarbeiter.objects(username="ulrich25").delete()
    ulrich25 = Mitarbeiter()
    ulrich25.nachname = "Hardmann"
    ulrich25.vorname = "Ulrich"
    ulrich25.username = "ulrich25"
    ulrich25.set_password("test")
    ulrich25.rolle = "Mitarbeiter"
    ulrich25.aktiv = True
    ulrich25.gebdat = "1989-04-04"
    ulrich25.geschlecht = "transmännlich"
    ulrich25.email = "uli25@web.de"
    ulrich25.telefon = "123456789"
    ulrich25.adresse_plz = "87700"
    ulrich25.adresse_ort = "Memmingen"
    ulrich25.adresse_strasse = "Amselweg"
    ulrich25.adresse_hausnr = "5"
    ulrich25.stunden_pro_woche = 40
    ulrich25.urlaubstage = 25
    ulrich25.save()


# Testklasse für Arbeitspaket 1 (Stammdatenverwaltung)
@pytest.mark.usefixtures("client", "app")
class TestAP1:
    # Testet, ob die funktionen_eintragen() Funktion eine übergebene Liste korrekt erweitert und in JSON umwandelt
    def test_funktionen_eintragen(self, client, app):
        links = [
            {
                "route": "mitarbeiter.aktivieren",
                "label": "Aktivieren"
            },
            {
                "route": "mitarbeiter.deaktivieren",
                "label": "Deaktivieren"
            }
        ]
        expected_result = "{\"funktionen\":[{\"route\":\"mitarbeiter.aktivieren\",\"label\":\"Aktivieren\"}," \
                          "{\"route\":\"mitarbeiter.deaktivieren\",\"label\":\"Deaktivieren\"}]}"
        result = funktionen_eintragen(links)
        # Umweg load -> dump, damit Leerzeichen etc. in beiden Ergebnisstrings gleich positioniert sind
        assert json.dumps(json.loads(result)) == json.dumps(json.loads(expected_result))

    ###############################################################
    # UC 1.1 Mitarbeiter anlegen
    ###############################################################

    # Testet, ob die "Neuer Mitarbeiter"-Seite ohne Login erreichbar ist
    # -> muss auf die Login-Seite weiterleiten und "Sie sind nicht eingeloggt" flashen
    def test_mitarbeiter_neu_erreichbar_ohne_login(self, client, app):
        rv = client.get('/mitarbeiter/neu', follow_redirects=True)
        assert rv.status_code == 200
        assert ("Sie sind nicht eingeloggt" in str(rv.data))

    # Testet, ob die "Neuer Mitarbeiter"-Seite als Personalsachbearbeiter erreichbar ist
    # -> muss das "Neuer Mitarbeiter"-Formular anzeigen
    def test_mitarbeiter_neu_erreichbar_als_personalsachbearbeiter(self, client, app):
        set_user(app, "personalsachbearbeiter")
        rv = client.get('/mitarbeiter/neu', follow_redirects=True)
        assert rv.status_code == 200
        assert ("Mitarbeiter anlegen" in str(rv.data))

    # Testet, ob die "Neuer Mitarbeiter"-Seite als Mitarbeiter erreichbar ist
    # -> muss das auf die Startseite weiterleiten und auf die fehlende Autorisierung hinweisen
    def test_mitarbeiter_neu_erreichbar_als_mitarbeiter(self, client, app):
        set_user(app, "mitarbeiter")
        rv = client.get('/mitarbeiter/neu', follow_redirects=True)
        assert rv.status_code == 200
        assert ("Sie sind nicht autorisiert, die Seite zu sehen." in str(rv.data))

    # Testet, ob ein neuer Mitarbeiter mit korrektem Input angelegt werden kann
    # -> das System muss auf die Startseite weiterleiten und eine Erfolgsmeldung ausgeben
    # -> der Mitarbeiter muss in der Datenbank vorhanden sein (d.h. ausgelesen werden können)
    def test_mitarbeiter_neu_anlegen_korrekter_input(self, client, app):
        Mitarbeiter.objects(username="ulrich25").delete()
        set_user(app, "personalsachbearbeiter")
        form_input = {
            "vorname": "Ulrich",
            "nachname": "Hardmann",
            "username": "ulrich25",
            "passwort": "test",
            "passwort_wiederholen": "test",
            "rolle": "Mitarbeiter",
            "gebdat": "1989-04-04",
            "geschlecht": "transmännlich",
            "email": "uli25@web.de",
            "telefon": "123456789",
            "adresse_plz": "87700",
            "adresse_ort": "Memmingen",
            "adresse_strasse": "Amselweg",
            "adresse_hausnr": "5",
            "stunden_pro_woche": "40",
            "urlaubstage_pro_jahr": "25"
        }
        rv = client.post('/mitarbeiter/neu', data=form_input, follow_redirects=True)
        assert rv.status_code == 200
        assert ("Mitarbeiter ulrich25 erfolgreich angelegt" in str(rv.data))
        assert Mitarbeiter.objects(username="ulrich25").first() is not None
        Mitarbeiter.objects(username="ulrich25").delete()

    # Testet, ob das Anlegen eines neuen Mitarbeiters mit invalidem Input möglich ist
    # -> das System muss das Anlegen verweigern und Fehlermeldungen für die inkorrekten Felder anzeigen
    def test_mitarbeiter_neu_anlegen_inkorrekter_input(self, client, app):
        Mitarbeiter.objects(username="ulrich25").delete()
        set_user(app, "personalsachbearbeiter")
        form_input = {
            "vorname": "Ulrich",
            "nachname": "Hardmann",
            "username": "ulrich25",
            "passwort": "test",
            "passwort_wiederholen": "pimmel",
            "rolle": "Mitarbeiter",
            "gebdat": "1989-04-04",
            "geschlecht": "transmännlich",
            "email": "test",
            "telefon": "123456789",
            "adresse_plz": "87700",
            "adresse_ort": "Memmingen",
            "adresse_strasse": "Amselweg",
            "adresse_hausnr": "5",
            "stunden_pro_woche": "asdfg",
            "urlaubstage_pro_jahr": "25"
        }
        rv = client.post('/mitarbeiter/neu', data=form_input, follow_redirects=True)
        assert rv.status_code == 200
        assert ("Invalid email address" in str(rv.data))
        assert Mitarbeiter.objects(username="ulrich25").first() is None
        Mitarbeiter.objects(username="ulrich25").delete()

    ###############################################################
    # UC 1.2 Mitarbeiter suchen
    ###############################################################

    # Testet, ob die Mitarbeitersuche ohne Login erreichbar ist
    # -> muss auf die Login-Seite weiterleiten und "Sie sind nicht eingeloggt" flashen
    def test_mitarbeitersuche_erreichbar_ohne_login(self, client, app):
        rv = client.get('/mitarbeiter/suchen?funktionen=%7B%22funktionen%22%3A+%5B%7B%22route%22%3A+%22'
                        'mitarbeiter.aktivieren%22%2C+%22label%22%3A+%22Aktivieren%22%7D%2C+%7B%22route%22%3A+%22'
                        'mitarbeiter.deaktivieren%22%2C+%22label%22%3A+%22Deaktivieren%22%7D%2C+%7B%22'
                        'route%22%3A+%22mitarbeiter.bearbeiten%22%2C+%22label%22%3A+%22Bearbeiten%22%7D%5D%7D',
                        follow_redirects=True)
        assert rv.status_code == 200
        assert ("Sie sind nicht eingeloggt" in str(rv.data))

    # Testet, ob die Mitarbeitersuche als Personalsachbearbeiter erreichbar ist
    # -> muss das "Mitarbeiter suchen"-Formular anzeigen
    def test_mitarbeitersuche_erreichbar_als_personalsachbearbeiter(self, client, app):
        set_user(app, "personalsachbearbeiter")
        rv = client.get('/mitarbeiter/suchen?funktionen=%7B%22funktionen%22%3A+%5B%7B%22route%22%3A+%22'
                        'mitarbeiter.aktivieren%22%2C+%22label%22%3A+%22Aktivieren%22%7D%2C+%7B%22route%22%3A+%22'
                        'mitarbeiter.deaktivieren%22%2C+%22label%22%3A+%22Deaktivieren%22%7D%2C+%7B%22'
                        'route%22%3A+%22mitarbeiter.bearbeiten%22%2C+%22label%22%3A+%22Bearbeiten%22%7D%5D%7D',
                        follow_redirects=True)
        assert rv.status_code == 200
        assert ("Mitarbeiter suchen" in str(rv.data))

    # Testet, ob die Mitarbeitersuche als Mitarbeiter erreichbar ist
    # -> muss das auf die Startseite weiterleiten und auf die fehlende Autorisierung hinweisen
    def test_mitarbeitersuche_erreichbar_als_mitarbeiter(self, client, app):
        set_user(app, "mitarbeiter")
        rv = client.get('/mitarbeiter/suchen?funktionen=%7B%22funktionen%22%3A+%5B%7B%22route%22%3A+%22'
                        'mitarbeiter.aktivieren%22%2C+%22label%22%3A+%22Aktivieren%22%7D%2C+%7B%22route%22%3A+%22'
                        'mitarbeiter.deaktivieren%22%2C+%22label%22%3A+%22Deaktivieren%22%7D%2C+%7B%22'
                        'route%22%3A+%22mitarbeiter.bearbeiten%22%2C+%22label%22%3A+%22Bearbeiten%22%7D%5D%7D',
                        follow_redirects=True)
        assert rv.status_code == 200
        assert ("Sie sind nicht autorisiert, die Seite zu sehen." in str(rv.data))

    # Testet, was beim Durchführen der Mitarbeitersuche passiert, wenn kein Treffer vorliegt
    # -> Meldung "Kein Mitarbeiter zu Ihrer Suche gefunden" sollte geflasht werden
    def test_mitarbeitersuche_suchergebnisse_kein_treffer(self, client, app):
        set_user(app, "personalsachbearbeiter")
        rv = client.post('/mitarbeiter/suchen?funktionen=%7B%22funktionen%22%3A+%5B%7B%22route%22%3A+%22'
                         'mitarbeiter.aktivieren%22%2C+%22label%22%3A+%22Aktivieren%22%7D%2C+%7B%22route%22%3A+%22'
                         'mitarbeiter.deaktivieren%22%2C+%22label%22%3A+%22Deaktivieren%22%7D%2C+%7B%22'
                         'route%22%3A+%22mitarbeiter.bearbeiten%22%2C+%22label%22%3A+%22Bearbeiten%22%7D%5D%7D',
                         data={"suche": "asdfghjlk"},
                         follow_redirects=True)
        assert rv.status_code == 200
        assert "Kein Mitarbeiter zu Ihrer Suche gefunden" in str(rv.data)

    # Testet, was beim Durchführen der Mitarbeitersuche passiert, wenn Treffer vorliegen
    # -> Suchergebnisse sollten inklusive der Aktionslinks (in diesem Fall "Bearbeiten") angezeigt werden
    def test_mitarbeitersuche_suchergebnisse_treffer(self, client, app):
        set_user(app, "personalsachbearbeiter")
        rv = client.post('/mitarbeiter/suchen?funktionen=%7B%22funktionen%22%3A+%5B%7B%22route%22%3A+%22'
                         'mitarbeiter.aktivieren%22%2C+%22label%22%3A+%22Aktivieren%22%7D%2C+%7B%22route%22%3A+%22'
                         'mitarbeiter.deaktivieren%22%2C+%22label%22%3A+%22Deaktivieren%22%7D%2C+%7B%22'
                         'route%22%3A+%22mitarbeiter.bearbeiten%22%2C+%22label%22%3A+%22Bearbeiten%22%7D%5D%7D',
                         data={"suche": "a"},
                         follow_redirects=True)
        assert rv.status_code == 200
        assert "Bearbeiten" in str(rv.data)

    ###############################################################
    # UC 1.3 Mitarbeiterdaten ändern
    ###############################################################

    # Testet, ob die "Mitarbeiter Bearbeiten"-Seite ohne Login erreichbar ist
    # -> muss auf die Login-Seite weiterleiten und "Sie sind nicht eingeloggt" flashen
    def test_mitarbeiter_bearbeiten_erreichbar_ohne_login(self, client, app):
        rv = client.get('/mitarbeiter/bearbeiten/mitarbeiter', follow_redirects=True)
        assert rv.status_code == 200
        assert ("Sie sind nicht eingeloggt" in str(rv.data))

    # Testet, ob die "Mitarbeiter Bearbeiten"-Seite als Personalsachbearbeiter erreichbar ist
    # -> muss das "Mitarbeiter Bearbeiten"-Formular fuer den angegebenen Mitarbeiter anzeigen
    def test_mitarbeiter_bearbeiten_erreichbar_als_personalsachbearbeiter(self, client, app):
        set_user(app, "personalsachbearbeiter")
        rv = client.get('/mitarbeiter/bearbeiten/mitarbeiter', follow_redirects=True)
        assert rv.status_code == 200
        assert ("Mitarbeiter mitarbeiter bearbeiten" in str(rv.data))

    # Testet, ob die "Mitarbeiter Bearbeiten"-Seite als Mitarbeiter erreichbar ist
    # -> muss das auf die Startseite weiterleiten und auf die fehlende Autorisierung hinweisen
    def test_mitarbeiter_bearbeiten_erreichbar_als_mitarbeiter(self, client, app):
        set_user(app, "mitarbeiter")
        rv = client.get('/mitarbeiter/bearbeiten/mitarbeiter', follow_redirects=True)
        assert rv.status_code == 200
        assert ("Sie sind nicht autorisiert, die Seite zu sehen." in str(rv.data))

    # Testet, ob die "Mitarbeiter Bearbeiten"-Seite mit nicht existentem Username erreichbar ist
    # -> muss auf die Startseite weiterleiten und eine entsprechende Fehlermeldung flashen
    def test_mitarbeiter_bearbeiten_erreichbar_falscher_username(self, client, app):
        set_user(app, "personalsachbearbeiter")
        rv = client.get('/mitarbeiter/bearbeiten/test123', follow_redirects=True)
        assert rv.status_code == 200
        assert ("Der Mitarbeiter, den Sie bearbeiten wollen, existiert nicht" in str(rv.data))

    # Testet, ob ein Mitarbeiter über die App bearbeitet werden kann
    # -> das System muss auf die Startseite weiterleiten und eine Erfolgsmeldung ausgeben
    # -> die geänderten Daten müssen in der Datenbank vorhanden sein (d.h. ausgelesen werden können)
    def test_mitarbeiter_bearbeiten_korrekter_input(self, client, app):
        create_ulrich25()
        set_user(app, "personalsachbearbeiter")
        form_input = {
            "vorname": "Ulrike",
            "nachname": "Hardmann",
            "username": "ulrich25",
            "rolle": "Mitarbeiter",
            "gebdat": "1989-04-04",
            "geschlecht": "transmaskulin",
            "email": "uli25@web.de",
            "telefon": "123456789",
            "adresse_plz": "87700",
            "adresse_ort": "Memmingen",
            "adresse_strasse": "Amselweg",
            "adresse_hausnr": "5",
            "stunden_pro_woche": "18",
            "urlaubstage_pro_jahr": "25"
        }
        rv = client.post('/mitarbeiter/bearbeiten/ulrich25', data=form_input, follow_redirects=True)
        assert rv.status_code == 200
        # Meldung wird angezeigt
        assert "Mitarbeiterdaten erfolgreich" in str(rv.data)
        # Daten sind in der Datenbank wirklich angepasst
        assert Mitarbeiter.objects(username="ulrich25").first().stunden_pro_woche == 18
        Mitarbeiter.objects(username="ulrich25").delete()

    # Testet, ob die Validierung des "Bearbeiten"-Formulars funktioniert
    # -> das System muss eine Fehlermeldung bei den entsprechenden Feldern anzeigen
    # -> die im Request geschickten Daten dürfen nicht in der Datenbank stehen
    def test_mitarbeiter_bearbeiten_inkorrekter_input(self, client, app):
        create_ulrich25()
        set_user(app, "personalsachbearbeiter")
        form_input = {
            "vorname": "Ulrike",
            "nachname": "Hardmann",
            "username": "ulrich25",
            "rolle": "Mitarbeiter",
            "gebdat": "1989-04-04",
            "geschlecht": "transmaskulin",
            "email": "uli25@web.de",
            "telefon": "123456789",
            "adresse_plz": "87700",
            "adresse_ort": "Memmingen",
            "adresse_strasse": "Amselweg",
            "adresse_hausnr": "5",
            "stunden_pro_woche": "asdf",
            "urlaubstage_pro_jahr": "500"
        }
        rv = client.post('/mitarbeiter/bearbeiten/ulrich25', data=form_input, follow_redirects=True)
        assert rv.status_code == 200
        # Meldung wird angezeigt
        assert "This field is required" in str(rv.data)
        # Daten sind in der Datenbank unverändert
        assert Mitarbeiter.objects(username="ulrich25").first().urlaubstage != 500
        Mitarbeiter.objects(username="ulrich25").delete()

    ###############################################################
    # UC 1.4 Mitarbeiter deaktivieren
    ###############################################################

    # Testet, ob die "Mitarbeiter Deaktivieren"-Seite ohne Login erreichbar ist
    # -> muss auf die Login-Seite weiterleiten und "Sie sind nicht eingeloggt" flashen
    def test_mitarbeiter_deaktivieren_erreichbar_ohne_login(self, client, app):
        rv = client.get('/mitarbeiter/deaktivieren/mitarbeiter', follow_redirects=True)
        assert rv.status_code == 200
        assert ("Sie sind nicht eingeloggt" in str(rv.data))

    # Testet, ob die "Mitarbeiter Deaktivieren"-Seite als Personalsachbearbeiter erreichbar ist
    # -> muss einen Bestätigungsdialog zum Deaktivieren des angegebenen Mitarbeiters anzeigen
    def test_mitarbeiter_deaktivieren_erreichbar_als_personalsachbearbeiter(self, client, app):
        set_user(app, "personalsachbearbeiter")
        rv = client.get('/mitarbeiter/deaktivieren/mitarbeiter', follow_redirects=True)
        assert rv.status_code == 200
        assert ("Mitarbeiter deaktivieren" in str(rv.data))

    # Testet, ob die "Mitarbeiter Deaktivieren"-Seite als Mitarbeiter erreichbar ist
    # -> muss das auf die Startseite weiterleiten und auf die fehlende Autorisierung hinweisen
    def test_mitarbeiter_deaktivieren_erreichbar_als_mitarbeiter(self, client, app):
        set_user(app, "mitarbeiter")
        rv = client.get('/mitarbeiter/deaktivieren/mitarbeiter', follow_redirects=True)
        assert rv.status_code == 200
        assert ("Sie sind nicht autorisiert, die Seite zu sehen." in str(rv.data))

    # Testet, ob die "Mitarbeiter Deaktivieren"-Seite mit nicht existentem Username erreichbar ist
    # -> muss auf die Startseite weiterleiten und eine entsprechende Fehlermeldung flashen
    def test_mitarbeiter_deaktivieren_erreichbar_falscher_username(self, client, app):
        set_user(app, "personalsachbearbeiter")
        rv = client.get('/mitarbeiter/deaktivieren/test123', follow_redirects=True)
        assert rv.status_code == 200
        assert ("Der Mitarbeiter, den Sie deaktivieren wollen, existiert nicht" in str(rv.data))

    # Testet, ob ein Mitarbeiter per POST-Anfrage an die entsprechende URL deaktiviert werden kann
    # (entspricht dem Drücken des "Bestätigen"-Buttons in der GUI)
    # -> der anschliessend aus der Datenbank ausgelesene Status des Mitarbeiters muss "inaktiv" sein
    def test_mitarbeiter_deaktivieren_bestaetigen(self, client, app):
        set_user(app, "personalsachbearbeiter")
        # Testmitarbeiter erstellen und sicherstellen, dass dieser vor der Testdurchführung aktiv ist
        create_ulrich25()
        ulrich25 = Mitarbeiter.objects(username="ulrich25").first()
        ulrich25.aktiv = True
        ulrich25.save()
        form_input = {
            "bestaetigen": True
        }
        rv = client.post("/mitarbeiter/deaktivieren/ulrich25", data=form_input, follow_redirects=True)
        # Weiterleitung und Flashen der Erfolgsmeldung testen
        assert rv.status_code == 200
        assert ("Mitarbeiter ulrich25 deaktiviert" in str(rv.data))
        # Sicherstellen, dass die Änderung persistent in der Datenbank übernommen wurde
        assert not Mitarbeiter.objects(username="ulrich25").first().aktiv
        Mitarbeiter.objects(username="ulrich25").delete()

    ###############################################################
    # UC 1.5 Mitarbeiter aktivieren
    ###############################################################

    # Testet, ob die "Mitarbeiter Aktivieren"-Seite ohne Login erreichbar ist
    # -> muss auf die Login-Seite weiterleiten und "Sie sind nicht eingeloggt" flashen
    def test_mitarbeiter_aktivieren_erreichbar_ohne_login(self, client, app):
        rv = client.get('/mitarbeiter/aktivieren/mitarbeiter', follow_redirects=True)
        assert rv.status_code == 200
        assert ("Sie sind nicht eingeloggt" in str(rv.data))

    # Testet, ob die "Mitarbeiter Aktivieren"-Seite als Personalsachbearbeiter erreichbar ist
    # -> muss einen Bestätigungsdialog zum Aktivieren des angegebenen Mitarbeiters anzeigen
    def test_mitarbeiter_aktivieren_erreichbar_als_personalsachbearbeiter(self, client, app):
        set_user(app, "personalsachbearbeiter")
        rv = client.get('/mitarbeiter/aktivieren/mitarbeiter', follow_redirects=True)
        assert rv.status_code == 200
        assert ("Mitarbeiter aktivieren" in str(rv.data))

    # Testet, ob die "Mitarbeiter Aktivieren"-Seite als Mitarbeiter erreichbar ist
    # -> muss das auf die Startseite weiterleiten und auf die fehlende Autorisierung hinweisen
    def test_mitarbeiter_aktivieren_erreichbar_als_mitarbeiter(self, client, app):
        set_user(app, "mitarbeiter")
        rv = client.get('/mitarbeiter/aktivieren/mitarbeiter', follow_redirects=True)
        assert rv.status_code == 200
        assert ("Sie sind nicht autorisiert, die Seite zu sehen." in str(rv.data))

    # Testet, ob die "Mitarbeiter Aktivieren"-Seite mit nicht existentem Username erreichbar ist
    # -> muss auf die Startseite weiterleiten und eine entsprechende Fehlermeldung flashen
    def test_mitarbeiter_aktivieren_erreichbar_falscher_username(self, client, app):
        set_user(app, "personalsachbearbeiter")
        rv = client.get('/mitarbeiter/aktivieren/test123', follow_redirects=True)
        assert rv.status_code == 200
        assert ("Der Mitarbeiter, den Sie aktivieren wollen, existiert nicht" in str(rv.data))

    # Testet, ob ein Mitarbeiter per POST-Anfrage an die entsprechende URL aktiviert werden kann
    # (entspricht dem Drücken des "Bestätigen"-Buttons in der GUI)
    # -> der anschliessend aus der Datenbank ausgelesene Status des Mitarbeiters muss "aktiv" sein
    def test_mitarbeiter_aktivieren_bestaetigen(self, client, app):
        set_user(app, "personalsachbearbeiter")
        # Testmitarbeiter erstellen und sicherstellen, dass dieser vor der Testdurchführung inaktiv ist
        create_ulrich25()
        ulrich25 = Mitarbeiter.objects(username="ulrich25").first()
        ulrich25.aktiv = False
        ulrich25.save()
        form_input = {
            "bestaetigen": True
        }
        rv = client.post("/mitarbeiter/aktivieren/ulrich25", data=form_input, follow_redirects=True)
        # Weiterleitung und Flashen der Erfolgsmeldung testen
        assert rv.status_code == 200
        assert ("Mitarbeiter ulrich25 aktiviert" in str(rv.data))
        # Sicherstellen, dass die Änderung persistent in der Datenbank übernommen wurde
        assert Mitarbeiter.objects(username="ulrich25").first().aktiv
        Mitarbeiter.objects(username="ulrich25").delete()
