from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, DateField, SelectField
from wtforms.fields.html5 import DateTimeField
from wtforms.validators import DataRequired, Required, InputRequired


class ZeitstempelForm(FlaskForm):
    eingestempelt = DateTimeField("Eingestempelt: ", validators=[DataRequired()], format='%Y-%m-%d %H:%M:%S')
    ausgestempelt = DateTimeField("Ausgestempelt: ", validators=[DataRequired()], format='%Y-%m-%d %H:%M:%S')
    submit = SubmitField("Speichern")
    id = StringField(validators=[DataRequired()])

    def fill(self, zeitstempel):
        self.eingestempelt.data = zeitstempel.eingestempelt
        self.ausgestempelt.data = zeitstempel.ausgestempelt
        self.id.data = zeitstempel.id
