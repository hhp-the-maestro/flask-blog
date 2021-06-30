from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField

class PostForm(FlaskForm):
	title = StringField('Title')
	content = TextAreaField('Content')
	submit = SubmitField('Post')

	def validate_title(self, title):
		if title.data == '':
			raise ValidationError('the title field is empty')

	def validate_content(self, content):
		if content.data == '':
			raise ValidationError('your post must have some content')
	
