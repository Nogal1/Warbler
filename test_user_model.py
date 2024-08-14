"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows
from sqlalchemy.exc import IntegrityError

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test cases for User model."""

    def setUp(self):
        """Create test client, add sample data."""
        User.query.delete()
        Message.query.delete()
        Follows.query.delete()
        db.session.commit()

        self.client = app.test_client()

        # Sample data
        u1 = User.signup("user1", "user1@test.com", "password", None)
        u2 = User.signup("user2", "user2@test.com", "password", None)
        db.session.commit()

        self.u1 = User.query.get(u1.id)
        self.u2 = User.query.get(u2.id)

    def tearDown(self):
        """Clean up fouled transactions."""
        db.session.rollback()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_repr_method(self):
        """Does the repr method work as expected?"""
        self.assertEqual(repr(self.u1), f"<User #{self.u1.id}: {self.u1.username}, {self.u1.email}>")

    def test_is_following(self):
        """Does is_following successfully detect when user1 is following user2?"""
        self.u1.following.append(self.u2)
        db.session.commit()
        self.assertTrue(self.u1.is_following(self.u2))
        self.assertFalse(self.u2.is_following(self.u1))

    def test_is_not_following(self):
        """Does is_following successfully detect when user1 is not following user2?"""
        self.assertFalse(self.u1.is_following(self.u2))

    def test_is_followed_by(self):
        """Does is_followed_by successfully detect when user1 is followed by user2?"""
        self.u2.following.append(self.u1)
        db.session.commit()
        self.assertTrue(self.u1.is_followed_by(self.u2))
        self.assertFalse(self.u2.is_followed_by(self.u1))

    def test_is_not_followed_by(self):
        """Does is_followed_by successfully detect when user1 is not followed by user2?"""
        self.assertFalse(self.u1.is_followed_by(self.u2))

    def test_user_create(self):
        """Does User.create successfully create a new user given valid credentials?"""
        u = User.signup("user3", "user3@test.com", "password", None)
        db.session.commit()

        self.assertIsNotNone(User.query.get(u.id))
        self.assertEqual(u.username, "user3")
        self.assertEqual(u.email, "user3@test.com")

    def test_user_create_fail(self):
        """Does User.create fail to create a new user if validations fail?"""
        invalid_u = User.signup(None, "invalid@test.com", "password", None)
        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_user_authenticate(self):
        """Does User.authenticate successfully return a user when given valid credentials?"""
        u = User.authenticate("user1", "password")
        self.assertIsNotNone(u)
        self.assertEqual(u.id, self.u1.id)

    def test_user_authenticate_invalid_username(self):
        """Does User.authenticate fail to return a user when the username is invalid?"""
        self.assertFalse(User.authenticate("invalidusername", "password"))

    def test_user_authenticate_invalid_password(self):
        """Does User.authenticate fail to return a user when the password is invalid?"""
        self.assertFalse(User.authenticate("user1", "wrongpassword"))
