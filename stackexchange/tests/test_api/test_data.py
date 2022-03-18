import random

from stackexchange.tests import factories


def setup_test_data():
    """Set up the test data.
    """
    # Create some users
    users = factories.UserFactory.create_batch(size=100)
    # Award some badges to the users
    for user in users:
        factories.UserBadgeFactory.create_batch(size=random.randint(0, 20), user=user)
    # Create some questions from the users
    questions = []
    for user in users:
        user_questions = factories.QuestionFactory.create_batch(size=random.randint(0, 3), owner=user)
        for question in user_questions:
            factories.CommentFactory.create_batch(size=random.randint(0, 3), post=question, user=user)
        questions += user_questions
    # Post some answers to the questions
    for question in questions:
        user = random.choice(users)
        user_answers = factories.AnswersFactory.create_batch(size=random.randint(0, 3), parent=question, owner=user)
        for answer in user_answers:
            factories.CommentFactory.create_batch(size=random.randint(0, 3), post=answer, user=user)
