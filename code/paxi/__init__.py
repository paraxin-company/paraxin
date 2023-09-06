from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:mahshiman@localhost:3306/paxi"
app.config["SECRET_KEY"] = "5d426f53f0667ec0a11e3504388812bc79956119c8534ba877380c54b0c293d2"
db = SQLAlchemy(app)
login_manager = LoginManager(app)

from paxi import routes