from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length

class VillageForm(FlaskForm):
    name = StringField('Village Name', validators=[DataRequired(), Length(max=100)])
    production = IntegerField('Production', validators=[DataRequired()])
    submit = SubmitField('Add Village')

class RouteForm(FlaskForm):
    from_village = SelectField('From Village', validators=[DataRequired(), Length(max=100)])
    to_village = SelectField('To Village', validators=[DataRequired(), Length(max=100)])
    amount = IntegerField('Amount', validators=[DataRequired()])
    submit = SubmitField('Add Route')

