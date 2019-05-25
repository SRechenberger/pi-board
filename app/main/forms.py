from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed

from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import Length

from app import images

class EditProfileForm(FlaskForm):
    profile_pic = FileField(
        'Profile Pic',
        validators=[
            FileAllowed(images)
        ]
    )
    displayed_name = StringField(
        'Displayed Name',
        validators=[Length(0,128)]
    )
    status_message = TextAreaField(
        'Status Message',
        validators=[Length(0,128)]
    )
    submit = SubmitField('Save')


class PostForm(FlaskForm):
    body = TextAreaField(
        'Post Something',
        validators=[Length(1)]
    )
    submit = SubmitField('Post!')
