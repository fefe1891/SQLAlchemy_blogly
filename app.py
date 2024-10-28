"""Blogly application."""

from flask import Flask, render_template, redirect, request, flash, url_for
from flask_debugtoolbar import DebugToolbarExtension
from flask_migrate import Migrate
from models import db, connect_db, User, Post, Tag

app = Flask(__name__)

app.config['SECRET_KEY'] = "secret"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
migrate = Migrate(app, db)

connect_db(app)
def init_db():
    with app.app_context():
        db.create_all() 
        
init_db()


@app.route('/')
def user_home_page():
    """Homepage with 5 most recent posts."""
    posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
    return render_template('homepage.html', posts=posts)

@app.route('/users')
def list_users():
    """Show list of users."""
    users = User.query.order_by(User.last_name).order_by(User.first_name).all()

    return render_template('users.html', users=users)

@app.route('/users/<int:user_id>/edit', methods=['GET'])
def edit_user(user_id):
    """Show edit form for user."""
    user = User.query.get_or_404(user_id)
    
    return render_template('edit_user.html', user=user)

@app.route('/users/<int:user_id>/edit', methods=['POST'])
def update_user(user_id):
    """Handle edit form; update user and redirect to list of users."""
    user = User.query.get_or_404(user_id)
    user.first_name = request.form['first_name']
    user.last_name = request.form['last_name']
    user.image_url = request.form['image_url'] if request.form['image_url'] != '' else 'jonny-gios-xhqwAuPokt0-unsplash.jpg'
    
    db.session.commit()
    
    flash('User successfully updated!')
    return redirect('/users')


@app.route('/users/<int:user_id>', methods=['GET'])
def show_user(user_id):
    """Show detail page for user."""
    user = User.query.get_or_404(user_id)
    posts = Post.query.filter_by(user_id=user_id).all()
    tags = Tag.query.all()
    return render_template('user_details.html', user=user, posts=posts, tags=tags)

@app.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    """Delete user and redirect to list of users."""
    User.query.filter_by(id=user_id).delete()
    db.session.commit()
    
    return redirect('/users')



@app.route('/users/<int:user_id>/posts/new', methods=['GET', 'POST'])
def create_new_post(user_id):
    """Create a new post for a user."""
    # Handle Post request
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        
        # Fetch user id from form data
        user_id = request.form['user_id']
        
        # Validate if user exists
        user = User.query.get(user_id)
        if user is None:
            flash("User not found.")
            return redirect(url_for('list_users')) # Redirecting to the list users page if invalid user
        # Create new post
        post = Post(title=title, content=content, user_id=user_id)
        
        # Fetch tags for Post using tag ID's from form data
        tags = [Tag.query.get(tag_id) for tag_id in request.form.getlist('tags')]
        post.tags = tags
        
        # Add new post to the database
        db.session.add(post)
        db.session.commit()
        
        # Go to the user details page
        return redirect(url_for('show_user', user_id=user_id))
        
    # Handle GET request
    else:
        # Fetch user for 'GET" request
        user = User.query.get_or_404(user_id)
        tags = Tag.query.all()
        return render_template('posts_new_form.html', user=user, tags=tags)



@app.route('/posts/<int:post_id>', methods=['GET'])
def posts_show(post_id):
    """Show post."""
    
    post = Post.query.get_or_404(post_id)
    
    return render_template('post_detail.html', post=post)


@app.route('/posts/<int:post_id>/edit', methods=['GET', 'POST'])
def edit_post(post_id):
    """Show form to edit a post."""
    
    post = Post.query.get_or_404(post_id)
    tags = Tag.query.all() # Fetch all tags
    
    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        post.tags = [Tag.query.get(tag_id) for tag_id in request.form.getlist('tags')]
        db.session.commit()
        flash(f"Post edited successfully", 'success')
        return redirect(f'/posts/{post_id}')
    
    
    return render_template('edit_post.html', post=post, tags=tags)


@app.route('/posts/<int:post_id>/edit', methods=['POST'])
def update_post(post_id):
    """Handle editing of a post. Redirect to the post view."""
    
    post = Post.query.get_or_404(post_id)
    post.title = request.form['title']
    post.content = request.form['content']
    
    db.session.commit()
    
    flash("Post edited successfully")
    
    return redirect(f'/posts/{post_id}')


@app.route('/posts/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    """Delete the post."""
    
    Post.query.filter_by(id=post_id).delete()
    db.session.commit()
    
    flash("Post deleted successfully")
    
    return redirect('/')

@app.route('/users/new', methods=['GET'])
def users_new_form():
    """Show an add form for new users."""
    return render_template('users_new_form.html')

@app.route('/users/new', methods=['POST'])
def users_new():
    """Handle add form; add user and redirect to list of users."""
    image_url = request.form['image_url'] or 'jonny-gios-xhqwAuPokt0-unsplash.jpg'
    new_user = User(
        first_name=request.form['first_name'],
        last_name=request.form['last_name'],
        image_url = request.form['image_url'] if request.form['image_url'] != '' else 'jonny-gios-xhqwAuPokt0-unsplash.jpg'
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return redirect('/users')


@app.route('/tags', methods=['GET'])
def list_tags():
    """Show page about info with all tags."""
    tags = Tag.query.order_by(Tag.name).all()
    return render_template('list_tags.html', tags=tags)


@app.route('/tags/new', methods=['GET', 'POST'])
def new_tag():
    """Show form to add a new tag and handle form submission."""
    if request.method == 'POST':
        new_tag = Tag(name=request.form['name'])
        posts = [Post.query.get(post_id) for post_id in request.form.getlist('posts')]
        new_tag.posts = posts
        
        db.session.add(new_tag)
        db.session.commit()
        flash(f"Tag '{new_tag.name}' added.", 'success')
        return redirect('/tags')
    else:
        posts = Post.query.all()
        return render_template('new_tag.html', posts=posts)
    
    
@app.route('/tags/<int:tag_id>', methods=['GET'])
def show_tag(tag_id):
    """Show details about a tag."""
    tag = Tag.query.get_or_404(tag_id)
    return render_template('show_tag.html', tag=tag)


@app.route('/tags/<int:tag_id>/edit', methods=['GET', 'POST'])
def edit_tag(tag_id):
    """Show edit form for a tag and handle form submission."""
    tag = Tag.query.get_or_404(tag_id)
    if request.method == 'POST':
        tag.name = request.form['name']
        posts = [Post.query.get(post_id) for post_id in request.form.getlist('posts')]
        tag.posts = posts
        
        db.session.commit()
        flash(f"Tag '{tag.name}' updated.", 'success')
        return redirect('/tags')
    else:
        posts = Post.query.all()
        return render_template('edit_tag.html', tag=tag, posts=posts)


@app.route('/tags/<int:tag_id>/delete', methods=['POST'])
def delete_tag(tag_id):
    """Delete a tag."""
    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()
    flash(f"Tag '{tag.name}' deleted.", 'danger')
    return redirect('/tags')


@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return render_template('404.html'), 404
