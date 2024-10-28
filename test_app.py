import os
import unittest
from bs4 import BeautifulSoup
from datetime import datetime
from app import app
from models import db, User, Post, Tag
import logging

logging.basicConfig(level=logging.DEBUG)


class UserTestCase(unittest.TestCase):
    """Tests for user routes."""

    def setUp(self):
        """Setup test client before each test."""
        logging.debug('Starting setUp')
        """Setup test client before each test."""
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///blogly_test"

        self.client = app.test_client()

        with app.app_context():
            db.create_all()
            logging.debug('Finished setUp')

    def tearDown(self):
        
        logging.debug('Starting tearDown')
        """Cleanup db and remove session after each test."""
        with app.app_context():
            db.session.remove()
            db.drop_all()
            logging.debug('Finished tearDown')

    def test_list_users(self):
        """Test list of users route."""
        logging.debug("Starting test_show_user")
        # Add test user
        user = User(first_name="Testy", last_name="McTestface", image_url="some_url")
        with app.app_context():
            db.session.add(user)
            db.session.commit()

        resp = self.client.get("/users")
        html = resp.get_data(as_text=True)

        # Check that the response status code is 200
        self.assertEqual(resp.status_code, 200)

        # Check that the name appears in the html of the page
        self.assertIn("Testy McTestface", html)

    def test_show_user(self):
        """Tests details about one user."""
        logging.debug("Starting test_show_user")

        user = User(first_name="Testy", last_name="McTestface", image_url="some_url")
        
        with app.app_context():
            db.session.add(user)
            db.session.commit()
            user = User.query.get(user.id) # refetch the user instance

        resp = self.client.get(f"/users/{user.id}")
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn("<p>Full name: Testy McTestface</p>", html)
        self.assertIn("<p>Created at: ", html)
        self.assertRegex(html, r"[A-Z][a-z]+ \d{2}, \d{4}, \d{2}:\d{2} (AM|PM)</p>")

    def test_users_new(self):
        """Test adding a new user."""
        logging.debug("Starting test_show_user")

        with self.client:
            # Check new user does not exist yet
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            first_name = f"New{timestamp}"
            last_name = f"User{timestamp}"
            
            new_user_name = f"{first_name} {last_name}"
            resp = self.client.get("/users")
            html = resp.get_data(as_text=True)
            self.assertNotIn(new_user_name, html)

            # Mock data for a new user
            data = {
                "first_name": "New",
                "last_name": "User",
                "image_url": "",  # assuming no image url for this user
            }

            # Use test client to send POST request
            resp = self.client.post("/users/new", data=data, follow_redirects=True)

            html = resp.get_data(as_text=True)

            # Check if request was successful
            self.assertEqual(resp.status_code, 200)

            # Check if new name appears in the user's list
            self.assertIn("New User", html)

    def test_edit_user(self):
        """Test editing an exisiting user."""
        logging.debug("Starting test_show_user")

        # Create a new user first
        new_user = User(
            first_name="Testy", last_name="McTestface", image_url="some_url"
        )
        with app.app_context():
            db.session.add(new_user)
            db.session.commit()
            new_user = User.query.get(new_user.id)

        # Check the 'GET' request: render the form
        resp = self.client.get(f"/users/{new_user.id}/edit")
        html = resp.get_data(as_text=True)

        # Check if the form loads correctly
        self.assertEqual(resp.status_code, 200)
        self.assertIn('<form action="/users/', html)

        # Mock data for the edit user
        edit_user_data = {
            "first_name": "EditedName",
            "last_name": "EditedSurname",
            "image_url": "",
        }

        # Check the 'POST' request: edit user with mock data
        resp = self.client.post(
            f"/users/{new_user.id}/edit", data=edit_user_data, follow_redirects=True
        )
        html = resp.get_data(as_text=True)

        # Check if editing was successful and redirects correctly
        self.assertEqual(resp.status_code, 200)

        # Check if the user's data was edited correctly
        self.assertIn("EditedName EditedSurname", html)
        
        
    def test_post_creation(self):
        """Test creation of a new post."""
        logging.debug("Starting test_post_creation")
        
        # Create a new user first
        new_user = User(
            first_name="Testy", last_name="McTestface", image_url="some_url"
        )
        
        with app.app_context():
            db.session.add(new_user)
            db.session.commit()
            new_user2 = User.query.get(new_user.id)
            
        # Mock data for the new post
        post_data = {
            "title": "Test Post",
            "content": "Test Content",
            "user_id": new_user2.id
        }
        
        # Use test client to send post request
        resp = self.client.post(f"/users/{new_user2.id}/posts/new", data=post_data, follow_redirects=True)
        
        resp = self.client.get(f"/users/{new_user2.id}")
        html = resp.get_data(as_text=True)
        
        # Check if request was successful
        self.assertEqual(resp.status_code, 200)
        
        # Check if new title and content are in HTML
        self.assertIn("Test Post", html)
        
        
    def test_edit_post(self):
        """Test editing an exisiting post."""
        logging.debug("Starting test_edit_post")
        
        # Create a new user first
        new_user = User(first_name="Testy", last_name="McTestface", image_url="some_url")
        
        with app.app_context():
            db.session.add(new_user)
            db.session.commit()
            new_user = User.query.get(new_user.id)
            
            # Create a post for the user
            new_post = Post(title="Test title", content="Test content", user_id=new_user.id)
            
            with app.app_context():
                db.session.add(new_post)
                db.session.commit()
                new_post = Post.query.get(new_post.id)
                
                # Mock data for the edited post
                edit_post_data = {
                    "title": "Edited title",
                    "content": "Edited content",
                }
                
                # Use test client to send POST request
                resp = self.client.post(f"/posts/{new_post.id}/edit", data=edit_post_data, follow_redirects=True)
                html = resp.get_data(as_text=True)
                
                # Check if request was successful
                self.assertEqual(resp.status_code, 200)
                
                # Check if the post's data was edited correctly
                self.assertIn("Edited title", html)
                self.assertIn("Edited content", html)
                
                
    def test_flash_messages(self):
        """Tests if flash messages are shown after editing a post."""
        
        # Open app context for the whole function
        with app.app_context():
            # Create a new user and a new post
            user = User(first_name="Test", last_name="User", image_url="")
            post = Post(title="Test Post", content="Test Content", user=user)
            
            db.session.add(user)
            db.session.add(post)
            db.session.commit()
            
            # Query the post instance 
            post = Post.query.get(post.id)
            
            # Mock data for edited post
            edit_post_data = {"title": "Edited", "content": "Content"}
            
            # Use test client to sent post request
            with self.client as c:
                resp = c.post(f"/posts/{post.id}/edit", data=edit_post_data, follow_redirects=True)
                
                html = resp.get_data(as_text=True)
                
                # Check if request was successful
                self.assertEqual(resp.status_code, 200)
                
                # Check if flash messages were shown
                self.assertIn("Edited", html)
                
                
