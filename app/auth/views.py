# coding=utf-8
from flask import render_template, redirect, url_for, flash, request
from . import auth
from flask.ext.login import login_user, login_required, logout_user, current_user
from ..models import User
from .forms import LoginForm, RegistrationForm,\
	PasswordResetRequestForm, ChangePasswordForm, PasswordResetForm, ChangeEmailForm
from manage import db
from ..email import send_email


@auth.before_app_request
def before_request():
	if current_user.is_authenticated and not current_user.confirmed and\
		request.endpoint[:5] != 'auth.':
		return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
	if current_user.is_anonymous or current_user.confirmed:
		return redirect(url_for('main.index'))
	return render_template('auth/unconfirmed.html')


@auth.route('/confirm')
@login_required
def resend_confirmation():
	token = current_user.generate_confirmation_token()
	send_email(current_user.email,'确认您的账号', 'auth/email/confirm', user=current_user, token=token)
	flash('新的确认邮件已发送至您的邮箱,请确认.')
	return redirect(url_for('main.index'))


@auth.route('/login',methods=['GET','POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user is not None and user.verify_password(form.password.data):
			login_user(user,form.remember_me.data)
			return redirect(request.args.get('next') or url_for('main.index'))
		flash('无效的用户名或密码.')
	return render_template('auth/login.html',form=form)


@auth.route('/logout')
@login_required
def logout():
	logout_user()
	flash('您已退出.')
	return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(email=form.email.data,username=form.username.data
					,password=form.password.data)
		db.session.add(user)
		db.session.commit()
		token = user.generate_confirmation_token()
		send_email(user.email, '确认您的账号', 'auth/email/confirm', user=user, token=token)
		flash('确认邮件已经发送到您的邮箱,请确认.')
		return redirect(url_for('main.index'))
	return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
def confirm(token):
	if current_user.confirmed:
		return redirect(url_for('main.index'))
	if current_user.confirm(token):
		flash('您已完成账号确认,马上开始您的天马之旅吧!')
	else:
		flash('您的确认链接无效或已过期,请尝试重新获取确认链接.')
		return redirect(url_for('auth.unconfirmed'))
	return redirect(url_for('main.index'))


@auth.route('/change-password',methods=['GET','POST'])
@login_required
def change_password():
	form = ChangePasswordForm()
	if form.validate_on_submit():
		if current_user.verify_password(form.old_password.data):
			current_user.password = form.password.data
			db.session.add(current_user)
			flash('您的密码已修改.')
			return redirect(url_for('main.index'))
		else:
			flash('密码填写错误.')
	return render_template('auth/change_password.html', form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
	if not current_user.is_anonymous:
		return redirect(url_for('main.index'))
	form = PasswordResetRequestForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user:
			token = user.generate_reset_password_token()
			send_email(user.email, '重置密码', 'auth/email/reset_password', user=user, token=token, next=request.args.get('next'))
			flash('重置密码的邮件已发送至您的邮箱,请查收.')
		return redirect(url_for('auth.login'))
	return render_template('auth/reset_password.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
	if not current_user.is_anonymous:
		return redirect(url_for('main.index'))
	form = PasswordResetForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user is None:
			return redirect(url_for('main.index'))
		if user.reset_password(token, form.password.data):
			flash('您的密码已重置.')
			return redirect(url_for('auth.login'))
		else:
			return redirect(url_for('main.index'))
	return render_template('auth/reset_password.html', form=form)


@auth.route('/change-mail', methods=['GET', 'POST'])
@login_required
def change_email_request():
	form = ChangeEmailForm()
	if form.validate_on_submit():
		if current_user.verify_password(form.password.data):
			new_mail = form.email.data
			token = current_user.generate_email_change_token(new_mail)
			send_email(new_mail, '确认您的邮箱地址', 'auth/email/change_email', user=current_user, token=token)
			flash('确认您的新邮箱地址的邮件已发送至您的邮箱,请查收.')
			return redirect(url_for('main.index'))
		else:
			flash('邮箱或密码无效.')
	return render_template('auth/change_email.html', form=form)


@auth.route('/change-mail/<token>')
@login_required
def change_email(token):
	if current_user.change_email(token):
		flash('您的邮箱地址已更新.')
	else:
		flash('请求无效.')
	return redirect(url_for('main.index'))





































