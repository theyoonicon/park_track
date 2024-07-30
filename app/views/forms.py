from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo, ValidationError
from ..models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', 
                           validators=[DataRequired(), 
                                       Length(min=4, max=20), 
                                       Regexp('^[A-Za-z0-9]*$', 0, 
                                              'Usernames must have only letters and numbers')])
    email = StringField('Email', 
                        validators=[DataRequired(), 
                                    Email(message='Invalid email address')])
    password = PasswordField('Password', 
                             validators=[DataRequired(), 
                                         Length(min=8), 
                                         Regexp('(?=.*[a-z])', 0, 
                                                'Password must contain at least one lowercase letter'),
                                         Regexp('(?=.*[A-Z])', 0, 
                                                'Password must contain at least one uppercase letter'),
                                         Regexp('(?=.*[0-9])', 0, 
                                                'Password must contain at least one number'),
                                         Regexp('(?=.*[!@#$%^&*()_+=-])', 0, 
                                                'Password must contain at least one special character')])
    confirm_password = PasswordField('Confirm Password', 
                                     validators=[DataRequired(), 
                                                 EqualTo('password', 
                                                         message='Passwords must match')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is already in use.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already registered.')
