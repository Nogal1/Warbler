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