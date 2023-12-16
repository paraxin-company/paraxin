from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, RadioField, FileField, MultipleFileField, EmailField, SelectField
from wtforms.validators import DataRequired, Length, ValidationError
from flask_login import current_user
from paxi.method import passwords
from paxi.model import Category
from paxi import app


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
    fullname = StringField('Full Name')
    username = StringField('User Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

    # def validate_username(self, username):
    #     if current_user.username != username.data:
    #         if current_user.fullname != username.data:
    #             if User.query.filter_by(username=username.data).first():
    #                 raise ValidationError(f'یوزر نیم {username.data} قبلا توسط شخص دیگری انتخاب شده است. نام جدید انتخاب کنید')
    #         else:
    #             raise ValidationError('توصیه ما به شما این است که UserName و FullName با هم متفاوت باشند (برای امنیت بیشتر توصیه میشود)')
        
    def validate_password(self, password):
        if passwords.check_pass(current_user.password, password.data) == False:
            raise ValidationError('پسورد وارد شده درست نمی باشد')
        

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