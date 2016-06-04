# coding=utf-8
from flask import jsonify, request, current_app, url_for, g
from . import api
from ..models import Post, Comment,Permission
from .decorators import permission_required
from manage import db

@api.route('/post/<int:id>/comments')
def get_post_comments(id):
	post = Post.query.get_or_404(id)
	page = request.args.get('page', 1, type=int)
	pagination = post.comments.order_by(Post.timestamp.desc()).paginate(
		page, per_page=current_app.config['FLASK_PER_PAGE_COMMENTS'], error_out=False)
	comments = pagination.items
	prev =False
	if pagination.has_prev:
		prev = url_for('main.get_post_comments', page=page - 1, _external=False)
	next = False
	if pagination.has_next:
		next = url_for('main.get_post_comments', page=page + 1, _external=False)
	return jsonify({
		'post_comments': [comment.to_json() for comment in comments],
		'prev': prev,
		'next': next,
		'count': pagination.total})


@api.route('/comments')
def get_comments():
	page = request.args.get('page', 1, type=int)
	pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(page, per_page=current_app.config['FLASK_PER_PAGE_COMMENTS'], error_out=False)
	comments = pagination.items
	prev = False
	if pagination.has_prev:
		prev = url_for('get_comments', page=page - 1, _external=False)
	next = False
	if pagination.has_next:
		next = url_for('get_comments', page=page - 1, _external=False )
	return jsonify({
		'comments': [comment.to_json() for comment in comments],
		'prev': prev,
		'next': next,
		'count': pagination.total})


@api.route('/comments/<int:id>')
def get_comment(id):
	comment = Comment.query.get_or_404(id)
	return jsonify(comment.to_json())


@api.route('/posts/<int:id>/comments/', methods=['POST'])
@permission_required(Permission.COMMENT)
def new_post_comment(id):
	post = Post.query.get_or_404(id)
	comment = Comment.from_json(request.json)
	comment.author = g.current_user
	comment.post = post
	db.session.add(comment)
	db.session.commit()
	return jsonify(comment.to_json()), 201,\
		   {'location': url_for('api.get_comment', id=comment.id, _external=True)}





