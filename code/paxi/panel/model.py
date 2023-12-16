from paxi import login_manager, db
from flask_login import UserMixin

@login_manager.user_loader
def get_id(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    # TODO: admin table
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(40))
    username = db.Column(db.String(40), unique=True, nullable=False)
    phone = db.Column(db.String(11), nullable=False)
    # verify value use for email and phone varification, first number is for email and second is for phone
    verify = db.Column(db.String(2), nullable=False, default='00')
    email = db.Column(db.String(40), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    profile = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"{self.id}) {self.fullname}"