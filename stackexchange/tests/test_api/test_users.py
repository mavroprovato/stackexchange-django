"""Users API testing
"""
import random
import unittest

import dateutil.parser
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from stackexchange import enums, models
from .. import factories


class UserTests(APITestCase):
    """Users view set tests
    """
    @classmethod
    def setUpTestData(cls):
        """Set up the test data.
        """
        users = factories.UserFactory.create_batch(size=100)
        # Create some questions from the users
        questions = []
        for user in users:
            questions += factories.QuestionFactory.create_batch(size=random.randint(0, 3), owner=user)
        # Post some answers to the questions
        for question in questions:
            factories.AnswersFactory.create_batch(
                size=random.randint(0, 3), parent=question, owner=random.choice(users))

    def test_list(self):
        """Test users list endpoint
        """
        # Test that the list endpoint returns successfully
        response = self.client.get(reverse('user-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the user information returned is correct
        for row in response.json()['items']:
            user = models.User.objects.get(pk=row['user_id'])
            self.assertEqual(row['is_employee'], user.is_employee)
            self.assertEqual(row['reputation'], user.reputation)
            self.assertEqual(dateutil.parser.parse(row['creation_date']), user.creation_date)
            self.assertEqual(row['location'], user.location)
            self.assertEqual(row['website_url'], user.website_url)
            self.assertEqual(row['display_name'], user.display_name)

    def test_list_sort_by_reputation(self):
        """Test the user list sorted by user reputation.
        """
        response = self.client.get(reverse('user-list'), data={'sort': 'reputation', 'order': 'asc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reputations = [row['reputation'] for row in response.json()['items']]
        self.assertListEqual(reputations, sorted(reputations))

        response = self.client.get(reverse('user-list'), data={'sort': 'reputation', 'order': 'desc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reputations = [row['reputation'] for row in response.json()['items']]
        self.assertListEqual(reputations, sorted(reputations, reverse=True))

    def test_list_sort_by_creation_date(self):
        """Test the user list sorted by user creation date.
        """
        response = self.client.get(reverse('user-list'), data={'sort': 'creation', 'order': 'asc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        creation_dates = [row['creation_date'] for row in response.json()['items']]
        self.assertListEqual(creation_dates, sorted(creation_dates))

        response = self.client.get(reverse('user-list'), data={'sort': 'creation', 'order': 'desc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reputation = [row['creation_date'] for row in response.json()['items']]
        self.assertListEqual(reputation, sorted(reputation, reverse=True))

    @unittest.skip("Postgres and python sorting algorithms differ")
    def test_list_sort_by_display_name(self):
        """Test the user list sorted by user display name.
        """
        response = self.client.get(reverse('user-list'), data={'sort': 'name', 'order': 'asc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        display_names = [row['display_name'] for row in response.json()['items']]
        self.assertListEqual(display_names, sorted(display_names))

        response = self.client.get(reverse('user-list'), data={'sort': 'name', 'order': 'desc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        display_names = [row['display_name'] for row in response.json()['items']]
        self.assertListEqual(display_names, sorted(display_names, reverse=True))

    def test_list_in_name(self):
        """Test the in name filter for users.
        """
        # Create a user that will surely be returned
        user = factories.UserFactory.create(display_name='John Doe')
        response = self.client.get(reverse('user-list'), data={'inname': 'oh'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Assert that all users contain the string in their display name
        self.assertTrue(all('oh' in row['display_name'] for row in response.json()['items']))
        # Assert that the user was returned
        self.assertIn(user.id, [int(row['user_id']) for row in response.json()['items']])

    def test_detail(self):
        """Test the user detail endpoint.
        """
        # Test getting one user
        user = random.sample(list(models.User.objects.all()), 1)[0]
        response = self.client.get(reverse('user-detail', kwargs={'pk': user.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['items'][0]['user_id'], user.pk)

    def test_detail_multiple(self):
        """Test the user detail endpoint for multiple ids.
        """
        # Test getting multiple users
        users = random.sample(list(models.User.objects.all()), 3)
        response = self.client.get(reverse('user-detail', kwargs={'pk': ';'.join(str(user.pk) for user in users)}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertSetEqual({row['user_id'] for row in response.json()['items']}, {user.pk for user in users})

    def test_privileges(self):
        """Test the user privileges endpoint.
        """
        user = random.sample(list(models.User.objects.all()), 1)[0]
        response = self.client.get(reverse('user-privileges', kwargs={'pk': user.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Assert that the privileges are returned by ascending reputation
        self.assertListEqual([row['reputation'] for row in response.json()['items']],
                             sorted([row['reputation'] for row in response.json()['items']]))
        # Assert that the user has the correct privileges based on the reputation
        user_privileges = [privilege for privilege in enums.Privilege if privilege.reputation <= user.reputation]
        self.assertEqual(len(user_privileges), len(response.json()['items']))
        # Assert the privilege descriptions and short descriptions are correct
        self.assertListEqual([privilege.description for privilege in user_privileges],
                             [row['description'] for row in response.json()['items']])
        self.assertListEqual([privilege.name.replace('_', ' ').capitalize() for privilege in user_privileges],
                             [row['short_description'] for row in response.json()['items']])

    def test_answers(self):
        """Test user answers endpoint
        """
        # Test that the list endpoint returns successfully
        user = random.sample(list(models.User.objects.all()), 1)[0]
        response = self.client.get(reverse('user-answers', kwargs={'pk': user.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the user information returned is correct
        for row in response.json()['items']:
            answer = models.Post.objects.get(pk=row['answer_id'])
            self.assertEqual(row['owner']['reputation'], answer.owner.reputation)
            self.assertEqual(row['owner']['user_id'], answer.owner.pk)
            self.assertEqual(row['owner']['display_name'], answer.owner.display_name)
            self.assertEqual(row['score'], answer.score)
            self.assertEqual(dateutil.parser.parse(row['last_activity_date']), answer.last_activity_date)
            self.assertEqual(dateutil.parser.parse(row['creation_date']), answer.creation_date)
            self.assertEqual(row['question_id'], answer.parent.pk)
            self.assertEqual(row['content_license'], enums.ContentLicense[answer.content_license].name)

    def test_answers_sort_by_activity(self):
        """Test the user answer list sorted by question activity date.
        """
        user = random.sample(list(models.User.objects.all()), 1)[0]
        response = self.client.get(
            reverse('user-answers', kwargs={'pk': user.pk}), data={'sort': 'activity', 'order': 'asc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reputations = [row['last_activity_date'] for row in response.json()['items']]
        self.assertListEqual(reputations, sorted(reputations))

        response = self.client.get(
            reverse('user-answers', kwargs={'pk': user.pk}), data={'sort': 'activity', 'order': 'desc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reputations = [row['last_activity_date'] for row in response.json()['items']]
        self.assertListEqual(reputations, sorted(reputations, reverse=True))

    def test_answers_sort_by_creation_date(self):
        """Test the user answer list sorted by user creation date.
        """
        user = random.sample(list(models.User.objects.all()), 1)[0]
        response = self.client.get(
            reverse('user-answers', kwargs={'pk': user.pk}), data={'sort': 'creation', 'order': 'asc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        creation_dates = [row['creation_date'] for row in response.json()['items']]
        self.assertListEqual(creation_dates, sorted(creation_dates))

        response = self.client.get(
            reverse('user-answers', kwargs={'pk': user.pk}), data={'sort': 'creation', 'order': 'desc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reputation = [row['creation_date'] for row in response.json()['items']]
        self.assertListEqual(reputation, sorted(reputation, reverse=True))

    def test_answers_sort_by_votes(self):
        """Test the user answer list sorted by votes.
        """
        user = random.sample(list(models.User.objects.all()), 1)[0]
        response = self.client.get(
            reverse('user-answers', kwargs={'pk': user.pk}), data={'sort': 'votes', 'order': 'asc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        creation_dates = [row['score'] for row in response.json()['items']]
        self.assertListEqual(creation_dates, sorted(creation_dates))

        response = self.client.get(
            reverse('user-answers', kwargs={'pk': user.pk}), data={'sort': 'votes', 'order': 'desc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reputation = [row['score'] for row in response.json()['items']]
        self.assertListEqual(reputation, sorted(reputation, reverse=True))

    def test_questions(self):
        """Test user questions endpoint
        """
        # Test that the list endpoint returns successfully
        user = random.sample(list(models.User.objects.all()), 1)[0]
        response = self.client.get(reverse('user-questions', kwargs={'pk': user.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the user information returned is correct
        for row in response.json()['items']:
            question = models.Post.objects.get(pk=row['question_id'])
            self.assertEqual(row['owner']['reputation'], question.owner.reputation)
            self.assertEqual(row['owner']['user_id'], question.owner.pk)
            self.assertEqual(row['owner']['display_name'], question.owner.display_name)
            self.assertEqual(row['view_count'], question.view_count)
            self.assertEqual(row['accepted_answer_id'], getattr(question.accepted_answer, 'pk', None))
            self.assertEqual(row['answer_count'], question.answer_count)
            self.assertEqual(row['score'], question.score)
            self.assertEqual(dateutil.parser.parse(row['last_activity_date']), question.last_activity_date)
            self.assertEqual(dateutil.parser.parse(row['creation_date']), question.creation_date)
            self.assertEqual(dateutil.parser.parse(row['last_edit_date']), question.last_edit_date)
            self.assertEqual(row['content_license'], enums.ContentLicense[question.content_license].name)
            self.assertEqual(row['title'], question.title)

    def test_questions_sort_by_activity(self):
        """Test the user question list sorted by question activity date.
        """
        user = random.sample(list(models.User.objects.all()), 1)[0]
        response = self.client.get(
            reverse('user-questions', kwargs={'pk': user.pk}), data={'sort': 'activity', 'order': 'asc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reputations = [row['last_activity_date'] for row in response.json()['items']]
        self.assertListEqual(reputations, sorted(reputations))

        response = self.client.get(
            reverse('user-questions', kwargs={'pk': user.pk}), data={'sort': 'activity', 'order': 'desc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reputations = [row['last_activity_date'] for row in response.json()['items']]
        self.assertListEqual(reputations, sorted(reputations, reverse=True))

    def test_questions_sort_by_creation_date(self):
        """Test the user question list sorted by user creation date.
        """
        user = random.sample(list(models.User.objects.all()), 1)[0]
        response = self.client.get(
            reverse('user-questions', kwargs={'pk': user.pk}), data={'sort': 'creation', 'order': 'asc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        creation_dates = [row['creation_date'] for row in response.json()['items']]
        self.assertListEqual(creation_dates, sorted(creation_dates))

        response = self.client.get(
            reverse('user-questions', kwargs={'pk': user.pk}), data={'sort': 'creation', 'order': 'desc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reputation = [row['creation_date'] for row in response.json()['items']]
        self.assertListEqual(reputation, sorted(reputation, reverse=True))

    def test_questions_sort_by_votes(self):
        """Test the user question list sorted by votes.
        """
        user = random.sample(list(models.User.objects.all()), 1)[0]
        response = self.client.get(
            reverse('user-questions', kwargs={'pk': user.pk}), data={'sort': 'votes', 'order': 'asc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        creation_dates = [row['score'] for row in response.json()['items']]
        self.assertListEqual(creation_dates, sorted(creation_dates))

        response = self.client.get(
            reverse('user-questions', kwargs={'pk': user.pk}), data={'sort': 'votes', 'order': 'desc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reputation = [row['score'] for row in response.json()['items']]
        self.assertListEqual(reputation, sorted(reputation, reverse=True))
