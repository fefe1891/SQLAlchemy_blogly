import os
import unittest
from datetime import datetime
from app import app
from models import db, User
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

    if __name__ == "__main__":
        unittest.main()
