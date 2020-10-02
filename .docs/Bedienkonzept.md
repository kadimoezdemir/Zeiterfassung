Projekt: Online-Mitarbeiterverwaltung

Auftraggeber:\
   Softwaretechnik Praktikum 2020\
   Hochschule Kempten\
   Bahnhofstr. 61, 87435 Kempten

Auftragnehmer:\
   Team D\
   Hochschule Kempten\
   Bahnhofstr. 61, 87435 Kempten

# Bedienkonzept

## UC3.1 Login

![UC3.1 Login](./Bedienkonzept/uc3-1.png)

## Startseite und Menüführung

### Mitarbeiter

Die Use Cases "Einstempeln", "Ausstempeln" und "Letzten Zeitstempel anzeigen" sind direkt in die Startseite integriert. Falls es beim Stempeln Komplikationen gibt, kann unter dem "Einstempeln/Ausstempeln"-Button eine Warnung mit entsprechenden Optionen angezeigt werden (dies wird im Bedienkonzept zu den entsprechenden Use Cases beschrieben).

In der oberen rechten Ecke werden zusätzlich zum hier abgebildeten "Logout"-Button noch der Benutzername des angemeldeten Mitarbeiters sowie die Rolle (Mitarbeiter/Personalsachbearbeiter), in der dieser angemeldet ist, angezeigt

![Startseite](./Bedienkonzept/StartseiteMA.png)

Unter "Meine Statistiken" findet der Mitarbeiter alle Auswertungsfunktionen zu seiner eigenen Arbeitszeit:

![Statistiken](./Bedienkonzept/MeineStatistiken.png)

### Personalsachbearbeiter

![Startseite](./Bedienkonzept/StartseitePSB.png)

Dem Personalsachbearbeiter wird ein zusätzlicher Menüpunkt "Personalmanagement" eingeblendet, unter dem er alle für ihn reservierten Funktionen findet:

![Personalmanagement](./Bedienkonzept/Personalmgmt.png)

Unter "Statistiken" kann der Personalsachbearbeiter Auswertungen zur Arbeitszeit der anderen Mitarbeiter durchführen:

![Statistiken](./Bedienkonzept/Statistiken.png)

## Use Cases

### AP1

#### UC1.1 Mitarbeiter anlegen
![UC1.1](./Bedienkonzept/uc1-1.png)

#### UC1.2 Mitarbeiter suchen
![UC1.2](./Bedienkonzept/uc1-2.png)

Im Gegensatz zur obigen Darstellung wird in der Benutzeroberfläche des Produkts kein "Optionen"-Dropdown verwendet, sondern die passenden Optionen werden direkt als Icons dargestellt.

#### UC1.3 Mitarbeiterdaten ändern
![UC1.3](./Bedienkonzept/uc1-3.png)

#### UC1.4 Mitarbeiter deaktivieren
![UC1.4](./Bedienkonzept/uc1-4.png)

#### UC1.5 Mitarbeiter aktivieren
![UC1.5](./Bedienkonzept/uc1-5.png)



### AP2

#### UC2.1 Fehltag hinzufügen
![UC2.1](./Bedienkonzept/uc2-1.png)

#### UC2.2 Fehltage ändern
![UC2.2](./Bedienkonzept/uc2-2.png)

#### UC2.3 Fehltage löschen
![UC2.3](./Bedienkonzept/uc2-3.png)

#### UC2.4 Filtereinstellungen ändern
![UC2.4](./Bedienkonzept/uc2-4.png)

#### UC2.5 Sortierverfahren ändern
![UC2.5](./Bedienkonzept/uc2-5.png)

#### UC2.6 Mitarbeiter auswählen
![UC2.6](./Bedienkonzept/uc2-6.png)



### AP4

#### UC4.1 Einstempeln
![UC4.1](./Bedienkonzept/UC4.1.png)

#### UC4.2 Ausstempeln
![UC4.2](./Bedienkonzept/UC4.2.png)

#### UC4.3 Letzten Zeitstempel anzeigen
![UC4.3](./Bedienkonzept/UC4.3.png)

#### UC4.4 Zeitstempel auflisten
![UC4.4](./Bedienkonzept/UC4.4.png)

#### UC4.5 Zeitstempel bearbeiten
![UC4.5](./Bedienkonzept/UC4.5.png)



### AP5

#### UC5.1 Anwesenheitstableau aufrufen
![UC5.1](./Bedienkonzept/uc5-1.jpg)

#### UC5.2 Eigene Arbeitstage-Jahresübersicht aufrufen
![UC5.2](./Bedienkonzept/uc5-2.jpg)

#### UC5.3 Beliebige Arbeitstage-Jahresübersicht aufrufen
![UC5.3](./Bedienkonzept/uc5-3.jpg)



### AP6

#### UC6.1 Eigene Jahres-Stunden-Übersicht einsehen
![UC6.1](./Bedienkonzept/uc6-1.png)

#### UC6.2 Eigenen aktuellen Stundensaldo einsehen
![UC6.2](./Bedienkonzept/uc6-2.png)

#### UC6.3 Jahres-Stunden-Übersicht eines bestimmten Mitarbeiters einsehen
![UC6.3](./Bedienkonzept/uc6-3.png)

#### UC6.4 Stundensaldo von bestimmten Mitarbeiter einsehen
![UC6.4](./Bedienkonzept/uc6-4.png)

## UC3.2 Logout

![UC3.2 Logout](./Bedienkonzept/uc3-2.png)
