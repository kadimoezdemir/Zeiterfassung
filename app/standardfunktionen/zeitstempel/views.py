from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import current_user
from datetime import datetime, date, time
import calendar
from functools import reduce
from app.models.models import Mitarbeiter, Zeitstempel
from app.main.forms import role_req

# define the blueprint
meine_zeitstempel = Blueprint('meine_zeitstempel', __name__, template_folder='pages')


# all routes
@meine_zeitstempel.route('/', methods=["GET", "POST"])
@role_req('Mitarbeiter', 'Personalsachbearbeiter')
def home():
    global ztstart, ztend, ma
    ma = Mitarbeiter.objects(username=current_user.username).first()
    zt = ma.zeitstempel
    ca = calendar

    # Filterfunktion
    if request.method == "POST":
        if request.form["submitButton"] == 'alle anzeigen':
            return render_template("meine_zeitstempel.html", ca=ca, ma=ma, zt=zt, info=session)
        elif request.form["submitButton"] == 'filtern':
            strstart = request.form["start"]
            strtend = request.form["end"]
            if (strstart == "") or (strtend == ""):
                flash("Bitte beide Felder füllen!")
            else:
                ztstart = datetime.strptime(strstart, '%Y-%m-%d')
                ztend = datetime.strptime(strtend, '%Y-%m-%d')
                larray = []
                if ztstart > ztend:
                    flash("Startdatum kommt vor Enddatum!")
                else:
                    for k in zt:
                        if k.ausgestempelt is not None:
                            if (ztstart <= k.eingestempelt and ztend >= k.eingestempelt) \
                                    or (ztstart <= k.ausgestempelt and ztend >= k.ausgestempelt):
                                larray.append(k)
                return render_template("meine_zeitstempel.html", ztstart=strstart, ztend=strtend, ca=ca, ma=ma,
                                       zt=larray, info=session)

    return render_template("meine_zeitstempel.html", ca=ca, ma=ma, zt=zt, info=session)