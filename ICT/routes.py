from flask import render_template, url_for, flash, redirect, request, abort, jsonify, current_app, Blueprint
from ICT import db, bcrypt
from ICT.forms import (RegistrationForm, LoginForm, UpdateAccountForm, PostForm, 
                      CommentForm, SearchForm, ChangePasswordForm, AdminUserEditForm)
from ICT.models import User, Post, Comment, Vote, Settings, CommentVote
from flask_login import login_user, current_user, logout_user, login_required
import secrets
import os
from PIL import Image
from datetime import datetime
from sqlalchemy import func, or_, desc

# Create Blueprint at the top
main = Blueprint('main', __name__)

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static', 'uploads', 'profile_pics', picture_fn)
    
    # Resize image
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    
    return picture_fn

@main.route("/")
@main.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    sort = request.args.get('sort', 'newest')
    
    if sort == 'top':
        # Modified query to include posts even if they have no votes
        posts = (Post.query
                .filter_by(draft=False)
                .outerjoin(Vote)  # Changed from join to outerjoin
                .group_by(Post.id)
                .order_by(func.coalesce(func.sum(Vote.value), 0).desc(),  # Handle NULL cases
                         Post.date_posted.desc()))  # Secondary sort by date
    else:
        posts = (Post.query
                .filter_by(draft=False)
                .order_by(Post.date_posted.desc()))
    
    posts = posts.paginate(page=page, per_page=5)
    return render_template('home.html', posts=posts, sort=sort)
    
@main.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in', 'success')
        return redirect(url_for('main.login'))  # Redirect to login instead of home
    return render_template('register.html', title='Register', form=form)

@main.route("/login", methods=['GET', 'POST'])
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
            flash('Login unsuccessful. Please check email and password.', 'danger')
    return render_template('login.html', title='Login', form=form)

