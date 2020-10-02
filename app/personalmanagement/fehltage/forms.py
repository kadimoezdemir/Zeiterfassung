from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, SelectField
from wtforms.validators import DataRequired
from datetime import datetime, timedelta, date


# Formular zum Eintragen und/oder Bearbeiten von Fehlzeiten
class FehlzeitForm(FlaskForm):
    datum_start = DateField("Datum von", validators=[DataRequired()], format='%Y-%m-%d')
    datum_ende = DateField("bis", validators=[DataRequired()], format='%Y-%m-%d')
    grund = SelectField("Grund", choices=[("Erkrankung", "Erkrankung"), ("Home-Office", "Home-Office"),
                                          ("Urlaub", "Urlaub"), ("Zeitausgleich", "Zeitausgleich")],
                                            validators=[DataRequired()])
    submit = SubmitField("Speichern")
    id = StringField(validators=[DataRequired()])

    def fill(self, fehlzeit):
        self.grund.data = fehlzeit.grund
        self.id.data = fehlzeit.id
        self.datum_start.data = fehlzeit.datum_start
        self.datum_ende.data = fehlzeit.datum_ende


# Formular zum Filtern der Fehlzeiten
class FilterForm(FlaskForm):
    radio = StringField(validators=[DataRequired()])
    datum_tag = DateField("Datum", format='%Y-%m-%d')
    datum_woche = DateField("Datum", format='%Y-%m-%d')
    datum_start = DateField("Datum von", format='%Y-%m-%d')
    datum_ende = DateField("bis", format='%Y-%m-%d')

    monat = SelectField("Monat", choices=[("1", "Januar"), ("2", "Februar"),
                                          ("3", "März"), ("4", "April"), ("5", "Mai"), ("6", "Juni"),
                                          ("7", "Juli"), ("8", "August"), ("9", "September"),
                                          ("10", "Oktober"), ("11", "November"), ("12", "Dezember")])
    jahr_woche = SelectField("Jahr", choices=[("2020", "2020"), ("2019", "2019"),
                                          ("2018", "2018"), ("2017", "2017"), ("2016", "2016"), ("2015", "2015"),
                                          ("2014", "2014"), ("2013", "2013"), ("2012", "2012"),
                                          ("2011", "2011"), ("2010", "2010"), ("2009", "2009")])

    jahr_monat = SelectField("Jahr", choices=[("2020", "2020"), ("2019", "2019"),
                                          ("2018", "2018"), ("2017", "2017"), ("2016", "2016"), ("2015", "2015"),
                                          ("2014", "2014"), ("2013", "2013"), ("2012", "2012"),
                                          ("2011", "2011"), ("2010", "2010"), ("2009", "2009")])
    jahr_jahr = SelectField("Jahr", choices=[("2020", "2020"), ("2019", "2019"),
                                        ("2018", "2018"), ("2017", "2017"), ("2016", "2016"), ("2015", "2015"),
                                        ("2014", "2014"), ("2013", "2013"), ("2012", "2012"),
                                        ("2011", "2011"), ("2010", "2010"), ("2009", "2009")])
    kalenderwoche = StringField("Kalenderwoche")
    kw_datum_start = DateField(format='%Y-%m-%d')
    kw_datum_ende = DateField(format='%Y-%m-%d')
    grund = StringField()

    erkrankung = StringField()
    home_office = StringField()
    urlaub = StringField()
    zeitausgleich = StringField()

    submit = SubmitField("Anwenden")

    def validiere_filter(self):
        if self.radio.data == 'unbegrenzt':
            # keine falschen Eingaben möglich
            return True

        elif self.radio.data == 'tag':
            # Datum muss vorhanden sein
            if self.datum_tag.data is not None:
                return True
            else:
                return False

        elif self.radio.data == 'woche':
            # es muss entweder ein Datum oder Kalenderwoche und Jahr vorhanden sein
            if self.datum_woche.data is not None:
                return True
            elif self.kalenderwoche.data and self.jahr_woche.data is not None:
                return True
            else:
                return False

        elif self.radio.data == 'monat':
            # es muss ein Monat und ein Jahr gewählt sein
            if self.monat.data and self.jahr_monat.data is not None:
                return True
            else:
                return False

        elif self.radio.data == 'jahr':
            # es muss ein Jahr ausgewählt sein
            if self.jahr_jahr.data is not None:
                return True
            else:
                return False

        elif self.radio.data == 'beliebig':
            # es müssen zwei Daten angegeben sein die einen gültigen Zeitraum ergeben
            if self.datum_start.data and self.datum_ende.data is not None:
                if self.datum_start.data <= self.datum_ende.data:
                    return True
                else:
                    return False

    def use_filter(self, fehlzeiten):
        # Ergebnis
        gefilterte_fehlzeiten = None

        # Radiobutton-Filtereingaben auf Fehlzeiten anwenden
        if self.radio.data == 'unbegrenzt':
            radio_fehlzeiten = fehlzeiten

        elif self.radio.data == 'tag':
            # finde Fehlzeit die diesen Tag beinhaltet
            radio_fehlzeiten = [x for x in fehlzeiten if x.datum_start <= self.datum_tag.data <= x.datum_ende]

        elif self.radio.data == 'woche':
            # finde das Anfangs- und Enddatum der Woche
            if self.kalenderwoche.data and self.jahr_woche.data is not None:
                self.setze_wochen_anfang_und_ende_fuer_kalenderwoche(int(self.jahr_woche.data),
                                                                     int(self.kalenderwoche.data))
            elif self.datum_woche.data is not None:
                self.setze_wochen_anfang_und_ende_fuer_datum()

            # finde alle Fehlzeiten in dieser Woche
            radio_fehlzeiten = [x for x in fehlzeiten if
                                (self.kw_datum_start.data <= x.datum_start <= self.kw_datum_ende.data)
                                or (self.kw_datum_ende.data >= x.datum_ende >= self.kw_datum_start.data)]

        elif self.radio.data == 'monat':
            radio_fehlzeiten = [x for x in fehlzeiten if
                    (x.datum_start.year == int(self.jahr_monat.data) or x.datum_ende.year == int(self.jahr_monat.data))
                    and (x.datum_start.month == int(self.monat.data) or x.datum_ende.month == int(self.monat.data))]

        elif self.radio.data == 'jahr':
            radio_fehlzeiten = [x for x in fehlzeiten if  x.datum_start.year == int(self.jahr_jahr.data)
                                                        or x.datum_ende.year == int(self.jahr_jahr.data)]

        elif self.radio.data == 'beliebig':
            # finde alle Fehlzeiten in dem angegebenen Zeitraum
            radio_fehlzeiten = [x for x in fehlzeiten if
                                (self.datum_start.data <= x.datum_start <= self.datum_ende.data)
                                or (self.datum_ende.data >= x.datum_ende >= self.datum_start.data)]

        # Checkbox-Filtereingaben auf bereits nach Radiobutton gefilterte Eingaben anwenden
        if self.erkrankung.data == 'true':
            # finde alle Fehlzeiten mit dem Grund Erkrankung aus den bereits gefilterten Ergebnissen
            erkrankungen = [x for x in radio_fehlzeiten if x.grund == 'Erkrankung']
            if gefilterte_fehlzeiten is None:
                gefilterte_fehlzeiten = erkrankungen
            # wenn bereits Ergebnisse vorhanden sind, füge die neuen hinzu ohne die alten zu überschreiben
            else:
                gefilterte_fehlzeiten += erkrankungen

        if self.home_office.data == 'true':
            homeoffices = [x for x in radio_fehlzeiten if x.grund == 'Home-Office']
            if gefilterte_fehlzeiten is None:
                gefilterte_fehlzeiten = homeoffices
            else:
                gefilterte_fehlzeiten += homeoffices

        if self.urlaub.data == 'true':
            urlaube = [x for x in radio_fehlzeiten if x.grund == 'Urlaub']
            if gefilterte_fehlzeiten is None:
                gefilterte_fehlzeiten = urlaube
            else:
                gefilterte_fehlzeiten += urlaube

        if self.zeitausgleich.data == 'true':
            zeitausgleiche = [x for x in radio_fehlzeiten if x.grund == 'Zeitausgleich']
            if gefilterte_fehlzeiten is None:
                gefilterte_fehlzeiten = zeitausgleiche
            else:
                gefilterte_fehlzeiten += zeitausgleiche

        if gefilterte_fehlzeiten is None:
            gefilterte_fehlzeiten = radio_fehlzeiten

        return gefilterte_fehlzeiten

    def setze_wochen_anfang_und_ende_fuer_datum(self):
        # setze den gewünschten Tag
        datum = date(self.datum_woche.data.year, self.datum_woche.data.month, self.datum_woche.data.day)
        # erster Wochentag = gewähltes Datum - Wochentag des Datums
        start = datum - timedelta(days=datum.weekday())
        # letzter Wochentag = erster Wochentag + 6
        ende = start + timedelta(days=6)

        # speichere Ergebnisse
        self.kw_datum_start.data = start
        self.kw_datum_ende.data = ende

    def setze_wochen_anfang_und_ende_fuer_kalenderwoche(self, jahr, woche):
        # setze datum auf den ersten Tag im Jahr
        datum = date(jahr, 1, 1)
        # bestimme ersten Wochentag des Jahres
        if datum.weekday() > 3:
            datum = datum + timedelta(7 - datum.weekday())
        else:
            datum = datum - timedelta(datum.weekday())

        # Verschiebung zum ersten Wochentag der gewünschten Woche
        delta = timedelta(days=(woche - 1) * 7)
        # erster Wochentag der gewünschten Woche = erster Wochentag des Jahres + Verschiebung zur gewünschten Woche
        start = datum + delta
        # letzter Wochentag = erster Wochentag + 6
        ende = start + timedelta(days=6)

        # speichere Ergebnisse
        self.kw_datum_start.data = start
        self.kw_datum_ende.data = ende



