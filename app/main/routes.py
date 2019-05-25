import os
from datetime import datetime

from flask import render_template, redirect, request, flash, url_for, current_app, g
from flask_login import login_required, current_user
from flask_babel import get_locale

from app import db, images
from app.models import User, Post
from app.main import bp
from app.main.forms import EditProfileForm, PostForm

from werkzeug.utils import secure_filename

@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    g.locale = str(get_locale())

@bp.route('/')
@bp.route('/index')
def index():

    if current_user.is_authenticated:
        posts = Post.query.order_by(Post.timestamp.desc())
        return render_template(
            'main/index.html.j2',
            title=f'PiBoard ({current_user.displayed_name or current_user.handle})',
            posts=posts
        )
    return render_template(
        'main/index.html.j2',
        title='PiBoard'
    )

@bp.route('/post/<post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.filter_by(id=post_id).first_or_404()
    user = post.author

    if post.author.handle != current_user.handle:
        flash('You cannot edit other users posts.')
        return redirect(
            url_for(
                'main.post',
                handle=post.author.handle,
                post_id=post.id
            )
        )

    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        post.edited = datetime.utcnow()
        db.session.commit()
        flash('Your post has been edited.')
        return redirect(
            url_for(
                'main.post',
                handle=post.author.handle,
                post_id=post.id
            )
        )
    elif request.method == 'GET':
        form.body.data = post.body

    return render_template(
        'main/post.html.j2',
        title='Edit Post',
        comment_form=form,
        user=user,
        post=post
    )


@bp.route('/post/<handle>/<post_id>', methods=['GET', 'POST'])
@login_required
def post(handle, post_id):
    post = Post.query.filter_by(id=post_id).first_or_404()
    user = User.query.filter_by(handle=handle).first_or_404()

    comment_form = PostForm()
    if comment_form.validate_on_submit():
        comment = Post(
            body=comment_form.body.data,
            author=current_user,
            comment_to=post
        )
        db.session.add(comment)
        db.session.commit()
        return redirect(
            url_for(
                'main.post',
                handle=handle,
                post_id=post_id
            )
        )

    return render_template(
        'main/post.html.j2',
        user=user,
        post=post,
        title=f'Answer {user.displayed_name or user.handle}',
        comment_form=comment_form
    )


@bp.route('/profile/<handle>', methods=['GET', 'POST'])
@login_required
def profile(handle):
    user = User.query.filter_by(handle=handle).first_or_404()
    posts = user.posts.order_by(Post.timestamp.desc()).all()

    post_form = PostForm()

    if post_form.validate_on_submit():
        post = Post(
            body=post_form.body.data,
            author=current_user
        )
        db.session.add(post)
        db.session.commit()
        flash('Your post has been posted')
        return redirect(url_for('main.profile', handle=handle))

    return render_template(
        'main/user_posts.html.j2',
        title=f'User {user.handle}',
        user=user,
        posts=posts,
        post_form=post_form,
        owner=(current_user.handle == handle)
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
        form=form
    )