@main.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@main.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.bio = form.bio.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('main.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.bio.data = current_user.bio
    image_file = url_for('static', filename='uploads/profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                         image_file=image_file, form=form)

@main.route("/admin/settings", methods=['POST'])
@login_required
def update_settings():
    if not current_user.is_admin:
        abort(403)
    
    # Get settings from form
    site_name = request.form.get('site_name', '')
    maintenance_mode = 'maintenance_mode' in request.form
    allow_registration = 'allow_registration' in request.form
    
    # Update settings in database
    settings = Settings.query.first()
    if not settings:
        settings = Settings()
        db.session.add(settings)
    
    settings.site_name = site_name
    settings.maintenance_mode = maintenance_mode
    settings.allow_registration = allow_registration
    
    db.session.commit()
    flash('Settings updated successfully!', 'success')
    return redirect(url_for('main.admin'))

@main.route("/change_password", methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if bcrypt.check_password_hash(current_user.password, form.current_password.data):
            hashed_password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
            current_user.password = hashed_password
            db.session.commit()
            flash('Your password has been updated!', 'success')
            return redirect(url_for('main.account'))
        else:
            flash('Current password is incorrect', 'danger')
    return render_template('change_password.html', title='Change Password', form=form)

@main.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data, 
            content=form.content.data, 
            author=current_user,
            draft=form.draft.data
        )
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_post.html', title='New Post', 
                         form=form, legend='New Post')

@main.route("/post/<int:post_id>", methods=['GET', 'POST'])
def post(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    if form.validate_on_submit():
        if current_user.is_authenticated:
            comment = Comment(content=form.content.data, 
                            post=post, 
                            author=current_user)
            db.session.add(comment)
            db.session.commit()
            flash('Comment added!', 'success')
            return redirect(url_for('main.post', post_id=post.id))
        else:
            flash('Please login to comment.', 'info')
            return redirect(url_for('main.login'))
    return render_template('post.html', title=post.title, 
                         post=post, form=form)

@main.route("/post/<int:post_id>/comment", methods=['POST'])
@login_required
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(
            content=form.content.data,
            post=post,
            author=current_user
        )
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been added!', 'success')
    return redirect(url_for('main.post', post_id=post.id))

@main.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user and not current_user.is_admin:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Post updated!', 'success')
        return redirect(url_for('main.post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post', 
                         form=form, legend='Update Post')

@main.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user and not current_user.is_admin:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted!', 'success')
    return redirect(url_for('main.home'))

@main.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)

@main.route("/post/<int:post_id>/vote", methods=['POST'])
@login_required
def vote_post(post_id):
    post = Post.query.get_or_404(post_id)
    vote_data = request.get_json()
    
    if not vote_data or 'vote_type' not in vote_data:
        return jsonify({'error': 'Invalid vote data'}), 400
    
    vote_value = 1 if vote_data['vote_type'] == 'up' else -1
    vote = Vote.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    
    if vote:
        if vote.value == vote_value:
            db.session.delete(vote)
            db.session.commit()
        else:
            vote.value = vote_value
            db.session.commit()
    else:
        vote = Vote(user=current_user, post=post, value=vote_value)
        db.session.add(vote)
        db.session.commit()
    
    return jsonify({
        'success': True,
        'new_count': post.get_vote_count()
    })

@main.route("/comment/<int:comment_id>/vote/<int:vote_type>", methods=['POST'])
@login_required
def vote_comment(comment_id, vote_type):
    comment = Comment.query.get_or_404(comment_id)
    
    if comment.author == current_user:
        return jsonify({'error': 'You cannot vote on your own comment'}), 400
        
    existing_vote = CommentVote.query.filter_by(
        user_id=current_user.id,
        comment_id=comment_id
    ).first()
    
    if existing_vote:
        if existing_vote.vote_type == bool(vote_type):
            db.session.delete(existing_vote)
            db.session.commit()
            return jsonify({
                'success': True,
                'action': 'removed',
                'vote_count': comment.get_vote_count()
            })
        else:
            existing_vote.vote_type = bool(vote_type)
            db.session.commit()
            return jsonify({
                'success': True,
                'action': 'changed',
                'vote_count': comment.get_vote_count()
            })
    else:
        vote = CommentVote(
            user_id=current_user.id,
            comment_id=comment_id,
            vote_type=bool(vote_type)
        )
        db.session.add(vote)
        db.session.commit()
        return jsonify({
            'success': True,
            'action': 'added',
            'vote_count': comment.get_vote_count()
        })

@main.route("/comment/<int:comment_id>/delete", methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.author != current_user and not current_user.is_admin:
        abort(403)
    post_id = comment.post_id
    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted!', 'success')
    return redirect(url_for('main.post', post_id=post_id))

@main.route("/admin")
@login_required
def admin():
    if not current_user.is_admin:
        abort(403)
    
    site_settings = Settings.get_settings()
    total_users = User.query.count()
    total_posts = Post.query.count()
    total_comments = Comment.query.count()
    
    # Get all users for the user management table
    users = User.query.order_by(User.date_joined.desc()).all()
    
    # Get recent activity
    recent_users = User.query.order_by(User.date_joined.desc()).limit(5).all()
    recent_posts = Post.query.order_by(Post.date_posted.desc()).limit(5).all()
    recent_comments = Comment.query.order_by(Comment.date_posted.desc()).limit(5).all()
    
    return render_template('admin.html', 
                         title='Admin Panel',
                         site_settings=site_settings,
                         total_users=total_users,
                         total_posts=total_posts,
                         total_comments=total_comments,
                         users=users,  # Add this line
                         recent_users=recent_users,
                         recent_posts=recent_posts,
                         recent_comments=recent_comments)

@main.route("/admin/user/<int:user_id>/edit", methods=['GET', 'POST'])
@login_required
def admin_edit_user(user_id):
    if not current_user.is_admin:
        abort(403)
    user = User.query.get_or_404(user_id)
    form = AdminUserEditForm()
    
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.bio = form.bio.data
        db.session.commit()
        flash(f'User {user.username} has been updated!', 'success')
        return redirect(url_for('main.admin'))
        
    elif request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
        form.bio.data = user.bio
    
    return render_template('admin_edit_user.html', title='Edit User',
                         form=form, user=user)

@main.route("/admin/user/<int:user_id>/delete", methods=['POST'])
@login_required
def admin_delete_user(user_id):
    if not current_user.is_admin:
        abort(403)
    
    user = User.query.get_or_404(user_id)
    
    # Prevent deleting own account
    if user.id == current_user.id:
        flash('You cannot delete your own account through the admin panel!', 'danger')
        return redirect(url_for('main.admin'))
    
    # Prevent deleting last admin
    if user.is_admin and User.query.filter_by(is_admin=True).count() <= 1:
        flash('Cannot delete the only admin account!', 'danger')
        return redirect(url_for('main.admin'))
    
    try:
        # Delete user's comments and their votes
        user_comments = Comment.query.filter_by(user_id=user.id).all()
        for comment in user_comments:
            CommentVote.query.filter_by(comment_id=comment.id).delete()
        Comment.query.filter_by(user_id=user.id).delete()

        # Delete user's posts and their associated votes/comments
        user_posts = Post.query.filter_by(user_id=user.id).all()
        for post in user_posts:
            Comment.query.filter_by(post_id=post.id).delete()
            Vote.query.filter_by(post_id=post.id).delete()
        Post.query.filter_by(user_id=user.id).delete()

        # Delete user's votes
        Vote.query.filter_by(user_id=user.id).delete()
        CommentVote.query.filter_by(user_id=user.id).delete()

        # Delete profile picture if not default
        if user.image_file != 'default.jpg':
            try:
                picture_path = os.path.join(current_app.root_path, 'static/uploads/profile_pics', user.image_file)
                if os.path.exists(picture_path):
                    os.remove(picture_path)
            except Exception as e:
                current_app.logger.error(f"Error deleting profile picture: {e}")

        username = user.username
        db.session.delete(user)
        db.session.commit()

        flash(f'User "{username}" has been deleted successfully.', 'success')
        return redirect(url_for('main.admin'))

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting user: {e}")
        flash('An error occurred while deleting the user. Please try again.', 'danger')
        return redirect(url_for('main.admin'))

@main.route("/search")
def search():
    query = request.args.get('q', '')
    search_type = request.args.get('type', 'all')
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Number of results per page
    
    if not query:
        return render_template('search.html', 
                             query='',
                             results=[],
                             search_type=search_type,
                             page=page,
                             pages=0)

    # Initialize results list
    results = []
    
    if search_type in ['all', 'posts']:
        posts = Post.query.filter(
            or_(
                Post.title.ilike(f'%{query}%'),
                Post.content.ilike(f'%{query}%')
            )
        ).all()
        for post in posts:
            post.type = 'post'
            results.append(post)

    if search_type in ['all', 'comments']:
        comments = Comment.query.filter(
            Comment.content.ilike(f'%{query}%')
        ).all()
        for comment in comments:
            comment.type = 'comment'
            results.append(comment)

    if search_type in ['all', 'users']:
        users = User.query.filter(
            or_(
                User.username.ilike(f'%{query}%'),
                User.bio.ilike(f'%{query}%')
            )
        ).all()
        for user in users:
            user.type = 'user'
            results.append(user)

    # Pagination
    total_results = len(results)
    pages = (total_results + per_page - 1) // per_page  # Calculate total pages
    start = (page - 1) * per_page
    end = start + per_page
    paginated_results = results[start:end]

    return render_template('search.html',
                         query=query,
                         results=paginated_results,
                         search_type=search_type,
                         page=page,
                         pages=pages)

@main.route("/account/delete", methods=['POST'])
@login_required
def delete_account():
    # Check if user is last admin
    if current_user.is_admin and User.query.filter_by(is_admin=True).count() <= 1:
        flash('Cannot delete the only admin account!', 'danger')
        return redirect(url_for('main.account'))

    try:
        # Delete user's comments and their votes
        user_comments = Comment.query.filter_by(user_id=current_user.id).all()
        for comment in user_comments:
            CommentVote.query.filter_by(comment_id=comment.id).delete()
        Comment.query.filter_by(user_id=current_user.id).delete()

        # Delete user's posts and their associated votes/comments
        user_posts = Post.query.filter_by(user_id=current_user.id).all()
        for post in user_posts:
            Comment.query.filter_by(post_id=post.id).delete()
            Vote.query.filter_by(post_id=post.id).delete()
        Post.query.filter_by(user_id=current_user.id).delete()

        # Delete user's votes
        Vote.query.filter_by(user_id=current_user.id).delete()
        CommentVote.query.filter_by(user_id=current_user.id).delete()

        # Delete profile picture if not default
        if current_user.image_file != 'default.jpg':
            try:
                picture_path = os.path.join(current_app.root_path, 'static/uploads/profile_pics', current_user.image_file)
                if os.path.exists(picture_path):
                    os.remove(picture_path)
            except Exception as e:
                current_app.logger.error(f"Error deleting profile picture: {e}")

        # Store username for flash message
        username = current_user.username

        # Delete user and logout
        user_to_delete = current_user._get_current_object()
        logout_user()
        db.session.delete(user_to_delete)
        db.session.commit()

        flash(f'Account "{username}" has been permanently deleted.', 'success')
        return redirect(url_for('main.home'))

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting account: {e}")
        flash('An error occurred while deleting your account. Please try again.', 'danger')
        return redirect(url_for('main.account'))

# Error handlers
@main.errorhandler(404)
def error_404(error):
    return render_template('errors/404.html'), 404

@main.errorhandler(403)
def error_403(error):
    return render_template('errors/403.html'), 403

@main.errorhandler(500)
def error_500(error):
    return render_template('errors/500.html'), 500