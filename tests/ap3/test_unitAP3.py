import pytest

from flask_login import current_user
from flask import Blueprint
from app.main.forms import ROLE_REQ_ON
import app.main.forms
from flask_login import current_user, login_user

from app.models.models import Mitarbeiter

from tests.conftest import create_app
@pytest.mark.usefixtures("client", "app")
class TestAP3:

#Test1: Erreichbarkeit der URL /login
    def test_reach_login(self, client, app):
        """ Tests if the login page loads """

        rv = client.get('/login', follow_redirects=True)
        assert rv.status_code == 200

#Test2: Loginversuch mit korrekten Daten
    def test_correct_login(self, client, app):
        """Tests if the login works with right data"""


        rv = client.post('/login', data=dict(
            username='mitarbeiter',
            password="test"
        ), follow_redirects=True)
        assert rv.status_code == 200
        #falls Fehlermeldung nicht gefunden wurde, ist Login erfolgreich
        assert "Passwort oder Mitarbeiter ID falsch " not in str(rv.data)



#Test3: Loginversuch mit falschem Passwort
    def test_wrongpw_login(self, client, app):
        """Tests if the login works with wrong password"""
        rv = client.post('/login', data=dict(
            username='mitarbeiter',
            password='joiefjoimvteuoi'
        ), follow_redirects=True)
        assert rv.status_code == 200
        # Fehlermeldung muss angezeigt werden, sonst schlägt Test fehl
        assert "Passwort oder Mitarbeiter ID falsch" in str(rv.data)

#Test4: Loginversuch mit leerem Passwort
    def test_leerpw_login(self, client, app):
        """Tests if the login works with an empty password"""

        rv = client.post('/login', data=dict(
            username='mitarbeiter',
            password=''
        ), follow_redirects=True)
        assert rv.status_code == 200
        # Fehlermeldung muss angezeigt werden, sonst schlägt Test fehl
        assert "Passwort oder Mitarbeiter ID falsch" in str(rv.data)

#Test5: Loginversuch mit nichtexistentem Usernamen
    def test_wrongname_login(self, client, app):
        """Tests if the login works with an nonexistant username"""

        rv = client.post('/login', data=dict(
            username='toter-mitarbeiter',
            password='test'
        ), follow_redirects=True)
        assert rv.status_code == 200
        # Fehlermeldung muss angezeigt werden, sonst schlägt Test fehl
        assert "Passwort oder Mitarbeiter ID falsch" in str(rv.data)

#Test6: Loginversuch mit deaktiviertem User
    def test_deactivatedname_login(self, client, app):
        """Tests if the login works with an deactivated username and correct password"""

        # User muss davor in Datenbank sein
        rv = client.post('/login', data=dict(
            username='deactivated',
            password='test'
        ), follow_redirects=True)
        assert rv.status_code == 200
        # Fehlermeldung muss angezeigt werden, sonst schlägt Test fehl
        assert "Dieser Account wurde deaktiviert." in str(rv.data)

#Test7: Erreichbarkeit der URL /logout
    def test_reach_logout(self, client, app):
        """ Tests if the logout page loads """

        rv = client.get('/logout')
        assert rv.status_code == 302

#Test69: Riecks Test
    def test_mitarbeiter_neu_login_personalsachbearbeiter_1_1_a(self, client, app):
        test_user = Mitarbeiter.objects(username='personalsachbearbeiter').first()

        @app.login_manager.request_loader
        def load_user_from_request(request):
            return test_user

        rv = client.get('/mitarbeiter/neu', follow_redirects=True)
        assert rv.status_code == 200
        assert ("Mitarbeiter anlegen" in str(rv.data))

        rv = client.get('/personalmanagement', follow_redirects=True)
        assert rv.status_code == 200
        assert("Neuer Mitarbeiter" in str(rv.data))




