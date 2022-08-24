import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_user = os.getenv('DB_USER', 'student')
        self.database_password = os.getenv('DB_PASSWORD', 'student')        
        self.database_path = 'postgresql://{}:{}@{}/{}'.format(self.database_user, self.database_password, 'localhost:5432', self.database_name)

        
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
        
        self.new_question = {
            'question': 'How many ears do rabbits have?',
            'answer': 'Four (4)',
            'category': '3',
            'difficulty': '3'
        }

    
    def tearDown(self):
        """Executed after each test"""
        pass

    """
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertEqual(data['success'], True)

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=207')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_get_all_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(data['total_categories'])

    def test_delete_question(self):
        res = self.client().delete('/questions/22')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id==22).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 22)
        self.assertEqual(question, None)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])

    def test_create_new_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['added'])
        self.assertTrue(len(data['questions']))

    def test_405_if_question_creation_not_allowed(self):
        res = self.client().post('/questions/63', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['message'], 'method not allowed')

    def test_get_question_search_with_results(self):
        res = self.client().post('/questions/search', json={'search':'invented'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_searched_questions'])

    def test_get_question_search_without_results(self):
        res = self.client().post('/questions/search', json={'search':'Ecdysis'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 0)
        self.assertEqual(data['total_searched_questions'], 0)

    def test_find_questions_by_given_category_id(self):
        res = self.client().get('/categories/2/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    def test_404_cannot_find_questions_by_given_category_id(self):
        res = self.client().get('/categories/900/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['message'], 'resource not found')
        self.assertEqual(data['success'], False)

    def test_play_quiz(self):
        res = self.client().post('/quizzes', json={
            'previous_questions': [],
            'quiz_category': {'id': '4', 'type': 'History'}
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()