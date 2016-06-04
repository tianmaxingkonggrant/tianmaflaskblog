# coding=utf-8
from flask import (render_template, abort, redirect,url_for,
				   current_app, flash, request, make_response)
from . import main
from .forms import PostForm, EditProfileForm, EditProfileAdminForm, CommentForm, ImgForm, SearchForm
from .. import db
from ..models import User, Role, Permission, Post, Comment
from flask.ext.login import login_required, current_user
from ..decorator import admin_required,permission_required
from werkzeug.security import safe_join


@main.route('/',methods=['GET','POST'])
def index():
	form = PostForm()
	if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
		post = Post(title=form.title.data, body=form.body.data, author=current_user._get_current_object())
		db.session.add(post)
		return redirect(url_for('main.index'))
	show_followed = False
	if current_user.is_authenticated:
		show_followed = bool(request.cookies.get('show_followed', ''))
	if show_followed:
		query = current_user.followed_posts
	else:
		query = Post.query
	page = request.args.get('page', 1, type=int)
	pagination = query.order_by(Post.timestamp.desc()).paginate(
		page, per_page=current_app.config['FLASK_POSTS_PER_PAGE'], error_out=False
	)
	posts = pagination.items
	searchform = SearchForm()
	query = searchform.search.data
	if searchform.validate_on_submit():
		return redirect(url_for('main.search_results', query=query))
	return render_template('index.html', form=form,
			posts=posts, pagination=pagination,
			show_followed=show_followed, searchform=searchform)


@main.route('/user/<username>', methods=['GET', 'POST'])
def user(username):
	user = User.query.filter_by(username=username).first_or_404()
	page = request.args.get('page', 1, type=int)
	pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASK_POSTS_PER_PAGE'],
        error_out=False)
	posts = pagination.items
	form = ImgForm()
	from manage import app
	if form.validate_on_submit():
		current_user.img = form.picture.data.filename
		if current_user.img and user.allowed_img(current_user.img):
			imgdest = safe_join(app.config['UPLOAD_FOLDER'], current_user.img)
			form.picture.data.save(imgdest)
			db.session.add(current_user)
			return redirect(url_for('main.user', username=username))
	return render_template('user.html', form=form, user=user, posts=posts, pagination=pagination)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
	form = EditProfileForm()
	if form.validate_on_submit():
		current_user.name = form.name.data
		current_user.location = form.location.data
		current_user.about_me = form.about_me.data
		db.session.add(current_user)
		flash('您的资料已更新')
		return redirect(url_for('main.user', username=current_user.username))
	form.name.data = current_user.name
	form.location.data = current_user.location
	form.about_me.data = current_user.about_me
	return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
	user = User.query.get_or_404(id)
	form = EditProfileAdminForm(user=user)
	if form.validate_on_submit():
		user.email = form.email.data
		user.username = form.username.data
		user.location = form.location.data
		user.confirmed = form.confirmed.data
		user.role = Role.query.get(form.role.data)
		user.name = form.name.data
		user.about_me = form.about_me.data
		db.session.add(user)
		flash('用户资料已更新')
		return redirect(url_for('main.user',username=user.username))
	form.email.data = user.email
	form.username.data = user.username
	form.location.data = user.location
	form.confirmed.data = user.confirmed
	form.role.data = user.role_id
	form.name.data = user.name
	form.about_me.data = user.about_me
	return render_template('edit_profile.html', form=form, user=user)


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
	post = Post.query.get_or_404(id)
	form = CommentForm()
	if form.validate_on_submit():
		comment = Comment(body=form.body.data, post=post, author=
		current_user._get_current_object())
		db.session.add(comment)
		return redirect(url_for('main.post', id=post.id))
	page = request.args.get('page', 1, type=int)
	pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
		page, per_page=current_app.config['FLASK_PER_PAGE_COMMENT'])
	comments = pagination.items
	return render_template('post.html', posts=[post], form=form, comments=comments, pagination=pagination)

