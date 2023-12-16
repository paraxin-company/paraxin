from paxi import db
import datetime


class Category(db.Model):
    # TODO: work sample category table
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(50), nullable=False, unique=True)
    samples = db.relationship('Sample', backref='cat', lazy=True)

    def __repr__(self):
        return f"[{self.id}, {self.text}]"
    
    def count(self):
        return len(str(self.samples).split('|'))-1


class Sample(db.Model):
    # TODO: work sample table
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(90), nullable=False)
    content = db.Column(db.Text, nullable=False)
    baner = db.Column(db.Text, nullable=False)
    album = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.datetime.now)
    keyword = db.Column(db.String(120), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

    def __repr__(self):
        return f"|{self.id}"


class Weblog(db.Model):
    # TODO: weblog table
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    baner = db.Column(db.Text, nullable=False)
    keyword = db.Column(db.String(120), nullable=False)
    date = db.Column(db.DateTime, default=datetime.datetime.now)

    def __repr__(self):
        return f"{self.id}) {self.title[:30]} | {self.date}"


class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    full_name = db.Column(db.String(25), nullable=False)
    time = db.Column(db.DateTime, default=datetime.datetime.now)
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=False)

    def __repr__(self):
        return f"|{self.id}"


class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(40), nullable=False)
    title = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(11), nullable=False)
    name = db.Column(db.String(25), nullable=False)
    department = db.Column(db.String(25), nullable=False)
    relation = db.Column(db.String(25), nullable=False)
    text = db.Column(db.Text, nullable=False)
    time = db.Column(db.DateTime, default=datetime.datetime.now)
    answers = db.relationship('Answer', backref='tick', lazy=True)

    def __repr__(self):
        return f"|{self.id}"


class Verify(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tocken = db.Column(db.String(5), nullable=False)
    time = db.Column(db.DateTime, default=datetime.datetime.now)
    item = db.Column(db.String(40), nullable=False)

    def __repr__(self):
        return f"|{self.id}"
