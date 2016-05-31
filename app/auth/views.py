# coding=utf-8
from flask import render_template,redirect,url_for,flash,request
from . import auth
from flask.ext.login import login_user,login_required,logout_user
from ..models import User
from .forms import LoginForm


@auth.route('/login',methods=['GET','POST'])
def login():
	loginform = LoginForm()
	if loginform.validate_on_submit():
		user = User.query.filter_by(email=loginform.email.data).first()
		if user is not None and user.verify_password(loginform.password.data):
			login_user(user,loginform.remember_me.data)
			return redirect(request.args.get('next') or url_for('main.index'))
		flash('无效的用户名或密码.')
	return render_template('auth/login.html',loginform=loginform)


@auth.route('/logout')
@login_required
def logout():
	logout_user()
	flash('您已退出.')
	return redirect(url_for('index'))




