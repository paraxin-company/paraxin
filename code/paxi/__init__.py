from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:mahshiman@localhost:3306/paxi"
# app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://paraxini_etemad:EHAn,sybDhXT@5.144.130.53/paraxini_paxi"
app.config["SECRET_KEY"] = "5d426f53f0667ec0a11e3504388812bc79956119c8534ba877380c54b0c293d2"
db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = 'panel.paxi_login'
login_manager.login_message = 'ابتدا باید وارد شوید'
login_manager.login_message_category = 'danger'

folder_upload = r'paxi\static\media'
# folder_upload = r'paxi/static/media'

from paxi import routes