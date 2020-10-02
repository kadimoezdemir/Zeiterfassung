#! ../env/bin/python
# -*- coding: utf-8 -*-
import pytest
from app.models.models import Mitarbeiter, Fehlzeit
from datetime import date


@pytest.mark.usefixtures("client", "app")
class TestAP2:

    # Die folgenden Tests testen die Erreichbarkeit der Seiten ohne eingeloggt zu sein
    # Es muss auf die Startseite weitergeleitet und die Meldung "Sie sind nicht eingeloggt." geflasht werden
    def test_fehlzeit_home_ohne_login(self, client, app):
        rv = client.get('/fehltage/home', follow_redirects=True)
        assert rv.status_code == 200
        assert ("Sie sind nicht eingeloggt." in str(rv.data))

    def test_fehlzeit_uebersicht_ohne_login(self, client, app):
        rv = client.get('/fehltage/uebersicht/mitarbeiter', follow_redirects=True)
        assert rv.status_code == 200
        assert ("Sie sind nicht eingeloggt." in str(rv.data))

    def test_fehlzeit_eintragen_ohne_login(self, client, app):
        rv = client.get('/fehltage/eintragen/mitarbeiter', follow_redirects=True)
        assert rv.status_code == 200
        assert ("Sie sind nicht eingeloggt." in str(rv.data))

    def test_fehlzeit_bearbeiten_ohne_login(self, client, app):
        rv = client.get('/fehltage/bearbeiten/mitarbeiter/2', follow_redirects=True)
        assert rv.status_code == 200
        assert ("Sie sind nicht eingeloggt." in str(rv.data))

    def test_fehlzeit_loeschen_ohne_login(self, client, app):
        rv = client.get('/fehltage/loeschen/mitarbeiter/2', follow_redirects=True)
        assert rv.status_code == 200
        assert ("Sie sind nicht eingeloggt." in str(rv.data))

    # -------------------------------------------------------------------------------------------------
    # Die folgenden Tests testen allesamt ob die jeweilige URL als Personalsachbearbeiter aufrufbar ist
    # Der Personalsachbearbeiter hat die Berechtigung auf alle Seiten zuzugreifen und sollte deshalb alle URLs erreichen
    def test_fehlzeit_home_erreichbarkeit_als_personalsachbearbeiter(self, client, app):
        test_user = Mitarbeiter.objects(username='personalsachbearbeiter').first()

        @app.login_manager.request_loader
        def load_user_from_request(request):
            return test_user

        rv = client.get('/fehltage/home', follow_redirects=True)
        assert rv.status_code == 200
        assert ("Sie sind nicht eingeloggt." not in str(rv.data))
        assert ("Mitarbeiter suchen" in str(rv.data))

    def test_fehlzeit_uebersicht_erreicharkeit_als_personalsachbearbeiter(self, client, app):
        test_user = Mitarbeiter.objects(username='personalsachbearbeiter').first()

        @app.login_manager.request_loader
        def load_user_from_request(request):
            return test_user

        rv = client.get('/fehltage/uebersicht/mitarbeiter', follow_redirects=True)
        assert rv.status_code == 200
        assert ("Sie sind nicht eingeloggt." not in str(rv.data))
        assert ("Mit Arbeiter" in str(rv.data))

    def test_fehlzeit_eintragen_erreichbarkeit_als_personalsachbearbeiter(self, client, app):
        test_user = Mitarbeiter.objects(username='personalsachbearbeiter').first()

        @app.login_manager.request_loader
        def load_user_from_request(request):
            return test_user

        rv = client.get('/fehltage/eintragen/mitarbeiter', follow_redirects=True)
        assert rv.status_code == 200
        assert ("Sie sind nicht eingeloggt." not in str(rv.data))
        assert ("Fehlzeit eintragen" in str(rv.data))
        assert ("Datum von" in str(rv.data))
        assert ("bis" in str(rv.data))
        assert ("Grund" in str(rv.data))

    def test_fehlzeit_bearbeiten_erreichbarkeit_als_personalsachbearbeiter(self, client, app):
        test_user = Mitarbeiter.objects(username='personalsachbearbeiter').first()

        @app.login_manager.request_loader
        def load_user_from_request(request):
            return test_user

        # Sicherstellen, dass eine auswählbare Fehlzeit existiert
        fehlzeit = Fehlzeit()
        fehlzeit.datum_start = date(2040, 3, 3)
        fehlzeit.datum_ende = date(2040, 3, 3)
        fehlzeit.grund = "Urlaub"
        fehlzeit.id = "777"
        ma = Mitarbeiter.objects(username="mitarbeiter").first()
        ma.fehlzeiten.append(fehlzeit)
        ma.save()

        rv = client.get('/fehltage/bearbeiten/mitarbeiter/777', follow_redirects=True)
        assert rv.status_code == 200
        assert ("Sie sind nicht eingeloggt." not in str(rv.data))
        assert ("Fehlzeit bearbeiten" in str(rv.data))

        ma.fehlzeiten.filter(id="777").delete()
        ma.save()

    def test_fehlzeit_loeschen_erreichbarkeit_als_personalsachbearbeiter(self, client, app):
        test_user = Mitarbeiter.objects(username='personalsachbearbeiter').first()

        @app.login_manager.request_loader
        def load_user_from_request(request):
            return test_user

        # Fehlzeit anlegen, damit der Test reproduzierbar wird
        fehlzeit = Fehlzeit()
        fehlzeit.datum_start = date(2030, 3, 3)
        fehlzeit.datum_ende = date(2030, 3, 3)
        fehlzeit.grund = "Urlaub"
        fehlzeit.id = "777"
        ma = Mitarbeiter.objects(username="mitarbeiter").first()
        ma.fehlzeiten.append(fehlzeit)
        ma.save()

        rv = client.get('/fehltage/loeschen/mitarbeiter/777', follow_redirects=True)
        assert rv.status_code == 200
        assert ("Sie sind nicht eingeloggt." not in str(rv.data))
        assert ("Fehlzeit \\xc3\\x9cbersicht" in str(rv.data))
        assert ("Fehlzeit erfolgreich" in str(rv.data))
        assert ("Mit Arbeiter" in str(rv.data))

        # Sicherstellen, dass die Fehlzeit nicht mehr in der Datenbank ist
        ma = Mitarbeiter.objects(username="mitarbeiter").first()
        assert ma.fehlzeiten.filter(id="777").first() is None

    # --------------------------------------------------------------------------------------
    # Die folgenden Tests testen allesamt ob die jeweilige URL als Mitarbeiter aufrufbar ist
    # Mitarbeiter hat nicht die Berechtigung auf eine der Seiten zuzugreifen und sollte deshalb keine der URLs erreichen
    def test_fehlzeit_home_erreichbarkeit_als_mitarbeiter(self, client, app):
        test_user = Mitarbeiter.objects(username='mitarbeiter').first()

        @app.login_manager.request_loader
        def load_user_from_request(request):
            return test_user

        rv = client.get('/fehltage/home', follow_redirects=True)
        assert rv.status_code == 200
        assert ("Sie sind nicht eingeloggt." not in str(rv.data))
        assert ("Mitarbeiter suchen" not in str(rv.data))
        assert ("Sie sind nicht autorisiert, die Seite zu sehen." in str(rv.data))

    def test_fehlzeit_uebersicht_erreicharkeit_als_mitarbeiter(self, client, app):
        test_user = Mitarbeiter.objects(username='mitarbeiter').first()

        @app.login_manager.request_loader
        def load_user_from_request(request):
            return test_user

        rv = client.get('/fehltage/uebersicht/mitarbeiter', follow_redirects=True)
        assert rv.status_code == 200
        assert ("Sie sind nicht eingeloggt." not in str(rv.data))
        assert ("Mit Arbeiter" not in str(rv.data))
        assert ("Sie sind nicht autorisiert, die Seite zu sehen." in str(rv.data))

    def test_fehlzeit_eintragen_erreichbarkeit_als_mitarbeiter(self, client, app):
        test_user = Mitarbeiter.objects(username='mitarbeiter').first()

        @app.login_manager.request_loader
        def load_user_from_request(request):
            return test_user

        rv = client.get('/fehltage/eintragen/mitarbeiter', follow_redirects=True)
        assert rv.status_code == 200
        assert ("Sie sind nicht eingeloggt." not in str(rv.data))
        assert ("Fehlzeit eintragen" not in str(rv.data))
        assert ("Sie sind nicht autorisiert, die Seite zu sehen." in str(rv.data))

    def test_fehlzeit_bearbeiten_erreichbarkeit_als_mitarbeiter(self, client, app):
        test_user = Mitarbeiter.objects(username='mitarbeiter').first()

        @app.login_manager.request_loader
        def load_user_from_request(request):
            return test_user

        # Sicherstellen, dass eine auswählbare Fehlzeit existiert
        fehlzeit = Fehlzeit()
        fehlzeit.datum_start = date(2040, 3, 3)
        fehlzeit.datum_ende = date(2040, 3, 3)
        fehlzeit.grund = "Urlaub"
        fehlzeit.id = "777"
        ma = Mitarbeiter.objects(username="mitarbeiter").first()
        ma.fehlzeiten.append(fehlzeit)
        ma.save()

        rv = client.get('/fehltage/bearbeiten/mitarbeiter/777', follow_redirects=True)
        assert rv.status_code == 200
        assert ("Sie sind nicht eingeloggt." not in str(rv.data))
        assert ("Fehlzeit bearbeiten" not in str(rv.data))
        assert ("Sie sind nicht autorisiert, die Seite zu sehen." in str(rv.data))

        ma.fehlzeiten.filter(id="777").delete()
        ma.save()

    def test_fehlzeit_loeschen_erreichbarkeit_als_mitarbeiter(self, client, app):
        test_user = Mitarbeiter.objects(username='mitarbeiter').first()

        @app.login_manager.request_loader
        def load_user_from_request(request):
            return test_user

        # Fehlzeit anlegen, damit der Test reproduzierbar wird
        fehlzeit = Fehlzeit()
        fehlzeit.datum_start = date(2030, 3, 3)
        fehlzeit.datum_ende = date(2030, 3, 3)
        fehlzeit.grund = "Urlaub"
        fehlzeit.id = "777"
        ma = Mitarbeiter.objects(username="mitarbeiter").first()
        ma.fehlzeiten.append(fehlzeit)
        ma.save()

        rv = client.get('/fehltage/loeschen/mitarbeiter/777', follow_redirects=True)
        assert rv.status_code == 200
        assert ("Sie sind nicht eingeloggt." not in str(rv.data))
        assert ("Fehlzeit \\xc3\\x9cbersicht" not in str(rv.data))
        assert ("Fehlzeit erfolgreich" not in str(rv.data))
        assert ("Sie sind nicht autorisiert, die Seite zu sehen." in str(rv.data))

        # Sicherstellen, dass die Fehlzeit noch in der Datenbank ist
        ma = Mitarbeiter.objects(username="mitarbeiter").first()
        fehlzeit = ma.fehlzeiten.filter(id="777").first()
        assert fehlzeit is not None

        ma.fehlzeiten.filter(id="777").delete()
        ma.save()

    #----------------------------------------------------------------------
    # Testet ob eine Fehlzeit mit gültigen Werten eingetragen werden kann
    def test_fehlzeit_eintragen_mit_gueltigen_werten(self, client, app):
        test_user = Mitarbeiter.objects(username='personalsachbearbeiter').first()

        @app.login_manager.request_loader
        def load_user_from_request(request):
            return test_user

        form_input = {
            "datum_start": "2030-03-03",
            "datum_ende": "2030-03-03",
            "grund": "Erkrankung",
            "id": "777"
        }
        rv = client.post('/fehltage/eintragen/mitarbeiter', data=form_input, follow_redirects=True)
        assert rv.status_code == 200
        assert ("Sie sind nicht eingeloggt." not in str(rv.data))
        assert ("Fehlzeit erfolgreich angelegt" in str(rv.data))

        # Sicherstellen, dass die Fehlzeit in der Datenbank eingetragen ist
        ma = Mitarbeiter.objects(username="mitarbeiter").first()
        assert ma.fehlzeiten.filter(id="777").first() is not None

        # Fehlzeit wieder loeschen, damit die ID beim naechsten Durchlauf frei ist
        ma.fehlzeiten.filter(id="777").delete()
        ma.save()

    # Testet ob der Versuch eine Fehlzeit mit ungültigen Werten einzutragen abgefangen wird
    def test_fehlzeit_eintragen_mit_ungueltigen_werten(self, client, app):
        test_user = Mitarbeiter.objects(username='personalsachbearbeiter').first()

        @app.login_manager.request_loader
        def load_user_from_request(request):
            return test_user

        form_input = {
            "datum_start": "2050-03-04",
            "datum_ende": "2050-03-03",
            "grund": "Erkrankung",
            "id": "777"
        }
        rv = client.post('/fehltage/eintragen/mitarbeiter', data=form_input, follow_redirects=True)
        assert rv.status_code == 200
        assert ("Sie sind nicht eingeloggt." not in str(rv.data))
        assert ("Fehlzeit erfolgreich angelegt" not in str(rv.data))
        assert ("Zeitrahmen ist" in str(rv.data))

        # Sicherstellen, dass die Fehlzeit nicht in der Datenbank eingetragen ist
        ma = Mitarbeiter.objects(username="mitarbeiter").first()
        assert ma.fehlzeiten.filter(id="777").first() is None

    # Testet ob eine Fehlzeit mit gültigen Werten bearbeitet werden kann
    def test_fehlzeit_bearbeiten_mit_gueltigen_werten(self, client, app):
        test_user = Mitarbeiter.objects(username='personalsachbearbeiter').first()

        @app.login_manager.request_loader
        def load_user_from_request(request):
            return test_user

        # Fehlzeit anlegen, die bearbeitet werden kann
        fehlzeit = Fehlzeit()
        fehlzeit.datum_start = date(2090, 3, 3)
        fehlzeit.datum_ende = date(2090, 3, 3)
        fehlzeit.grund = "Urlaub"
        fehlzeit.id = "888"
        ma = Mitarbeiter.objects(username="mitarbeiter").first()
        ma.fehlzeiten.append(fehlzeit)
        ma.save()

        form_input = {
            "datum_start": "2080-07-07",
            "datum_ende": "2080-07-07",
            "grund": "Erkrankung",
            "id": "888"
        }
        rv = client.post('/fehltage/bearbeiten/mitarbeiter/888', data=form_input, follow_redirects=True)
        assert rv.status_code == 200
        assert ("Sie sind nicht eingeloggt." not in str(rv.data))
        assert ("Fehlzeit erfolgreich bearbeitet" in str(rv.data))

        # Sicherstellen, dass die Fehlzeit in der Datenbank die neuen Werte besitzt
        ma = Mitarbeiter.objects(username="mitarbeiter").first()
        fehlzeit = ma.fehlzeiten.filter(id="888").first()
        assert str(fehlzeit.datum_start) == "2080-07-07"
        assert str(fehlzeit.datum_ende) == "2080-07-07"
        assert fehlzeit.grund == "Erkrankung"
        assert fehlzeit.id == "888"

        # Fehlzeit wieder loeschen, damit die ID beim naechsten Durchlauf frei ist
        ma.fehlzeiten.filter(id="888").delete()
        ma.save()

    # Testet ob der Versuch eine Fehlzeit mit ungültigen Werten zu bearbeiten abgefangen wird
    def test_fehlzeit_bearbeiten_mit_ungueltigen_werten(self, client, app):
        test_user = Mitarbeiter.objects(username='personalsachbearbeiter').first()

        @app.login_manager.request_loader
        def load_user_from_request(request):
            return test_user

        # Fehlzeit anlegen, die bearbeitet werden kann
        fehlzeit = Fehlzeit()
        fehlzeit.datum_start = date(2090, 3, 3)
        fehlzeit.datum_ende = date(2090, 3, 3)
        fehlzeit.grund = "Urlaub"
        fehlzeit.id = "888"
        ma = Mitarbeiter.objects(username="mitarbeiter").first()
        ma.fehlzeiten.append(fehlzeit)
        ma.save()

        form_input = {
            "datum_start": "2080-07-07",
            # datum_ende wir nicht angegeben -> unzulässig
            "grund": "Erkrankung",
            "id": "888"
        }
        rv = client.post('/fehltage/bearbeiten/mitarbeiter/888', data=form_input, follow_redirects=True)
        assert rv.status_code == 200
        assert ("Sie sind nicht eingeloggt." not in str(rv.data))
        assert ("Fehlzeit erfolgreich bearbeitet" not in str(rv.data))
        assert ("Dies ist ein Pflichtfeld." in str(rv.data))

        # Sicherstellen, dass die Fehlzeit in der Datenbank die alten Werte besitzt
        ma = Mitarbeiter.objects(username="mitarbeiter").first()
        fehlzeit = ma.fehlzeiten.filter(id="888").first()
        assert str(fehlzeit.datum_start) == "2090-03-03"
        assert str(fehlzeit.datum_ende) == "2090-03-03"
        assert fehlzeit.grund == "Urlaub"
        assert fehlzeit.id == "888"

        # Fehlzeit wieder loeschen, damit die ID beim naechsten Durchlauf frei ist
        ma.fehlzeiten.filter(id="888").delete()
        ma.save()

    # Testet ob mit gültigen Eingaben gefiltert werden kann
    def test_fehlzeit_uebersicht_filter_mit_gueltigen_werten(self, client, app):
        test_user = Mitarbeiter.objects(username='personalsachbearbeiter').first()

        @app.login_manager.request_loader
        def load_user_from_request(request):
            return test_user

        form_input = {
            "radio": "beliebig",
            "datum_start": "2000-01-01",
            "datum_ende": "2121-01-01",
            "erkrankung": "true"
        }

        rv = client.post('/fehltage/uebersicht/mitarbeiter/true/true', data=form_input, follow_redirects=True)
        assert rv.status_code == 200
        # assert (">Erkrankung<" in str(rv.data))
        assert (">Urlaub<" not in str(rv.data))
        assert (">Zeitausgleich<" not in str(rv.data))
        assert (">Home-Office<" not in str(rv.data))

    # Testet ob der Versuch mit ungültigen Eingaben zu filtern abgefangen wird
    def test_fehlzeit_uebersicht_filter_mit_ungueltigen_werten(self, client, app):
        test_user = Mitarbeiter.objects(username='personalsachbearbeiter').first()

        @app.login_manager.request_loader
        def load_user_from_request(request):
            return test_user

        form_input = {
            "radio": "beliebig",
            "datum_start": "2000-01-01",
            # datum_ende wird nicht angegeben -> unzulässig
            "erkrankung": "true"
        }

        rv = client.post('/fehltage/uebersicht/mitarbeiter/true/true', data=form_input, follow_redirects=True)
        assert rv.status_code == 200
        assert "Filtereinstellungen" in str(rv.data)
        assert ("Sie m\\xc3\\xbcssen ein Start- und Enddatum angeben" in str(rv.data))
