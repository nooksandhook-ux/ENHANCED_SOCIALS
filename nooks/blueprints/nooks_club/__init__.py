from flask import Blueprint

nooks_club_bp = Blueprint('nooks_club', __name__, template_folder='../../templates/nooks_club')

from . import routes
