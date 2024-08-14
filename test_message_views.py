"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data
db.drop_all()
db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        self.other_user = User.signup(username="otheruser",
                                      email="other@test.com",
                                      password="password",
                                      image_url=None)

        db.session.commit()

    def tearDown(self):
        """Clean up fouled transactions."""
        db.session.rollback()

    def test_add_message(self):
        """Can a logged-in user add a message?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post("/messages/new", data={"text": "Hello"})
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_add_message_logged_in(self):
        """Can a logged-in user add a message?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post("/messages/new", data={"text": "New test message"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"New test message", resp.data)

    def test_delete_message_logged_in(self):
        """Can a logged-in user delete their own message?"""
        testuser = User.query.get(self.testuser.id)
        m = Message(text="Test Message", user_id=testuser.id)
        db.session.add(m)
        db.session.commit()

        # Re-query to ensure m is attached to the session
        m = Message.query.get(m.id)

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = testuser.id

            resp = c.post(f"/messages/{m.id}/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertNotIn(b"Test Message", resp.data)

    def test_add_message_logged_out(self):
        """Is a logged-out user prohibited from adding a message?"""
        with self.client as c:
            resp = c.post("/messages/new", data={"text": "New test message"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"Access unauthorized", resp.data)

    def test_delete_message_logged_out(self):
        """Is a logged-out user prohibited from deleting a message?"""
        testuser = User.query.get(self.testuser.id)
        m = Message(text="Test Message", user_id=testuser.id)
        db.session.add(m)
        db.session.commit()

        # Re-query to ensure m is attached to the session
        m = Message.query.get(m.id)

        with self.client as c:
            resp = c.post(f"/messages/{m.id}/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"Access unauthorized", resp.data)

    def test_add_message_as_another_user(self):
        """Is a logged-in user prohibited from adding a message as another user?"""
        other_user = User.query.get(self.other_user.id)
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post(f"/messages/new", data={"text": "New test message", "user_id": other_user.id}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            

    def test_delete_message_as_another_user(self):
        """Is a logged-in user prohibited from deleting a message as another user?"""
        other_user = User.query.get(self.other_user.id)
        m = Message(text="Test Message", user_id=other_user.id)
        db.session.add(m)
        db.session.commit()

        # Re-query to ensure m is attached to the session
        m = Message.query.get(m.id)

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post(f"/messages/{m.id}/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            