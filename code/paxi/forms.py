from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, FileField, MultipleFileField
from wtforms.validators import DataRequired, Length, ValidationError

class LoginForm(FlaskForm):
    username = StringField('User name', validators=[
        DataRequired(),
        Length(min=4, max=20, message="طول نام کاربری شما درست نمی باشد")        
    ])
    password = PasswordField('Password', validators=[
        DataRequired()
    ])
    remember = BooleanField('remember me')


class BaseForm(FlaskForm):
    title = StringField('title', validators=[
        DataRequired(),
        Length(min=10, max=98)
    ])
    content = TextAreaField('content', validators=[
        DataRequired(),
        Length(min=100)
    ])
    baner = FileField('baner', validators=[
        DataRequired()
    ])
    keyword = TextAreaField('keyword', validators=[
        DataRequired(),
        Length(min=10, max=110)
    ])

    def validate_keyword(self, keyword):
        if ',' in keyword.data:
            raise ValidationError('کاراکتر "," در قسمت کلمات کلیدی مورد قبول نیست')

class WeblogForm(BaseForm):
    pass

class SampleForm(BaseForm):
    album = MultipleFileField('Album')