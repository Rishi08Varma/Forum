from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from .models import User, Post, Comment
from .forms import RegistrationForm, LoginForm, PostForm, CommentForm, ChangePasswordForm, ChangeDisplayNameForm, UpdateProfilePictureForm
from . import db, bcrypt
from werkzeug.utils import secure_filename
import os
import secrets
from flask import current_app as app
from PIL import Image

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/home')
def home():
    posts = Post.query.all()
    return render_template('home.html', posts=posts)

@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('main.login'))
    return render_template('signup.html', title='Register', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@main.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@main.route('/account')
@login_required
def account():
    return render_template('account.html', title='Account')

@main.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(subject=form.subject.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_post.html', title='New Post', form=form)

@main.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.subject, post=post)

@main.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.subject = form.subject.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('main.post', post_id=post.id))
    elif request.method == 'GET':
        form.subject.data = post.subject
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post', form=form)

@main.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('main.home'))

@main.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def comment_post(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(content=form.content.data, author=current_user, post=post)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been added!', 'success')
    return redirect(url_for('main.post', post_id=post.id))

@main.route('/post/<int:post_id>/comment/<int:comment_id>/reply', methods=['POST'])
@login_required
def reply_comment(post_id, comment_id):
    post = Post.query.get_or_404(post_id)
    parent_comment = Comment.query.get_or_404(comment_id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(content=form.content.data, author=current_user, post=post, parent=parent_comment)
        db.session.add(comment)
        db.session.commit()
        flash('Your reply has been added!', 'success')
    return redirect(url_for('main.post', post_id=post.id))

@main.route('/comment/<int:comment_id>/upvote', methods=['POST'])
@login_required
def upvote_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    comment.upvotes += 1
    db.session.commit()
    return redirect(request.referrer)

@main.route('/comment/<int:comment_id>/downvote', methods=['POST'])
@login_required
def downvote_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    comment.downvotes += 1
    db.session.commit()
    return redirect(request.referrer)

@main.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        abort(403)
    users = User.query.all()
    return render_template('admin.html', users=users)

@main.route('/admin/user/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if not current_user.is_admin:
        abort(403)
    user = User.query.get_or_404(user_id)
    form = RegistrationForm(obj=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        if form.password.data:
            user.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        db.session.commit()
        flash('User details have been updated!', 'success')
        return redirect(url_for('main.admin'))
    return render_template('edit_user.html', form=form, user=user)

@main.route('/post/<int:post_id>/upvote', methods=['POST'])
@login_required
def upvote_post(post_id):
    post = Post.query.get_or_404(post_id)
    post.upvotes += 1
    db.session.commit()
    return redirect(url_for('main.post', post_id=post.id))

@main.route('/post/<int:post_id>/downvote', methods=['POST'])
@login_required
def downvote_post(post_id):
    post = Post.query.get_or_404(post_id)
    post.downvotes += 1
    db.session.commit()
    return redirect(url_for('main.post', post_id=post.id))

@main.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        abort(403)
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User has been deleted!', 'success')
    return redirect(url_for('main.admin'))

@main.route('/admin/user/<int:user_id>/change_password', methods=['GET', 'POST'])
@login_required
def change_user_password(user_id):
    if not current_user.is_admin:
        abort(403)
    user = User.query.get_or_404(user_id)
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        db.session.commit()
        flash('User password has been updated!', 'success')
        return redirect(url_for('main.admin'))
    return render_template('change_user_password.html', form=form, user=user)

@main.route('/admin/user/<int:user_id>/change_display_name', methods=['GET', 'POST'])
@login_required
def change_user_display_name(user_id):
    if not current_user.is_admin:
        abort(403)
    user = User.query.get_or_404(user_id)
    form = ChangeDisplayNameForm()
    if form.validate_on_submit():
        user.display_name = form.display_name.data
        db.session.commit()
        flash('User display name has been updated!', 'success')
        return redirect(url_for('main.admin'))
    return render_template('change_user_display_name.html', form=form, user=user)

@main.route('/account/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        current_user.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        db.session.commit()
        flash('Your password has been updated!', 'success')
        return redirect(url_for('main.account'))
    return render_template('change_password.html', form=form)

@main.route('/account/change_display_name', methods=['GET', 'POST'])
@login_required
def change_display_name():
    form = ChangeDisplayNameForm()
    if form.validate_on_submit():
        current_user.display_name = form.display_name.data
        db.session.commit()
        flash('Your display name has been updated!', 'success')
        return redirect(url_for('main.account'))
    return render_template('change_display_name.html', form=form)

@main.route('/account/update_profile_picture', methods=['GET', 'POST'])
@login_required
def update_profile_picture():
    form = UpdateProfilePictureForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
            db.session.commit()
            flash('Your profile picture has been updated!', 'success')
            return redirect(url_for('main.account'))
    return render_template('update_profile_picture.html', form=form)

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    # Resize the image
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn
