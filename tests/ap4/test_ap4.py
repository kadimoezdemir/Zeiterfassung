import pytest
from app.models.models import Mitarbeiter
from tests.ap1.test_ap1 import create_ulrich25

# create_ulrich25() wird aus test_ap1 benutzt um einen neuen Mitarbeiter zu erstellen
# Er wird in der Datenbank angelegt, damit er als neuer User getestet werden kann
@pytest.mark.usefixtures("client", "app")
class TestAP4:
    # 1. Test: Einstempeln
    def test_einstempeln(self, client, app):
        """ User kann sich einstempeln """
        test_user = Mitarbeiter.objects(username='mitarbeiter').first()

        @app.login_manager.request_loader
        def load_user_from_request(request):
            return test_user

        rv = client.get('/', follow_redirects=True)

        assert rv.status_code == 200
        assert("Einstempeln" in str(rv.data))


    # 2. Test: Ausstempeln
    def test_ausstempeln(self, client, app):
        """ User kann sich ausstempeln """
        test_user = Mitarbeiter.objects(username='mitarbeiter').first()

        @app.login_manager.request_loader
        def load_user_from_request(request):
            return test_user

        rv = client.get('/', follow_redirects=True)

        assert rv.status_code == 200
        assert("Ausstempeln" in str(rv.data))

        # Ausstempelung vergessen Meldung
        assert("Ausstempeln vergessen?" in str(rv.data))


    # 3. Test: letzter Zeitstempel
    def test_letzter_zeitstempel(self, client, app):
        """ Letzter Zeitstempel wird angezeigt """
        test_user = Mitarbeiter.objects(username='mitarbeiter').first()

        @app.login_manager.request_loader
        def load_user_from_request(request):
            return test_user

        rv = client.get('/', follow_redirects=True)

        assert rv.status_code == 200
        assert("Zuletzt" in str(rv.data))


    # 4. Test: Meine Zeitstempel
    def test_meine_zeitstempel(self, client, app):
        test_user = Mitarbeiter.objects(username='mitarbeiter').first()

        @app.login_manager.request_loader
        def load_user_from_request(request):
            return test_user

        rv = client.get('/meine_zeitstempel', follow_redirects=True)

        assert rv.status_code == 200
        assert("Zeitstempel filter vom" in str(rv.data))
        assert("filtern" in str(rv.data))
        assert ("Eingestempelt" in str(rv.data))
        assert ("Ausgestempelt" in str(rv.data))


    # 5. Test: Zeitstempel bearbeiten/Übersicht
    def test_zeitstempel_bearbeiten(self, client, app):
        """ Uebersicht "Zeitstempel bearbeiten" von User "mitarbeiter" """
        test_user = Mitarbeiter.objects(username='personalsachbearbeiter').first()

        @app.login_manager.request_loader
        def load_user_from_request(request):
            return test_user

        rv = client.get('/zeitstempel/uebersicht/mitarbeiter', follow_redirects=True)

        assert rv.status_code == 200
        assert("Mit Arbeiter" in str(rv.data))
        assert ("Bearbeiten" in str(rv.data))
        assert ("Eingestempelt" in str(rv.data))
        assert ("Ausgestempelt" in str(rv.data))

    # 6. Test: Bearbeitung eines Zeitstempels
    def test_zeitstempel_bearbeitung(self, client, app):
        """ Ein Zeitstempel wird verändert """
        test_user = Mitarbeiter.objects(username='personalsachbearbeiter').first()

        @app.login_manager.request_loader
        def load_user_from_request(request):
            return test_user

        rv = client.get('/zeitstempel/bearbeiten/mitarbeiter/1', follow_redirects=True)

        assert rv.status_code == 200
        assert ("Eingestempelt:" in str(rv.data))
        assert ("Ausgestempelt:" in str(rv.data))


# Die folgenden Tests werden mit dem User Ulrich26 durchgeführt, der keine Zeitstempel besitzt
    # 1. Test: Einstempeln
    def test_einstempeln_new_user(self, client, app):
        """ User kann sich einstempeln """
        create_ulrich25()
        test_user = Mitarbeiter.objects(username='ulrich25').first()

        @app.login_manager.request_loader
        def load_user_from_request(request):
            return test_user

        rv = client.get('/', follow_redirects=True)

        assert rv.status_code == 200
        assert ("Einstempeln" in str(rv.data))
        Mitarbeiter.objects(username="ulrich25").delete()


    # 2. Test: Austempeln
    def test_ausstempeln_new_user(self, client, app):
        """ User kann sich ausstempeln """
        create_ulrich25()
        test_user = Mitarbeiter.objects(username='ulrich25').first()

        @app.login_manager.request_loader
        def load_user_from_request(request):
            return test_user

        rv = client.get('/', follow_redirects=True)

        assert rv.status_code == 200
        assert("Ausstempeln" in str(rv.data))

        # Ausstempelung vergessen Meldung
        assert("Ausstempeln vergessen?" in str(rv.data))
        Mitarbeiter.objects(username="ulrich25").delete()


    # 3. Test: letzter Zeitstempel
    def test_letzter_zeitstempel_new_user(self, client, app):
        """ Letzter Zeitstempel wird angezeigt """
        create_ulrich25()
        test_user = Mitarbeiter.objects(username='ulrich25').first()

        @app.login_manager.request_loader
        def load_user_from_request(request):
            return test_user

        rv = client.get('/', follow_redirects=True)

        assert rv.status_code == 200
        assert("Keine Zeitstempel vorhanden" in str(rv.data))
        Mitarbeiter.objects(username="ulrich25").delete()


    # 4. Test: Meine Zeitstempel
    def test_meine_zeitstempel_new_user(self, client, app):
        """ Zeitstempelliste wird angezeigt, von User "ulrich25" """
        create_ulrich25()
        test_user = Mitarbeiter.objects(username='ulrich25').first()

        @app.login_manager.request_loader
        def load_user_from_request(request):
            return test_user

        rv = client.get('/meine_zeitstempel', follow_redirects=True)

        assert rv.status_code == 200
        assert ("Zeitstempel filter vom" in str(rv.data))
        assert ("filtern" in str(rv.data))
        assert ("Eingestempelt" in str(rv.data))
        assert ("Ausgestempelt" in str(rv.data))
        assert ("Keine Zeitstempel vorhanden" in str(rv.data))
        Mitarbeiter.objects(username="ulrich25").delete()


    # 5. Test: Zeitstempel bearbeiten/Übersicht
    def test_zeitstempel_bearbeiten_new_user(self, client, app):
        """ Uebersicht "Zeitstempel bearbeiten" von User "ulrich25" """
        create_ulrich25()
        test_user = Mitarbeiter.objects(username='personalsachbearbeiter').first()

        @app.login_manager.request_loader
        def load_user_from_request(request):
            return test_user

        rv = client.post('/zeitstempel/uebersicht/ulrich25', follow_redirects=True)

        assert rv.status_code == 200
        assert ("Keine Zeitstempel vorhanden" in str(rv.data))
        Mitarbeiter.objects(username="ulrich25").delete()
