import os

from flask import render_template, redirect, request, flash, url_for, current_app
from flask_login import login_required, current_user

from app import db, images
from app.models import User
from app.main import bp
from app.main.forms import EditProfileForm

from werkzeug.utils import secure_filename

@bp.route('/')
@bp.route('/index')
def index():
    return render_template('main/index.html.j2', title='PiBoard')

@bp.route('/profile/<handle>')
@login_required
def profile(handle):
    user = User.query.filter_by(handle=handle).first_or_404()
    return render_template(
        'main/user_posts.html.j2',
        title=f'User {user.handle}',
        user=user,
        profile_pic=images.url(user.profile_pic) \
            if user.profile_pic else None
    )

@bp.route('/edit_profile/<handle>', methods=['GET', 'POST'])
@login_required
def edit_profile(handle):
    if current_user.handle != handle:
        flash('You cannot edit the profile of someone else!')
        return redirect(url_for('main.profile', handle=handle))

    user = User.query.filter_by(handle=handle).first_or_404()
    form = EditProfileForm()
    if form.validate_on_submit():
        new_profile_pic = form.profile_pic.data \
            if form.profile_pic.data else None
        if new_profile_pic:
            print(handle, secure_filename(new_profile_pic.filename))
            filename = images.save(
                new_profile_pic,
                handle,
                secure_filename(new_profile_pic.filename.lower())
            )

            old_profile_pic = user.profile_pic
            user.profile_pic = filename

            try:
                os.remove(images.path(old_profile_pic))
            except:
                pass

            db.session.commit()
            return redirect(url_for('main.profile', handle=handle))

        new_displayed_name = form.displayed_name.data \
            if form.displayed_name.data else None
        if new_displayed_name != user.displayed_name:
            user.displayed_name = new_displayed_name
            flash(f'Displayed name changed to {current_user.displayed_name}!')

        new_status_message = form.status_message.data \
            if form.status_message.data else None
        if new_status_message != user.status_message:
            user.status_message = new_status_message
            flash(f'Status message updated!')

        db.session.commit()
        return redirect(url_for('main.profile', handle=handle))

    elif request.method == 'GET':
        form.displayed_name.data = current_user.displayed_name
        form.status_message.data = current_user.status_message

    return render_template(
        'main/edit_profile.html.j2',
        title='Edit Profile',
        user=user,
        form=form,
        profile_pic=images.url(user.profile_pic) \
            if user.profile_pic else None
    )
