# coding=utf-8
from flask.ext.wtf import Form
from wtforms import StringField,SubmitField
from wtforms.validators import DataRequired

class NameForm(Form):
	name = StringField('您的用户名:',validators=[DataRequired()])
	submit = SubmitField('保存')
