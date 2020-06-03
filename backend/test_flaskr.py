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
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        self.new_question = {
            'question': 'test question',
            'answer': 'test answer',
            'difficulty': 1,
            'category': 1
        }

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    Test for successful GET request at /cateogories endpoint
    """
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['categories'])

    """
    Test for successful GET request at /questions endpoint, including pagination
    """

    def test_get_paginated_questions(self):
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
    
    """
    Test for failed GET request at /questions endpoint due to going beyond valid page number
    """

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not Found')  

    """
    Test for successful DELETE request at /questions endpoint for question id = 10
    """

    def test_delete_questions(self):
        res = self.client().delete('/questions/10')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 10)

    """
    Test for failed DELETE request at /questions endpoint a question that doesn't exist
    """

    def test_delete_questions_does_not_exist(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unproccessable')

    """
    Test for successful POST request at /cateogories endpoint to create a new question
    """

    def test_create_new_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 201)
        self.assertEqual(data['success'], True)

    """
    Test for failed POST request at /questions endpoint when a argument is missing from the questions JSON obhect
    """

    def test_400_if_missing_category(self):
        res = self. client(). post('/questions', json={"question": "New Question", "answer":"Just Added", "difficulty":"5"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Bad Request')

    """
    Test for successful POST request at /questions/search endpoint
    """

    def test_search_question(self):
        res = self.client().post('/questions/search', json={'searchTerm': 'is'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    """
    Test for successful POST request at /questions/search endpoint that returns no search results
    """

    def test_search_questions_no_results(self):
        res = self.client().post('/questions/search', json={'searchTerm': 'asdfkjasldalsdhlj'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_questions'], 0)

    """
    Test for failed POST request at /questions/search endpoint due to missing searchTerm argument
    """

    def test_search_questions_no_searchTerm(self):
        res = self.client().post('/questions/search')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unproccessable')

    """
    Test for successful GET request at /cateogories/1/questions endpoint
    """

    def test_get_questions_by_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    """
    Test for failed GET request at /cateogories/1/questions endpoint due to category id that doesn't exist
    """

    def test_get_questions_by_category_does_not_exist(self):
        res = self.client().get('/categories/1000/questions')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unproccessable')

    """
    Test for successful POST request at /quizzes endpoint
    """

    def test_get_question_for_quiz(self):
        res = self.client().post('/quizzes', json={"previous_questions": [], "quiz_category": {'id': 1, 'type': 'Science'}})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    """
    Test for failed POST request at /quizzes endpoint due to quiz category that doesn't exist
    """

    def test_get_question_for_quiz_bad_quiz_category(self):
        res = self.client().post('/quizzes', json={"previous_questions": [], "quiz_category": {'id': 1000, 'type': 'Science'}})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['question'], None)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()