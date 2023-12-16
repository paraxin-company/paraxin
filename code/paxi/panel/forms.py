from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, FileField
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
        Length(min=10, max=98, message="تعداد حرفی که در قسمت عنوان قرار دادین بیشتر 98 حرف است ")
    ])
    content = TextAreaField('content', validators=[
        DataRequired(),
        Length(min=100, message="برای قسمت محتوا تعداد باید بیشتر از 100 تا حروف باشه")
    ])
    keyword = TextAreaField('keyword', validators=[
        DataRequired(),
        Length(min=10, max=115, message="برای قسمت کلمات کلیدی نمیشه بیشتر از 115 تا حرف وارد کرد")
    ])

    def validate_keyword(self, keyword):
        if ',' in keyword.data:
            raise ValidationError('کاراکتر "," در قسمت کلمات کلیدی مورد قبول نیست')


class WeblogFormEdit(BaseForm):
    baner = FileField('baner')


class WeblogForm(BaseForm):
    baner = FileField('baner', validators=[
        DataRequired()
    ])

