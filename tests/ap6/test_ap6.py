#! ../env/bin/python
# -*- coding: utf-8 -*-

import pytest

from app.models.models import Mitarbeiter

@pytest.mark.usefixtures("client", "app")
class TestAP6:

    def test_personalmanagement_jahres_stunden_uebersicht(self, client, app):
        """
        Test für die Jahres Stunden Übersicht im Personalmanagement teil. Test der Struktur.
        """

        test_user = Mitarbeiter.objects(username='personalsachbearbeiter').first()

        @app.login_manager.request_loader
        def load_user_from_request(request):
            return test_user

        rv = client.get('/fehltage/jahresstunden_uebersicht/mitarbeiter', follow_redirects=True)

        assert rv.status_code == 200
        assert ("""<li class="list-group-item active">Januar</li>""" in str(rv.data))
        assert ("""<li class="list-group-item active">Februar</li>""" in str(rv.data))
        assert ("""<li class="list-group-item active">April</li>""" in str(rv.data))
        assert ("""<li class="list-group-item active">Mai</li>""" in str(rv.data))
        assert ("""<li class="list-group-item active">Juni</li>""" in str(rv.data))
        assert ("""<li class="list-group-item active">Juli</li>""" in str(rv.data))
        assert ("""<li class="list-group-item active">August</li>""" in str(rv.data))
        assert ("""<li class="list-group-item active">September</li>""" in str(rv.data))
        assert ("""<li class="list-group-item active">Oktober</li>""" in str(rv.data))
        assert ("""<li class="list-group-item active">November</li>""" in str(rv.data))
        assert ("""<li class="list-group-item active">Dezember</li>""" in str(rv.data))

        # Drop Down Menü Tests
        assert ("""<a class="dropdown-item" href="/fehltage/jahresstunden_uebersicht/mitarbeiter">2020</a>""" in str(rv.data))

        # Mitarbeiter Namens anzeige
        assert ("<h2>Mit Arbeiter</h2>" in str(rv.data))

    def test_personalmanagement_stundensaldo(self, client, app):
        """
        Test für die Stundensaldo Übersicht im Personalmanagement teil. Test der Struktur.
        """

        test_user = Mitarbeiter.objects(username='personalsachbearbeiter').first()

        @app.login_manager.request_loader
        def load_user_from_request(request):
            return test_user

        rv = client.get('/fehltage/stundensaldo/mitarbeiter', follow_redirects=True)

        assert rv.status_code == 200
        assert ("""<li class="list-group-item active">Stundensaldo</li>""" in str(rv.data))
        assert ("""<li class="list-group-item active">Arbeitstage</li>""" in str(rv.data))
        assert ("""<li class="list-group-item active">Urlaub</li>""" in str(rv.data))

        # Drop Down Menü Tests
        assert ("""<a class="dropdown-item" href="/fehltage/stundensaldo/mitarbeiter">2020</a>""" in str(rv.data))

        # Mitarbeiter Namens anzeige
        assert ("<h2>Mit Arbeiter</h2>" in str(rv.data))

    def test_personalmanagement_stundensaldo_mit_jahr(self, client, app):
        """
        Test für die Stundensaldo Übersicht im Personalmanagement teil mit Jahr. Test der Struktur.
        """

        test_user = Mitarbeiter.objects(username='personalsachbearbeiter').first()

        @app.login_manager.request_loader
        def load_user_from_request(request):
            return test_user

        rv = client.get('/fehltage/stundensaldo/mitarbeiter/2019', follow_redirects=True)

        assert rv.status_code == 200
        assert ("""<li class="list-group-item active">Stundensaldo</li>""" in str(rv.data))
        assert ("""<li class="list-group-item active">Arbeitstage</li>""" in str(rv.data))
        assert ("""<li class="list-group-item active">Urlaub</li>""" in str(rv.data))

        # Drop Down Menü Tests
        assert ("""<a class="dropdown-item" href="/fehltage/stundensaldo/mitarbeiter/2019">2019</a>""" in str(rv.data))
        assert ("""<a class="dropdown-item" href="/fehltage/stundensaldo/mitarbeiter">2020</a>""" in str(rv.data))

        # Mitarbeiter Namens anzeige
        assert ("<h2>Mit Arbeiter</h2>" in str(rv.data))

    def test_personalmanagement_jahres_stunden_uebersicht(self, client, app):
        """
        Test für die Jahres Stunden Übersicht im Personalmanagement teil. Test der Struktur.
        """

        test_user = Mitarbeiter.objects(username='personalsachbearbeiter').first()

        @app.login_manager.request_loader
        def load_user_from_request(request):
            return test_user

        rv = client.get('/fehltage/jahresstunden_uebersicht/mitarbeiter', follow_redirects=True)

        assert rv.status_code == 200
        assert ("""<li class="list-group-item active">Januar</li>""" in str(rv.data))
        assert ("""<li class="list-group-item active">Februar</li>""" in str(rv.data))
        assert ("""<li class="list-group-item active">April</li>""" in str(rv.data))
        assert ("""<li class="list-group-item active">Mai</li>""" in str(rv.data))
        assert ("""<li class="list-group-item active">Juni</li>""" in str(rv.data))
        assert ("""<li class="list-group-item active">Juli</li>""" in str(rv.data))
        assert ("""<li class="list-group-item active">August</li>""" in str(rv.data))
        assert ("""<li class="list-group-item active">September</li>""" in str(rv.data))
        assert ("""<li class="list-group-item active">Oktober</li>""" in str(rv.data))
        assert ("""<li class="list-group-item active">November</li>""" in str(rv.data))
        assert ("""<li class="list-group-item active">Dezember</li>""" in str(rv.data))

        # Drop Down Menü Tests
        assert ("""<a class="dropdown-item" href="/fehltage/jahresstunden_uebersicht/mitarbeiter">2020</a>""" in str(rv.data))

        # Mitarbeiter Namens anzeige
        assert ("<h2>Mit Arbeiter</h2>" in str(rv.data))

    def test_personalmanagement_stundensaldo_mit_jahr(self, client, app):
        """
        Test für die Stundensaldo Übersicht im Personalmanagement teil mit Jahr. Test der Struktur.
        """

        test_user = Mitarbeiter.objects(username='personalsachbearbeiter').first()

        @app.login_manager.request_loader
        def load_user_from_request(request):
            return test_user

        rv = client.get('/fehltage/stundensaldo/mitarbeiter/2019', follow_redirects=True)

        assert rv.status_code == 200
        assert ("""<li class="list-group-item active">Stundensaldo</li>""" in str(rv.data))
        assert ("""<li class="list-group-item active">Arbeitstage</li>""" in str(rv.data))
        assert ("""<li class="list-group-item active">Urlaub</li>""" in str(rv.data))

        # Drop Down Menü Tests
        assert ("""<a class="dropdown-item" href="/fehltage/stundensaldo/mitarbeiter">2020</a>""" in str(rv.data))
        assert ("""<a class="dropdown-item" href="/fehltage/stundensaldo/mitarbeiter/2019">2019</a>""" in str(rv.data))

        # Mitarbeiter Namens anzeige
        assert ("<h2>Mit Arbeiter</h2>" in str(rv.data))
