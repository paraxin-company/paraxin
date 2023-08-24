from paxi import db
import datetime

class User(db.Model):
    # TODO: admin table
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return f"{self.id}) {self.username}"


class Sample(db.Model):
    # TODO: work sample table
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text)
    album = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.datetime.now)
    keyword = db.Column(db.String(120), nullable=False)
    groups = db.relationship('Category', backref='group', lazy=True)

    def __repr__(self):
        return f"{self.id}) {self.title[:30]} | {self.date}"


class Category(db.Model):
    # TODO: work sample category table
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(70), nullable=False, unique=True)
    sample_id = db.Column(db.Integer, db.ForeignKey('sample.id'), nullable=False)

    def __repr__(self):
        return f"{self.id}) {self.text}"


class Weblog(db.Model):
    # TODO: weblog table
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text)
    album = db.Column(db.Text)
    keyword = db.Column(db.String(120), nullable=False)
    date = db.Column(db.DateTime, default=datetime.datetime.now)

    def __repr__(self):
        return f"{self.id}) {self.title[:30]} | {self.date}"