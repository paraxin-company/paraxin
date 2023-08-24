from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:mahshiman@localhost:3306/paxi"
db = SQLAlchemy(app)

from paxi import routes