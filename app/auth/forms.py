# coding=utf-8
from flask.ext.wtf import Form
from wtforms import StringField,SubmitField,PasswordField,BooleanField
from wtforms.validators import  DataRequired,EqualTo,Email,Length,Regexp
from wtforms import ValidationError
from ..models import User


class LoginForm(Form):
	email = StringField('邮箱',validators=[Email(message='邮箱格式不正确'),DataRequired(message='请填写登陆邮箱'),Length(1,64)])
	password = PasswordField('密码',validators=[DataRequired(message='请填写密码'),Length(6,20,message='密码需要6位到20位')])
	remember_me = BooleanField('记住我')
	submit = SubmitField('登陆')


class RegistrationForm(Form):
	email = StringField('邮箱',validators=[Email(message='邮箱格式不正确'),
		DataRequired(message='请填写登陆邮箱'),Length(1,64)])
	username = StringField('用户名',validators=[DataRequired(message='用户名不能为空'),
		Length(1,64),
		Regexp(ur"^([0-9A-Za-z]|[\u4e00-\u9fa5])+([0-9A-Za-z]|[\u4e00-\u9fa5])*$", 0, message='用户名不能是特殊字符，比如@￥%.')])
	password = PasswordField('密码',validators=[DataRequired(message='请填写密码'),Length(6,20,message='密码需要6位到20位'),EqualTo('password2',message='密码必须匹配')])
	password2 = PasswordField('确认密码',validators=[DataRequired(message='请填写密码')])
	submit = SubmitField('保存')

	@staticmethod
	def validate_email(self,field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError('该邮箱已经注册')

	@staticmethod
	def validate_username(self,field):
		if User.query.filter_by(username=field.data).first():
			raise ValidationError('该用户名已注册')


class ChangePasswordForm(Form):
	old_password = PasswordField('现用密码',validators=[DataRequired()])
	password = PasswordField('新密码',validators=[DataRequired(message='请填写密码'), Length(6, 20, message='密码需要6位到20位'), EqualTo('password2',\
												message='密码必须匹配')])
	password2 = PasswordField('确认密码', validators=[DataRequired()])
	submit = SubmitField('保存')


class PasswordResetRequestForm(Form):
	email = StringField('请填写注册邮箱', validators=[DataRequired(), Length(1, 64),Email()])
	submit = SubmitField('重置密码')


class PasswordResetForm(Form):
	email = StringField('邮箱', validators=[Email(message='邮箱格式不正确'),
		DataRequired(message='请填写登陆邮箱'),Length(1,64)])
	password = PasswordField('新密码', validators=[DataRequired(message='请填写密码'), Length(6, 20, message='密码需要6位到20位'), EqualTo('password2', message='密码必须匹配')])
	password2 = PasswordField('确认密码', validators=[DataRequired(message='请填写密码')])
	submit = SubmitField('保存')

	def validate_email(self, field):
		if User.query.filter_by(email=field.data).first() is None:
			return ValidationError('该邮箱不存在.')


class ChangeEmailForm(Form):
	email = StringField('新邮箱', validators=[Email(message='邮箱格式不正确'), DataRequired(message='请填写登陆邮箱'), Length(1,64)])
	password = PasswordField('密码', validators=[DataRequired(message='请填写密码')])
	submit = SubmitField('保存')

	def validate_email(self, field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError('该邮箱已注册,请更换邮箱')







