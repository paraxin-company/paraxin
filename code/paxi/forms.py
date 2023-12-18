from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, TextAreaField, EmailField, SelectField
from wtforms.validators import DataRequired, Length


class ContactForm(FlaskForm):
    email = EmailField('ایمیل شما', validators=[
        DataRequired()
    ])
    phone = StringField("شماره همراه", validators=[
        DataRequired(),
        Length(max=9)
    ])
    name = StringField("نام شما", validators=[
        DataRequired()
    ])
    title = StringField("عنوان پیام", validators=[
        DataRequired(),
        Length(max=50)
    ])
    department = SelectField("انتخاب دپارتمان", validators=[DataRequired()], choices=[
        "تیم پشتیبانی",
        "امور مالی",
        "ثبت درخواست مشاوره",
        "نقد و انتقاد",
        "دعوت به همکاری"
    ])
    relation = SelectField("طریقه‌ی آشنایی", validators=[DataRequired()], choices=[
        'از طریق تبلیغات',
        'از طریق آشنایان',
        'از طریق تلگرام',
        'موارد دیگر'
    ])
    text = TextAreaField("متن پیام", validators=[
        DataRequired()
    ])
    NotRobot = BooleanField('من ربات نیستم', validators=[DataRequired()])