@main.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
	post = Post.query.get_or_404(id)
	if current_user != post.author and not current_user.can(Permission.ADMINISTER):
		abort(403)
	form = PostForm()
	if form.validate_on_submit():
		post.title = form.title.data
		post.body = form.body.data
		db.session.add(post)
		flash('您的博文已更新.')
		return redirect(url_for('main.post', id=post.id))
	form.title.data = post.title
	form.body.data = post.body
	return render_template('edit_post.html', form=form)


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash('用户不存在.')
		return redirect(url_for('main.index'))
	if current_user.is_following(user):
		flash('您已关注了%s.' % username)
		return redirect(url_for('main.user', username=username))
	current_user.follow(user)
	return redirect(url_for('main.user', username=username))


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash('用户不存在.')
		return redirect(url_for('main.index'))
	if not current_user.is_following(user):
		flash('您已不再关注%s.' % username)
		return redirect(url_for('main.user', username=username))
	current_user.unfollow(user)
	return redirect(url_for('main.user', username=username))


@main.route('/followers/<username>')
def followers(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash('用户不存在.')
		return redirect(url_for('main.user', username=username))
	page = request.args.get('page', 1, type=int)
	pagination = user.followers.paginate(
		page, per_page=current_app.config['FLASK_FOLLOWERS_PER_PAGE'], error_out=False
	)
	follows = [{'user': item.follower, 'timestamp':item.timestamp} for item\
			   in pagination.items]
	return render_template('followers.html', user=user, pagination=pagination,
						   follows=follows, title="Followers of",
                           endpoint='main.followers')


@main.route('/followed/<username>')
def followed(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash('用户不存在.')
		return redirect(url_for('main.user', username=username))
	page = request.args.get('page', 1, type=int)
	pagination = user.followed.paginate(
		page, per_page=current_app.config['FLASK_FOLLOWERS_PER_PAGE'], error_out=False
	)
	follows = [{'user': item.followed, 'timestamp': item.timestamp} for item\
			   in pagination.items]
	return render_template('followers.html', user=user, pagination=pagination,
						   follows=follows, title='Followed by', endpoint='main.followed')


@main.route('/all')
def show_all():
	resp = make_response(redirect(url_for('main.index')))
	resp.set_cookie('show_followed', '', max_age=30 * 24 * 60 * 60)
	return resp


@main.route('/followed')
def show_followed():
	resp = make_response(redirect(url_for('main.index')))
	resp.set_cookie('show_followed', '1', max_age=30 * 24 * 60 * 60)
	return resp


@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
	page = request.args.get('page', 1, type=int)
	pagination =  Comment.query.order_by(Comment.timestamp.desc()).paginate(
		page, per_page=current_app.config['FLASK_PER_PAGE_COMMENT'], error_out=\
		False
	)
	comments = pagination.items
	return render_template('moderate.html', comments=comments, pagination=pagination,
						   page=page)



@main.route('/moderate/enable/<int:id>')#这里的路由相当于通道,并不停留在这个页面,这是一种需要
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
	comment = Comment.query.get_or_404(id)
	comment.disabled = False
	db.session.add(comment)
	return redirect(url_for('main.moderate', page=request.args.get('page', 1, type=int)))

@main.route('/moderate/disable/<int:id>')#这里的路由相当于通道,并不停留在这里.
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disabled(id):
	comment = Comment.query.get_or_404(id)
	comment.disabled =True
	db.session.add(comment)
	return redirect(url_for('main.moderate',page=request.args.get('page', 1, type=int)))


@main.route('/search_results/<query>')
def search_results(query):
	# searcher = ix.searcher()
	# results = searcher.find('content',querystring=query)
	from manage import app
	results = Post.query.whoosh_search(query, limit=app.config['MAX_SEARCH_RESULTS'],\
		fields=['title', 'body'], ).all()
	flash('搜索出来了！')
	return render_template('search_results.html', query=query, posts=results)



