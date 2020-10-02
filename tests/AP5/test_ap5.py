#! ../env/bin/python
# -*- coding: utf-8 -*-

import pytest
import app.main.forms
from app.models.models import Mitarbeiter


@pytest.mark.usefixtures("client", "app")
class TestAP5:
    def test_anwesenheitstableau_not_loggedin(self, client, app):
        """ Anwesenheitstableau darf nicht angezeigt werden, wenn nicht eingeloggt """

        rv = client.get('statistiken/anwesenheitstableau', follow_redirects=True)
        assert rv.status_code == 200
        assert ("Sie sind nicht eingeloggt." in str(rv.data))

    def test_anwesenheitstableau_as_mitarbeiter(self, client, app):
        """ Anwesenheitstableau darf nicht angezeigt werden, wenn als Mitarbeiter eingeloggt """
        test_user = Mitarbeiter.objects(username='mitarbeiter').first()

        @app.login_manager.request_loader
        def load_user_from_request(request):
            return test_user

        rv = client.get('statistiken/anwesenheitstableau', follow_redirects=True)
        assert rv.status_code == 200
        assert ("Sie sind nicht autorisiert, die Seite zu sehen." in str(rv.data))

    def test_anwesenheitstableau_as_personalsachbearbeiter(self, client, app):
        """ Anwesenheitstableau muss angezeigt werden, wenn als Personalsachbearbeiter eingeloggt """
        test_user = Mitarbeiter.objects(username='personalsachbearbeiter').first()

        @app.login_manager.request_loader
        def load_user_from_request(request):
            return test_user

        rv = client.get('statistiken/anwesenheitstableau', follow_redirects=True)
        assert rv.status_code == 200
        assert ("Anwesenheitstableau" in str(rv.data))
        # Tabelle wird angezeigt
        # Spalte "Vorname" wird angezeigt
        assert ('<div class="col-sm-3 text-left font-weight-bold">Vorname</div>' in str(rv.data))
        # Spalte "Nachname" wird angezeigt
        assert ('<div class="col-sm-3 text-left font-weight-bold">Nachname</div>' in str(rv.data))
        # Spalte "Anwesend/Abwesend" wird angezeigt
        assert ('<div class="col-sm-3 text-right font-weight-bold">Anwesend/Abwesend</div>' in str(rv.data))
        # Spalte "Grund" wird angezeigt
        assert ('<div class="col-sm-3 text-left font-weight-bold">Grund</div>' in str(rv.data))

    def test_meine_jahresarbeitstage_uebersicht_personalsachbearbeiter(self, client, app):
        """ Meine Jahresarbeitstageuebersicht als Personalsachbearbeiter erreichbar """

        test_user = Mitarbeiter.objects(username='personalsachbearbeiter').first()

        @app.login_manager.request_loader
        def load_user_from_request(request):
            return test_user

        rv = client.get('/meine_statistiken/meine_jahresarbeitstage_uebersicht', follow_redirects=True)
        assert rv.status_code == 200
        assert ("Meine Jahresarbeitstage" in str(rv.data))
        # Legende wird angezeigt
        assert ('<div class="row"><div class="col-sm-2 text-center table-danger"><b>Erkrankung</b></div><div '
                'class="col-sm-2 text-center table-info"><b>Home-Office</b></div><div class="col-sm-2 text-center '
                'table-secondary"><b>Urlaub</b></div><div class="col-sm-2 text-center '
                'table-warning"><b>Zeitausgleich</b></div><div class="col-sm-2 text-center '
                'light"><b>nichts</b></div><div class="col-sm-2 text-center '
                'table-success"><b>gearbeitet</b></div></div>' in str(rv.data))
        # Dropdown Menü wird angezeigt
        assert ('<a class="dropdown-item" href="/meine_statistiken/meine_jahresarbeitstage_uebersicht/2020">2020</a>' in str(rv.data))

    def test_meine_jahresarbeitstage_uebersicht_mitarbeiter(self, client, app):
        """ Meine Jahresarbeitstageuebersicht als Mitarbeiter erreichbar """

        test_user = Mitarbeiter.objects(username='mitarbeiter').first()

        @app.login_manager.request_loader
        def load_user_from_request(request):
            return test_user

        rv = client.get('/meine_statistiken/meine_jahresarbeitstage_uebersicht', follow_redirects=True)
        assert rv.status_code == 200
        assert ("Meine Jahresarbeitstage" in str(rv.data))
        # Legende wird angezeigt
        assert ('<div class="row"><div class="col-sm-2 text-center table-danger"><b>Erkrankung</b></div><div '
                'class="col-sm-2 text-center table-info"><b>Home-Office</b></div><div class="col-sm-2 text-center '
                'table-secondary"><b>Urlaub</b></div><div class="col-sm-2 text-center '
                'table-warning"><b>Zeitausgleich</b></div><div class="col-sm-2 text-center '
                'light"><b>nichts</b></div><div class="col-sm-2 text-center '
                'table-success"><b>gearbeitet</b></div></div>' in str(rv.data))
        # Dropdown Menü wird angezeigt
        assert ('<a class="dropdown-item" href="/meine_statistiken/meine_jahresarbeitstage_uebersicht/2020">2020</a>' in str(rv.data))

    def test_meine_jahresarbeitstage_uebersicht_loggedout(self, client, app):
        """ Meine Jahresarbeitstageuebersicht nicht erreichbar, wenn nicht eingeloggt """

        rv = client.get('/meine_statistiken/meine_jahresarbeitstage_uebersicht', follow_redirects=True)
        assert rv.status_code == 200
        assert ("Sie sind nicht eingeloggt." in str(rv.data))

    def test_jahresarbeitstage_uebersicht_eines_ma_personalsachbearbeiter(self, client, app):
        """ Jahresarbeitstageuebersicht eines Mitarbeitrs als Personalsachbearbeiter erreichbar"""

        test_user = Mitarbeiter.objects(username='personalsachbearbeiter').first()

        @app.login_manager.request_loader
        def load_user_from_request(request):
            return test_user

        rv = client.get('/statistiken/jahresarbeitstage/mitarbeiter', follow_redirects=True)
        assert rv.status_code == 200
        assert ("Jahresarbeitstage von Mit Arbeiter" in str(rv.data))
        # Legende wird angezeigt
        assert ('<div class="row"><div class="col-sm-2 text-center table-danger"><b>Erkrankung</b></div><div '
                'class="col-sm-2 text-center table-info"><b>Home-Office</b></div><div class="col-sm-2 text-center '
                'table-secondary"><b>Urlaub</b></div><div class="col-sm-2 text-center '
                'table-warning"><b>Zeitausgleich</b></div><div class="col-sm-2 text-center '
                'light"><b>nichts</b></div><div class="col-sm-2 text-center '
                'table-success"><b>gearbeitet</b></div></div>' in str(rv.data))
        # Dropdown Menü wird angezeigt
        assert ('<a class="dropdown-item" href="/statistiken/jahresarbeitstage/mitarbeiter/2020">2020</a>' in str(rv.data))

    def test_jahresarbeitstage_uebersicht_eines_ma_mitarbeiter(self, client, app):
        """ Jahresarbeitstageuebersicht eines Mitarbeitrs als Mitarbeiter NICHT erreichbar"""

        test_user = Mitarbeiter.objects(username='mitarbeiter').first()

        @app.login_manager.request_loader
        def load_user_from_request(request):
            return test_user

        rv = client.get('/statistiken/jahresarbeitstage/mitarbeiter', follow_redirects=True)
        assert rv.status_code == 200
        assert ("Sie sind nicht autorisiert, die Seite zu sehen." in str(rv.data))

    def test_jahresarbeitstage_uebersicht_eines_ma_loggedout(self, client, app):
        """ Jahresarbeitstageuebersicht eines Mitarbeitrs erreichbar, wenn nicht eingeloggt """

        rv = client.get('/statistiken/jahresarbeitstage/mitarbeiter', follow_redirects=True)
        assert rv.status_code == 200
        assert ("Sie sind nicht eingeloggt." in str(rv.data))
