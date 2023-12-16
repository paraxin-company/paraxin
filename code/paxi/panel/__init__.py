from flask import Blueprint

panel = Blueprint('panel', __name__, url_prefix='/paxi', template_folder='templates')

from paxi.panel import routes