import os
from unittest import TestCase
from models import db, Message, User, Likes

# Set the environmental variable to use a different database for tests
os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app

# Create our tables once for all tests
db.drop_all()
db.create_all()

class MessageModelTestCase(TestCase):
    """Test model for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        
        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.u1 = User.signup(username="user1", email="user1@test.com", password="password", image_url=None)
        self.u2 = User.signup(username="user2", email="user2@test.com", password="password", image_url=None)
        db.session.commit()

        self.m1 = Message(text="Test message 1", user_id=self.u1.id)
        self.m2 = Message(text="Test message 2", user_id=self.u2.id)
        db.session.add_all([self.m1, self.m2])
        db.session.commit()


    def tearDown(self):
        """Clean up fouled transactions."""
        db.session.rollback()


    def test_message_model(self):
        """Does basic model work?"""

        m = Message(
            text="Test message",
            user_id=self.u1.id
        )

        db.session.add(m)
        db.session.commit()

        # User should have one message
        self.assertEqual(len(self.u1.messages), 2)
        self.assertEqual(self.u1.messages[1].text, "Test message")


    def test_user_like_message(self):
        """Can a user like a message?"""
        like = Likes(user_id=self.u1.id, message_id=self.m2.id)
        db.session.add(like)
        db.session.commit()

        self.assertIn(self.m2, self.u1.likes)


    def test_user_unlike_message(self):
        """Can a user unlike a message?"""
        like = Likes(user_id=self.u1.id, message_id=self.m2.id)
        db.session.add(like)
        db.session.commit()

        db.session.delete(like)
        db.session.commit()

        self.assertNotIn(self.m2, self.u1.likes)


    def test_multiple_users_like_same_message(self):
        """Can multiple users like the same message?"""
        like1 = Likes(user_id=self.u1.id, message_id=self.m2.id)
        like2 = Likes(user_id=self.u2.id, message_id=self.m2.id)
        db.session.add_all([like1, like2])
        db.session.commit()

        self.assertIn(self.m2, self.u1.likes)
        self.assertIn(self.m2, self.u2.likes)


    def test_user_delete_message(self):
        """Can a user delete their own message?"""
        db.session.delete(self.m1)
        db.session.commit()

        self.assertNotIn(self.m1, self.u1.messages)

  
    def test_invalid_message(self):
        """Test creating a message with invalid data."""
        invalid_message = Message(text=None, user_id=self.u1.id)
        db.session.add(invalid_message)
        with self.assertRaises(Exception):
            db.session.commit()

if __name__ == "__main__":
    import unittest
    unittest.main()
