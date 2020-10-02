from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, PasswordField, IntegerField, HiddenField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from app.models.models import Mitarbeiter


# Validator, der die Verfügbarkeit eines Usernames prüft
def check_mitarbeiter_unique(form, field):
    if Mitarbeiter.objects(username=form.username.data).first() is not None:
        raise ValidationError('username bereits vergeben')


# Formular zum Anlegen eines neuen Mitarbeiters
# bzw. in erweiterter Form zum Bearbeiten eines existierenden Mitarbeiters (siehe unten)
class MitarbeiterForm(FlaskForm):
    nachname = StringField("Nachname", validators=[DataRequired(message="Nachname darf nicht leer sein")])
    vorname = StringField("Vorname", validators=[DataRequired(message="Vorname darf nicht leer sein")])
    username = StringField("Username", validators=[DataRequired(message="Username darf nicht leer sein"), check_mitarbeiter_unique])
    passwort = PasswordField("Passwort", validators=[DataRequired(message="Passwort darf nicht leer sein")])
    passwort_wiederholen = PasswordField(
        "Passwort wiederholen",
        validators=[DataRequired(message="Passwort darf nicht leer sein"), EqualTo('passwort', message='Passwörter müssen gleich sein')]
    )
    rolle = SelectField(
        "Rolle",
        choices=[("Mitarbeiter", "Mitarbeiter"), ("Personalsachbearbeiter", "Personalsachbearbeiter")],
        default="Mitarbeiter"
    )
    gebdat = DateField("Geburtsdatum", validators=[DataRequired(message="Bitte Geburtsdatum angeben")], format='%Y-%m-%d')
    geschlecht = SelectField("Geschlecht", choices=[
        ("androgyner Mensch", "androgyner Mensch"),
        ("androgyn", "androgyn"),
        ("bigender", "bigender"),
        ("weiblich", "weiblich"),
        ("Frau zu Mann (FzM)", "Frau zu Mann (FzM)"),
        ("gender variabel", "gender variabel"),
        ("genderqueer", "genderqueer"),
        ("intersexuell (auch inter*)", "intersexuell (auch inter*)"),
        ("männlich", "männlich"),
        ("Mann zu Frau (MzF)", "Mann zu Frau (MzF)"),
        ("weder noch", "weder noch"),
        ("geschlechtslos", "geschlechtslos"),
        ("nicht-binär", "nicht-binär"),
        ("weitere", "weitere"),
        ("Pangender", "Pangender"),
        ("Pangeschlecht", "Pangeschlecht"),
        ("trans", "trans"),
        ("transweiblich", "transweiblich"),
        ("transmännlich", "transmännlich"),
        ("Transmann", "Transmann"),
        ("Transmensch", "Transmensch"),
        ("Transfrau", "Transfrau"),
        ("trans*", "trans*"),
        ("trans*weiblich", "trans*weiblich"),
        ("trans*männlich", "trans*männlich"),
        ("Trans*Mann", "Trans*Mann"),
        ("Trans*Mensch", "Trans*Mensch"),
        ("Trans*Frau", "Trans*Frau"),
        ("transfeminin", "transfeminin"),
        ("Transgender", "Transgender"),
        ("transgender weiblich", "transgender weiblich"),
        ("transgender männlich", "transgender männlich"),
        ("Transgender Mann", "Transgender Mann"),
        ("Transgender Mensch", "Transgender Mensch"),
        ("Transgender Frau", "Transgender Frau"),
        ("transmaskulin", "transmaskulin"),
        ("transsexuell", "transsexuell"),
        ("weiblich-transsexuell", "weiblich-transsexuell"),
        ("männlich-transsexuell", "männlich-transsexuell"),
        ("transsexueller Mann", "transsexueller Mann"),
        ("transsexuelle Person", "transsexuelle Person"),
        ("transsexuelle Frau", "transsexuelle Frau"),
        ("Inter*", "Inter*"),
        ("Inter*weiblich", "Inter*weiblich"),
        ("Inter*männlich", "Inter*männlich"),
        ("Inter*Mann", "Inter*Mann"),
        ("Inter*Frau", "Inter*Frau"),
        ("Inter*Mensch", "Inter*Mensch"),
        ("intergender", "intergender"),
        ("intergeschlechtlich", "intergeschlechtlich"),
        ("zweigeschlechtlich", "zweigeschlechtlich"),
        ("Zwitter", "Zwitter"),
        ("Hermaphrodit", "Hermaphrodit"),
        ("Two Spirit drittes Geschlecht", "Two Spirit drittes Geschlecht"),
        ("Viertes Geschlecht", "Viertes Geschlecht"),
        ("XY-Frau", "XY-Frau"),
        ("Butch (maskuliner Typ in einer lesbischen Beziehung)", "Butch (maskuliner Typ in einer lesbischen Beziehung)"),
        ("Femme (femininer Typ in einer lesbischen Beziehung)", "Femme (femininer Typ in einer lesbischen Beziehung)"),
        ("Drag", "Drag"),
        ("Transvestit", "Transvestit"),
        ("Cross-Gender", "Cross-Gender")
    ], default="geschlechtslos")
    email = StringField("E-Mail", validators=[DataRequired(message="Email darf nicht leer sein"), Email("Keine Email-Adresse")])
    telefon = StringField("Telefon", validators=[DataRequired("Telefonnummer darf nicht leer sein")])
    adresse_plz = IntegerField("PLZ", validators=[DataRequired(message="PLZ darf nicht leer sein")])
    adresse_ort = StringField("Ort", validators=[DataRequired(message="Ort darf nicht leer sein")])
    adresse_strasse = StringField("Straße", validators=[DataRequired(message="Straße darf nicht leer sein")])
    adresse_hausnr = StringField("Hausnummer", validators=[DataRequired(message="Hausnummer darf nicht leer sein")])
    stunden_pro_woche = IntegerField("Stunden/Woche", default=40, validators=[DataRequired(message="Bitte Stundenzahl angeben")])
    urlaubstage = IntegerField("Urlaubstage/Jahr", default=25, validators=[DataRequired(message="Bitte Urlaubstagezahl angeben")])
    submit = SubmitField("Bestätigen")


