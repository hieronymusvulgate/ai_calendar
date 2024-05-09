from flask import Blueprint, render_template
from blueprints.user_authentication.user_authentication import *

forum_bp = Blueprint('forum', __name__, template_folder='templates')

@forum_bp.route('/')
@login_required
@token_required_forum(min_pro_token=24)
def forum():
    return render_template('forum.html')