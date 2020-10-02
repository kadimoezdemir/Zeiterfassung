from flask_script.commands import Command
from datetime import datetime, timedelta
import radar
import random
from app.models.models import *

fz_grund = [
    "Home-Office",
    "Erkrankung",
    "Urlaub",
    "Zeitausgleich"
]

ma_gen = {
    "nachname": [
        "Rüdiger",
        "Fahri",
        "Müller",
        "Maier",
        "Mayer",
        "Meier",
        "Meyer",
        "Majer",
        "Mayor",
        "Major",
        "Maher",
        "Paulaner",
        "Augustiner",
        "Matik",
        "Jovanovitsch"
    ],
    "vorname": [
        "Antonio",
        "August",
        "Paul",
        "Herr",
        "Paula",
        "Pauline",
        "Augustine",
        "Tim",
        "Tina",
        "Florentine",
        "Fahri",
        "Kork",
        "Giovanni",
        "Valeria"
    ],
    "rolle": [
        "Mitarbeiter",
        "Personalsachbearbeiter"
    ],
    "geschlecht": [
        "Butch",
        "Femme",
        "Two Spirit Drittes Geschlecht",
        "transmännlich",
        "transmenschlich",
        "transweiblich",
        "trans",
        "trans*"
    ],
    "adresse_ort": [
        "Ort 1",
        "Ort B",
        "Ort c"
    ]
}


class FillDB(Command):
    def run(self):
        # Mitarbeiter fuer Tests erstellen
        ma = Mitarbeiter()
        ma.nachname = "Sachbearbeiter"
        ma.vorname = "Personal"
        ma.username = "personalsachbearbeiter"
        ma.set_password("test")
        ma.rolle = "Personalsachbearbeiter"
        ma.aktiv = True
        ma.gebdat = radar.random_datetime()
        ma.geschlecht = random.choice(ma_gen["geschlecht"])
        ma.email = "test@web.de"
        ma.telefon = str(random.randint(100000, 9000000))
        ma.adresse_plz = str(random.randint(0, 99999))
        ma.adresse_ort = random.choice(ma_gen["adresse_ort"])
        ma.adresse_strasse = "Straße"
        ma.adresse_hausnr = str(random.randint(1, 100))
        ma.stunden_pro_woche = random.randint(25, 40)
        ma.urlaubstage = random.randint(18, 27)
        ma.save()

        ma = Mitarbeiter()
        ma.nachname = "Arbeiter"
        ma.vorname = "Mit"
        ma.username = "mitarbeiter"
        ma.set_password("test")
        ma.rolle = "Mitarbeiter"
        ma.aktiv = True
        ma.gebdat = radar.random_datetime()
        ma.geschlecht = random.choice(ma_gen["geschlecht"])
        ma.email = "test@web.de"
        ma.telefon = str(random.randint(100000, 9000000))
        ma.adresse_plz = str(random.randint(0, 99999))
        ma.adresse_ort = random.choice(ma_gen["adresse_ort"])
        ma.adresse_strasse = "Straße"
        ma.adresse_hausnr = str(random.randint(1, 100))
        ma.stunden_pro_woche = random.randint(25, 40)
        ma.urlaubstage = random.randint(18, 27)
        ma.save()

        # zufaellige Mitarbeiter erstellen
        for i in range(50):
            ma = Mitarbeiter()
            ma.nachname = random.choice(ma_gen["nachname"])
            ma.vorname = random.choice(ma_gen["vorname"])
            ma.username = ma.vorname + ma.nachname + str(random.randint(0, 10000))
            ma.set_password("test")
            ma.rolle = random.choice(ma_gen["rolle"])
            ma.aktiv = random.choice([True, False])
            ma.gebdat = radar.random_datetime()
            ma.geschlecht = random.choice(ma_gen["geschlecht"])
            ma.email = "test@web.de"
            ma.telefon = str(random.randint(100000, 9000000))
            ma.adresse_plz = str(random.randint(0, 99999))
            ma.adresse_ort = random.choice(ma_gen["adresse_ort"])
            ma.adresse_strasse = "Straße"
            ma.adresse_hausnr = str(random.randint(1, 100))
            ma.stunden_pro_woche = random.randint(25, 40)
            ma.urlaubstage = random.randint(18, 27)
            ma.save()

        ma = Mitarbeiter.objects()

        for m in ma:
            for i in range(5, 10):
                f = Fehlzeit()
                f.grund = random.choice(fz_grund)
                f.datum_start = radar.random_datetime(start='2010-01-01T00:00:00')
                f.datum_ende = f.datum_start + timedelta(days=random.randint(0, 10))
                m.set_fehlzeit_id(f)
                m.fehlzeiten.append(f)
                m.save()
            for i in range(20, 30):
                z = Zeitstempel()
                z.eingestempelt = radar.random_datetime(start='2010-01-01T00:00:00')
                z.ausgestempelt = z.eingestempelt + timedelta(hours=random.randint(1, 10))
                z.set_id(m)
                m.zeitstempel.append(z)
                m.save()