# Bearbeitungsformular für bereits existierende Mitarbeiter
# Versteckt das Username-Feld, weil der Username eines Mitarbeiters sich nicht ändern darf
# Ermöglicht es, das Passwort-Feld freizulassen, falls dieses nicht geändert werden soll
class MitarbeiterBearbeitenForm(MitarbeiterForm):
    username = HiddenField("Username")
    passwort = PasswordField("Passwort")
    passwort_wiederholen = PasswordField(
        "Passwort wiederholen",
        validators=[EqualTo('passwort', message='Passwörter müssen gleich sein')]
    )

    # Eintragen von Preset-Werten auf Basis eines Mitarbeiter-Objekts
    def fill(self, mitarbeiter: Mitarbeiter):
        self.nachname.data = mitarbeiter.nachname
        self.vorname.data = mitarbeiter.vorname
        self.username.data = mitarbeiter.username
        self.rolle.data = mitarbeiter.rolle
        self.gebdat.data = mitarbeiter.gebdat
        self.geschlecht.data = mitarbeiter.geschlecht
        self.email.data = mitarbeiter.email
        self.telefon.data = mitarbeiter.telefon
        self.adresse_plz.data = mitarbeiter.adresse_plz
        self.adresse_ort.data = mitarbeiter.adresse_ort
        self.adresse_strasse.data = mitarbeiter.adresse_strasse
        self.adresse_hausnr.data = mitarbeiter.adresse_hausnr
        self.stunden_pro_woche.data = mitarbeiter.stunden_pro_woche
        self.urlaubstage.data = mitarbeiter.urlaubstage


# Formular zur Mitarbeitersuche
# Abbrechen-Button ist im HTML-Template als Link enthalten
class MitarbeiterSuchen(FlaskForm):
    suche = StringField(validators=[DataRequired(message="Suchfeld darf nicht leer sein")])
    submit = SubmitField("Suche starten")


# Formular zum Bestätigen der Aktivierung eines Mitarbeiters
# Abbrechen-Button ist im HTML-Template als Link enthalten
class MitarbeiterAktivierenForm(FlaskForm):
    bestaetigen = SubmitField("Bestätigen")


# Formular zum Bestätigen der Deaktivierung eines Mitarbeiters
# Abbrechen-Button ist im HTML-Template als Link enthalten
class MitarbeiterDeaktivierenForm(FlaskForm):
    bestaetigen = SubmitField("Bestätigen")