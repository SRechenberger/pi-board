from flask import redirect, url_for, render_template, flash, request
from flask_login import login_required, current_user, logout_user, login_user

from app import db
from app.models import User
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(handle=form.handle.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password!')
            return redirect(url_for('main.index'))

        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('main.index'))

    return render_template(
        'auth/login.html.j2',
        title='Login',
        form=form
    )

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            handle=form.handle.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Successfully registered')
        return redirect(url_for('auth.login'))

    return render_template(
        'auth/register.html.j2',
        title='Register',
        form=form
    )

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))
