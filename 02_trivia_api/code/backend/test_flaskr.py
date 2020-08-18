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
        self.database_path = "postgres://{}:{}@{}/{}".format('postgres', 'postgres', 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_GET_categories_200(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_GET_paginated_questions_200(self):
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)
        categories = Category.query.all()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertEqual(data['total_questions'], len(Question.query.all()))
        self.assertEqual(data['categories'], [category.format() for category in categories])

    def test_GET_page_or_category_not_found_questions_404(self):
        res = self.client().get('/questions?category=Art&page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], "resource not found")

    def test_DELETE_question_success_200(self):
        res = self.client().delete('/questions/10')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)    
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted_question'], 10)


    def test_DELETE_question_not_found_404(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)  
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], "resource not found")

    def test_POST_add_question_success_200(self):
        res = self.client().post('/questions/create', json={"question":"test", "answer":"test1", "category":"2", "difficulty": "4"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True) 
        self.assertEqual(data['question'], 'test') 
        self.assertEqual(data['answer'], 'test1') 
        self.assertEqual(data['category'], 2) 
        self.assertEqual(data['difficulty'], 4)

    def test_POST_add_question_bad_400(self):
        res = self.client().post('/questions/create')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)  
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 400)
        self.assertEqual(data['message'], "bad request")

    def test_GET_questions_by_category_200(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True) 
        self.assertEqual(data['total_questions'], 3)
        self.assertEqual(data['current_category'], 'Science')

    def test_GET_question_by_category_not_found_404(self):
        res = self.client().get('/categories/100/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'resource not found')

    def test_POST_quizzes_200(self):
        res = self.client().post('/quizzes', json={"quiz_category": 3, "previous_questions": [13,14,15,40,50]})    
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True) 

    def test_POST_quizzes_400(self):
        res = self.client().post('/quizzes', json={"quiz": "3", "previous_questions": "15"})    
        data = json.loads(res.data)

        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 400)
        self.assertEqual(data['message'], "bad request")



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()