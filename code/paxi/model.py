from paxi import db, login_manager
from flask_login import UserMixin
import datetime

@login_manager.user_loader
def get_id(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    # TODO: admin table
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(50))
    username = db.Column(db.String(40), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    profile = db.Column(db.String(40), nullable=False)

    def __repr__(self):
        return f"{self.id}) {self.fullname}"

class Category(db.Model):
    # TODO: work sample category table
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(70), nullable=False, unique=True)
    samples = db.relationship('Sample', backref='cat', lazy=True)

    def __repr__(self):
        return f"{self.id}) {self.text}"

class Sample(db.Model):
    # TODO: work sample table
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(90), nullable=False)
    content = db.Column(db.Text)
    baner = db.Column(db.String(50), nullable=False)
    album = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.datetime.now)
    keyword = db.Column(db.String(120), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

    def __repr__(self):
        return f"{self.id}) {self.title[:30]} | {self.date}"

class Weblog(db.Model):
    # TODO: weblog table
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text)
    baner = db.Column(db.Text)
    keyword = db.Column(db.String(120), nullable=False)
    date = db.Column(db.DateTime, default=datetime.datetime.now)

    def __repr__(self):
        return f"{self.id}) {self.title[:30]} | {self.date}"