class TagTestCase(unittest.TestCase):
    def setUp(self):
        """Setup test client before each test."""
        app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///blogly_test"
        self.client = app.test_client()
        
        with app.app_context():
            db.create_all()
            
            
    def test_tag_creation(self):
        """Test creation of a new tag."""
        # Define a name with a current timestamp
        tag_name = "python" + datetime.now().strftime("%Y%m%d%H%M%S")
        # Define a new tag to the database
        with app.app_context():
            new_tag = Tag(name=tag_name)
            # Code for attaching posts to tag should be here
            db.session.add(new_tag)
            db.session.commit()
            
            tag = Tag.query.get(new_tag.id) # Refetech the tag instance
            
        resp = self.client.get("/tags")
        html = resp.get_data(as_text=True)
        
        # Check that response code is 200
        self.assertEqual(resp.status_code, 200)
        
        # Check that the tag appears in the html of the page
        self.assertIn("python", html)
        
        
    def test_show_tag(self):
        """Test if the show page for a tag is displayed correctly."""
        with app.app_context():
            new_tag = Tag(name="python")
            db.session.add(new_tag)
            db.session.commit()
            
            tag = Tag.query.get(new_tag.id)
            
        resp = self.client.get(f"/tags/{tag.id}")
        html = resp.get_data(as_text=True)
        
        # Check that the response status code is 200
        self.assertEqual(resp.status_code, 200)
        
        # Check that the tag name appears in the html of the page
        self.assertIn("python", html)
        
        
    def test_delete_tag(self):
        """Test if deleting a tag works correctly and redirects to tags list."""
        # Create a new tag to be deleted
        unique_tag_name = "my_test_tag"
        with app.app_context():
            new_tag = Tag(name=unique_tag_name)
            db.session.add(new_tag)
            db.session.commit()
            
            tag = Tag.query.get(new_tag.id)
            
        # Delete the tab and verify deletion
        with self.client as c:
            c.post(f"/tags/{tag.id}/delete", follow_redirects=True)
            
            resp = c.get("/tags")
            html = resp.get_data(as_text=True)
            
            # Check that the response status code is 200
            self.assertEqual(resp.status_code, 200)
            
            # Parse HTML
            soup = BeautifulSoup(html, 'html.parser')
            
            # Suppose the tag names are under a div with the class 'tag-names'
            tag_div = soup.find_all('div', {'class' : 'tag-names'})
            tag_names = [tag.text for tag in tag_div]
            
            # Check that the deleted tag does not appear in the html of the page
            self.assertNotIn(unique_tag_name, html)
            
            
    def tearDown(self):
        """Cleanup the database after each test."""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    if __name__ == "__main__":
        unittest.main()