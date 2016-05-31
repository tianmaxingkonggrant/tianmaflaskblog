# coding=utf-8

from flask.ext.wtf import Form
from wtforms import StringField,SubmitField,PasswordField,BooleanField
from wtforms.validators import  DataRequired,EqualTo,Email,Length

class LoginForm(Form):
	email = StringField('邮箱',validators=[Email(message='邮箱格式不正确'),DataRequired(message='请填写登陆邮箱'),Length(1,64)])
	password = PasswordField('密码',validators=[DataRequired(message='请填写密码'),Length(6,20,message='密码需要6位到20位')])
	remember_me = BooleanField('记住我')
	submit = SubmitField('登陆')
