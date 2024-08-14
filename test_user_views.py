import os
from unittest import TestCase
from models import db, User, Message, Likes, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app
db.drop_all()
db.create_all()

class UserViewsTestCase(TestCase):
    """Test views for users."""


    def setUp(self):
        """Create test client, add sample data."""
        User.query.delete()
        Message.query.delete()
        Likes.query.delete()
        Follows.query.delete()
        db.session.commit()

        self.client = app.test_client()

        # Sample data
        self.u1 = User.signup("user1", "user1@test.com", "password", None)
        self.u2 = User.signup("user2", "user2@test.com", "password", None)
        db.session.commit()

        self.u1_id = self.u1.id
        self.u2_id = self.u2.id


    def tearDown(self):
        """Clean up fouled transactions."""
        db.session.rollback()


    def test_view_user_profile(self):
        """Can a logged-in user view a profile page?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = self.u1_id

            resp = c.get(f"/users/{self.u1_id}")
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'user1', resp.data)


    def test_view_other_user_profile(self):
        """Can a logged-in user view another user's profile page?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = self.u1_id

            resp = c.get(f"/users/{self.u2_id}")
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'user2', resp.data)


    def test_follow_redirects_if_not_logged_in(self):
        """Is a non-logged-in user redirected when trying to follow someone?"""
        with self.client as c:
            resp = c.post(f"/users/follow/{self.u2_id}", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"Access unauthorized", resp.data)


    def test_unfollow_redirects_if_not_logged_in(self):
        """Is a non-logged-in user redirected when trying to unfollow someone?"""
        with self.client as c:
            resp = c.post(f"/users/stop-following/{self.u2_id}", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"Access unauthorized", resp.data)


    def test_like_redirects_if_not_logged_in(self):
        """Is a non-logged-in user redirected when trying to like a message?"""
        m = Message(text="Test Message", user_id=self.u2_id)
        db.session.add(m)
        db.session.commit()

        with self.client as c:
            resp = c.post(f"/users/add_like/{m.id}", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"Access unauthorized", resp.data)


    def test_unlike_redirects_if_not_logged_in(self):
        """Is a non-logged-in user redirected when trying to unlike a message?"""
        m = Message(text="Test Message", user_id=self.u2_id)
        db.session.add(m)
        db.session.commit()

        like = Likes(user_id=self.u1_id, message_id=m.id)
        db.session.add(like)
        db.session.commit()

        with self.client as c:
            resp = c.post(f"/users/remove_like/{m.id}", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"Access unauthorized", resp.data)


    def test_view_followers(self):
        """Can a logged-in user view their followers?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = self.u1_id

            resp = c.get(f"/users/{self.u1_id}/followers")
            self.assertEqual(resp.status_code, 302)

    def test_view_following(self):
        """Can a logged-in user view the users they are following?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = self.u1_id

            resp = c.get(f"/users/{self.u1_id}/following")
            self.assertEqual(resp.status_code, 302)

    def test_followers_redirects_if_not_logged_in(self):
        """Is a non-logged-in user redirected when trying to view followers?"""
        with self.client as c:
            resp = c.get(f"/users/{self.u1_id}/followers", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"Access unauthorized", resp.data)

    def test_following_redirects_if_not_logged_in(self):
        """Is a non-logged-in user redirected when trying to view following?"""
        with self.client as c:
            resp = c.get(f"/users/{self.u1_id}/following", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"Access unauthorized", resp.data)


    def test_update_profile_redirects_if_not_logged_in(self):
        """Is a non-logged-in user redirected when trying to update profile?"""
        with self.client as c:
            resp = c.post(f"/users/profile", data={"username": "updateduser", "email": "newemail@test.com", "password": "password"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"Access unauthorized", resp.data)


    

