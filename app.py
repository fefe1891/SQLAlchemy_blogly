"""Blogly application."""

from flask import Flask, render_template, redirect, request
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User

app = Flask(__name__)

app.config['SECRET_KEY'] = "secret"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)
def init_db():
    with app.app_context():
        db.create_all() 
        
init_db()


@app.route('/')
def user_home_page():
    """Redirect to list of users."""
    return redirect('/users')

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
    
    return redirect('/users')

@app.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    """Delete user and redirect to list of users."""
    User.query.filter_by(id=user_id).delete()
    db.session.commit()
    
    return redirect('/users')

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

@app.route('/users/<int:user_id>')
def show_user(user_id):
    """Show about the given user."""
    user = User.query.get_or_404(user_id)
    return render_template('user_details.html', user=user)
