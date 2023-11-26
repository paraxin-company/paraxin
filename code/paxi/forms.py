from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, RadioField, FileField, MultipleFileField
from wtforms.validators import DataRequired, Length, ValidationError, EqualTo
from flask_login import current_user
from paxi.method import passwords
from paxi.model import User
from paxi.model import Category
from paxi import app

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


class SampleBase(BaseForm):
    app.app_context().push()
    
    all_category = Category.query.all()
    category_list = []
    
    album = MultipleFileField('album')
    for category in all_category:
        category_list.append(category.text)
    category = RadioField('category', choices=category_list, validators=[
        DataRequired()
    ])

class SampleForm(SampleBase):
    baner = FileField('baner', validators=[
        DataRequired()
    ])


class SampleFormEdit(SampleBase):
    baner = FileField('baner')


class CategoryForm(FlaskForm):
    text = StringField('text', validators=[
        DataRequired(),
        Length(min=8, max=45, message='اطلاعات وارده در بخش عنوان دسته بندی نباید کمتر از 8 و بیشتر از 45 حرف باشد')
    ])


class ProfileForm(FlaskForm):
    username = StringField('user name', validators=[DataRequired()])
    password = PasswordField('new password', validators=[
        DataRequired(),
        Length(min=8)
    ])
    confirm_password = PasswordField('confirm new password', validators=[
        DataRequired(),
        EqualTo('password', message='پسورد وارد شده در قسمت پسورد جدید باید با هم برابر باشن')
    ])
    old_password = PasswordField('old password', validators=[DataRequired()])

    def validate_username(self, username):
        if current_user.username != username.data:
            if current_user.fullname != username.data:
                if User.query.filter_by(username=username.data).first():
                    raise ValidationError(f'یوزر نیم {username.data} قبلا توسط کسی انتخاب شده است')
            else:
                raise ValidationError('نمی شه نام کاربری با اسم کامل یکی باشه (برای امنیت بیشتر توصیه میشه)')
    
    def validate_old_password(self, old_password):
        if passwords.check_pass(current_user.password, old_password.data) == False:
            raise ValidationError('پسورد وارد شده درست نمی باشد')