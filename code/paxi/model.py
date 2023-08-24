from paxi import db
import datetime

# a1277ca60f867fd6f16f19c30e69a8c9024ee2bf40efcf3a044d2b63c0f1640f: sha256: aspad/amiraspad

class User(db.Model):
    # TODO: admin table
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(50))
    username = db.Column(db.String(40), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return f"{self.id}) {self.fullname}"

class Sample(db.Model):
    # TODO: work sample table
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(90), nullable=False)
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
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text)
    album = db.Column(db.Text)
    keyword = db.Column(db.String(120), nullable=False)
    date = db.Column(db.DateTime, default=datetime.datetime.now)

    def __repr__(self):
        return f"{self.id}) {self.title[:30]} | {self.date}"