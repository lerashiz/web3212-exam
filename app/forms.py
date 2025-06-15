from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, DecimalField, TextAreaField, DateField, RadioField, FileField
from wtforms.validators import DataRequired, Length, Optional, NumberRange
from flask_wtf.file import FileAllowed

class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

class EquipmentForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    inventory_number = StringField('Инвентарный номер', validators=[DataRequired()])
    category = SelectField('Категория', coerce=int, validators=[DataRequired()])
    purchase_date = DateField('Дата покупки', validators=[DataRequired()])
    price = DecimalField('Стоимость', validators=[DataRequired(), NumberRange(min=0)])
    status = RadioField('Статус', choices=[('active', 'В эксплуатации'), ('repair', 'На ремонте'), ('disposed', 'Списано')], default='active', validators=[DataRequired()])
    note = TextAreaField('Примечание', validators=[Optional()])
    image = FileField('Фотография', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png'])])

class MaintenanceForm(FlaskForm):
    date = DateField('Дата', validators=[DataRequired()])
    service_type = SelectField('Тип обслуживания', choices=[
    ('Диагностика', 'Диагностика'),
    ('Чистка', 'Чистка'),
    ('Обновление ПО', 'Обновление ПО')], validators=[DataRequired()])
    comment = TextAreaField('Комментарий', validators=[Optional()])
    submit = SubmitField('Добавить')

class DisposalForm(FlaskForm):
    reason = TextAreaField('Причина списания', validators=[DataRequired()])
    attachment = FileField('Акт списания (PDF)', validators=[DataRequired(), FileAllowed(['pdf'], 'Только PDF')])
    submit = SubmitField('Списать')