from flask import render_template
from flask_login import login_required, current_user

from app.models import User
from app.main import bp

@bp.route('/')
@bp.route('/index')
def index():
    return render_template('main/index.html.j2', title='PiBoard')

@bp.route('/profile/<handle>')
@login_required
def profile(handle):
    user = User.query.filter_by(handle=handle).first_or_404()
    return render_template(
        'main/profile.html.j2',
        user=user
    )
