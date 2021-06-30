from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import Length, Email, EqualTo, ValidationError
from flask_login import current_user
from flask_blog.models import User



class RegistrationForm(FlaskForm):
	username = StringField('Username',
	 validators=[Length(min=2, max=20)])
	email = StringField('Email', validators=[Email()])
	password = PasswordField('Password')
	confirm_password = PasswordField('Confirm Password',
	 validators=[EqualTo('password')])
	submit = SubmitField('Sign Up')

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()

		if user:
			raise ValidationError('username is already taken pls choose a different one')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()

		if user:
			raise ValidationError('email is already taken pls choose a different one')


class LoginForm(FlaskForm):
	email = StringField('Email', validators=[Email()])
	password = PasswordField('Password')
	remember = BooleanField('Remember me')
	submit = SubmitField('Log In')


class UpdateAccountForm(FlaskForm):
	username = StringField('Username',
	 validators=[Length(min=2, max=20)])
	email = StringField('Email', validators=[Email()])
	picture = FileField('update profile picture',
		validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
	submit = SubmitField('update')

	def validate_username(self, username):
		if username.data != current_user.username:
			user = User.query.filter_by(username=username.data).first()
			if user:
				raise ValidationError('username is already taken pls choose a different one')

	def validate_email(self, email):
		if email.data != current_user.email:
			user = User.query.filter_by(email=email.data).first()
			if user:
				raise ValidationError('email is already taken pls choose a different one')


class RequestResetForm(FlaskForm):
	email = StringField('Email', validators=[Email()])
	submit = SubmitField('Request Password Reset')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user is None:
			raise ValidationError('Unregistered email')

class ResetPasswordForm(FlaskForm):
	password = PasswordField('password')
	confirm_password = PasswordField('confirm_password')
	submit = SubmitField('Reset Password')
	