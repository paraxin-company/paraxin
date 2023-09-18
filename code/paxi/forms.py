from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, RadioField, FileField, MultipleFileField
from wtforms.validators import DataRequired, Length, ValidationError
from paxi.model import Category

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
    baner = FileField('baner', validators=[
        DataRequired()
    ])
    keyword = TextAreaField('keyword', validators=[
        DataRequired(),
        Length(min=10, max=115, message="برای قسمت کلمات کلیدی نمیشه بیشتر از 115 تا حرف وارد کرد")
    ])

    def validate_keyword(self, keyword):
        if ',' in keyword.data:
            raise ValidationError('کاراکتر "," در قسمت کلمات کلیدی مورد قبول نیست')


class WeblogForm(BaseForm):
    pass


class SampleForm(BaseForm):
    all_category = Category.query.all()
    category_list = []
    
    album = MultipleFileField('album')
    for category in all_category:
        category_list.append(category.text)
    category = RadioField('category', choices=category_list, validators=[
        DataRequired()
    ])


class CategoryForm(FlaskForm):
    text = StringField('text', validators=[
        DataRequired(),
        Length(min=8, max=45, message='اطلاعات وارده در بخش عنوان دسته بندی نباید کمتر از 8 و بیشتر از 45 حرف باشد')
    ])