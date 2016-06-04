# coding=utf-8
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, TextAreaField, \
	BooleanField, SelectField, FileField
from wtforms.validators import DataRequired, Length, Email, Regexp
from ..models import Role, User
from wtforms import ValidationError
from flask.ext.pagedown.fields import PageDownField

class NameForm(Form):
	name = StringField('您的用户名:',validators=[DataRequired()])
	submit = SubmitField('保存')


class EditProfileForm(Form):
	name =StringField('姓名:', validators=[Length(0,64)])
	location = StringField('住址:', validators=[Length(0, 64)])
	about_me = TextAreaField('关于我:')
	submit = SubmitField('保存资料')


class EditProfileAdminForm(Form):
	email = StringField('邮箱', validators=[Email(message='邮箱格式不正确'),DataRequired(message='请填写邮箱'),Length(1,64)])
	username = StringField('用户名',validators=[DataRequired(message='用户名不能为空'),
		Length(1,64), Regexp('[a-zA-Z]*([\u4e00-\u9fa5]+)[0-9]*',0,message='用户名只能是中文,字母或数字')])
	confirmed = BooleanField('确认')
	role = SelectField('角色',coerce=int)
	name =StringField('姓名:', validators=[Length(0,64)])
	location = StringField('住址:', validators=[Length(0, 64)])
	about_me = TextAreaField('关于我:')
	submit = SubmitField('保存资料')

	def __init__(self, user, *args, **kwargs):
		super(EditProfileAdminForm, self).__init__(*args, **kwargs)
		self.role.choices = [(role.id, role.name) for role in Role.\
			query.order_by(Role.name).all()]
		self.user = user

	def validate_email(self, field):
		if field.data != self.user.email and User.query.filter_by(email=field.data)\
			.first():
			raise ValidationError('该邮箱已注册.')

	def validate_username(self, field):
		if field.data != self.user.username and User.query.filter_by(username=field.\
																  data).first():
			raise ValidationError('该用户名已注册.')


class PostForm(Form):
	title = StringField('标题', validators=[Length(0, 128)])
	body = PageDownField('内容', validators=[DataRequired(message='填写内容')])
	submit = SubmitField('发表')


class CommentForm(Form):
	body = StringField('评论君', validators=[DataRequired(message='请填写评论内容')])
	submit = SubmitField('评论')


class ImgForm(Form):
	picture = FileField('上传照片')
	submit = SubmitField('保存')


class SearchForm(Form):
	search = StringField('', validators=[DataRequired()])
	submit=SubmitField('搜索')