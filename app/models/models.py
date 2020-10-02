from flask_mongoengine import MongoEngine
from mongoengine import Q
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = MongoEngine()


# Alle Fehlzeiten eines Mitarbeiters werden im Mitarbeiterobjekt als Liste gespeichert
class Fehlzeit(db.EmbeddedDocument):
    datum_start = db.DateField()
    datum_ende = db.DateField()
    grund = db.StringField()
    id = db.StringField()

    # Daten aus einem "Fehlzeit eintragen"-Formular übernehmen
    def fill(self, form):
        self.datum_start = form.datum_start.data
        self.datum_ende = form.datum_ende.data
        self.grund = form.grund.data
        self.id = form.id.data


# Alle Zeitstempel eines Mitarbeiters werden im Mitarbeiterobjekt als Liste gespeichert
class Zeitstempel(db.EmbeddedDocument):
    eingestempelt = db.DateTimeField()
    ausgestempelt = db.DateTimeField()
    id = db.StringField()

    def ausstempeln(self):
        self.ausgestempelt = datetime.now()

    def einstempeln(self):
        self.eingestempelt = datetime.now()

    # Nächste Zeitstempel-ID aus den bisher in der Datenbank
    # eingetragenen Stempeln ermitteln und eintragen
    def set_id(self, mitarbeiter):
        zt = mitarbeiter.zeitstempel.filter()
        max_id = 0
        for z in zt:
            if max_id < int(z.id):
                max_id = int(z.id)
        self.id = str(max_id + 1)

    # Daten aus einem "Zeitstempel Bearbeiten"-Formular übernehmen
    def fill(self, form):
        self.eingestempelt = form.eingestempelt.data
        self.ausgestempelt = form.ausgestempelt.data
        self.id = form.id.data

    def validate_zeitstempel(self, mitarbeiter):
        # Ein Zeitstempelobjekt darf keine zwei Zeitstempel beinhalten die eine Zeitdifferenz von 12 Stunden haben
        diff = (self.ausgestempelt - self.eingestempelt).total_seconds()
        if diff >= 43200:
            return 'hours_difference'
        # Einstempel-Zeitstempel muss zeitlich vor dem Ausstempel-Zeitstempel liegen
        if self.eingestempelt < self.ausgestempelt:
            zt = mitarbeiter.zeitstempel.filter()
            # Zeitstempel muss für den Mitarbeiter einzigartig sein -> keine zwei gleiche Zeitstempel
            for z in zt:
                if z.id != self.id:
                    if self.eingestempelt < z.eingestempelt:
                        if self.ausgestempelt >= z.eingestempelt:
                            return 'belegt'
                    else:
                        if self.eingestempelt <= z.ausgestempelt:
                            return 'belegt'

            return 'true'
        return 'rahmen'


class Mitarbeiter(db.Document, UserMixin):
    nachname = db.StringField(required=True)
    vorname = db.StringField(required=True)
    username = db.StringField(required=True, unique=True)
    passwort_hash = db.StringField(required=True)
    rolle = db.StringField(required=True)
    aktiv = db.BooleanField(required=True)
    gebdat = db.DateField()
    geschlecht = db.StringField()
    email = db.EmailField()
    telefon = db.StringField()
    adresse_plz = db.StringField()
    adresse_ort = db.StringField()
    adresse_strasse = db.StringField()
    adresse_hausnr = db.StringField()
    stunden_pro_woche = db.IntField(required=True, default=40)
    urlaubstage = db.IntField(required=True, default=25)
    fehlzeiten = db.EmbeddedDocumentListField(Fehlzeit)
    zeitstempel = db.EmbeddedDocumentListField(Zeitstempel)

    def fill(self, form):
        self.nachname = form.nachname.data
        self.vorname = form.vorname.data
        self.username = form.username.data
        self.rolle = form.rolle.data
        self.aktiv = True
        self.gebdat = form.gebdat.data
        self.geschlecht = form.geschlecht.data
        self.email = form.email.data
        self.telefon = form.telefon.data
        self.adresse_plz = str(form.adresse_plz.data)
        self.adresse_ort = form.adresse_ort.data
        self.adresse_strasse = form.adresse_strasse.data
        self.adresse_hausnr = form.adresse_hausnr.data
        self.stunden_pro_woche = form.stunden_pro_woche.data
        self.urlaubstage = form.urlaubstage.data

    def set_password(self, password_plaintext):
        self.passwort_hash = generate_password_hash(password_plaintext)

    def check_password(self, password_plaintext):
        return check_password_hash(self.passwort_hash, password_plaintext)

    def __repr__(self):
        return f"[{self.username} ({self.vorname} {self.nachname}): {self.rolle}, aktiv: {self.aktiv}]"

    def string(self):
        return f"[{self.username} ({self.vorname} {self.nachname}): {self.rolle}, aktiv: {self.aktiv}]"

    def aktivieren(self):
        self.aktiv = True

    def deaktivieren(self):
        self.aktiv = False

    @staticmethod
    def suchen(suche):
        return Mitarbeiter.objects.filter(
            Q(username__icontains=suche) | Q(nachname__icontains=suche) | Q(vorname__icontains=suche))

    # implementiert von Gianni Rota (AP2)
    def set_fehlzeit_id(self, neue_fehlzeit):
        max_id = 0
        for fehlzeit in self.fehlzeiten:
            if max_id < int(fehlzeit.id):
                max_id = int(fehlzeit.id)

        neue_fehlzeit.id = str(max_id+1)

    # implementiert von Gianni Rota (AP2)
    # Fehlzeiteingabe prüfen und ggf. den Fehlergrund zurückgeben um eine dementsprechende Fehlermeldung anzeigen zu können
    def validate_fehlzeit(self, neue_fehlzeit):
        if neue_fehlzeit.datum_start <= neue_fehlzeit.datum_ende:
            for fehlzeit in self.fehlzeiten:
                if fehlzeit.id != neue_fehlzeit.id:
                    if neue_fehlzeit.datum_start < fehlzeit.datum_start:
                        if neue_fehlzeit.datum_ende >= fehlzeit.datum_start:
                            return 'occupied'
                    else:
                        if neue_fehlzeit.datum_start <= fehlzeit.datum_ende:
                            return 'occupied'

            return 'valid'

        return 'time_frame'
