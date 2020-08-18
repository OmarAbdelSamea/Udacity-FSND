import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

# Change this variable with to change questions per page
QUESTIONS_PER_PAGE = 10

# flask app setup
def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @DONE: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, origins='*')
 
  '''
  @DONE: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')  
    return response  
 
  '''
  @DONE: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories', methods=['GET'])
  def get_categories():
    categories = Category.query.all()
    formatted_categories = [category.format() for category in categories]
    return jsonify({
      'success': True,
      'categories': formatted_categories
    })


  '''
  @DONE: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  # Function to paginate questions
  def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start =  (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    return current_questions

  @app.route('/questions', methods=['GET'])
  def get_paginated_questions():
    categories = Category.query.all()
    questions = Question.query.order_by(Question.category).all()
    paginated_questions = paginate_questions(request, questions)
    if not paginated_questions:
      abort(404) 
    return jsonify({
      'success': True,
      'questions': paginated_questions,
      'total_questions': len(questions),
      'categories': [category.format() for category in categories]
    })

  '''
  @DONE: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    question = Question.query.get(question_id)
    if not question:
      abort(404)
    Question.delete(question)
    return jsonify({
      'success': True,
      'deleted_question': question_id
    })
  '''
  @DONE: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions/create', methods=['POST'])
  def create_question():
    try:
      body = request.get_json()
      question = Question(
        question=body['question'],
        answer=body['answer'],
        category=body['category'],
        difficulty=body['difficulty']
      )
      question.insert()
      return jsonify({
        'success': True,
        'question': question.question,
        'answer': question.answer,
        'category': question.category,
        'difficulty': question.difficulty
      })
    except:
      abort(400)  
  '''
  @DONE: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_question():
    try:  
      body = request.get_json()
      search_term = body['searchTerm']
      questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
      if not questions:
        abort(404)
      return jsonify({
        'success': True,
        'questions': [question.format() for question in questions]
      })  
    except:
        abort(400)  
    

  '''
  @DONE: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_questions_by_category(category_id):
    questions = Question.query.filter(Question.category == category_id).all()
    category = Category.query.get(category_id)
    if not questions:
      abort(404)
    return jsonify({
      'success': True,
      'questions': [question.format() for question in questions],
      'total_questions': len(questions),
      'current_category': category.type
    })  
  '''
  @DONE: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def quizz_questions():
    try:
      body = request.get_json()
      old_questions = body['previous_questions']
      # front end is modfied to return only category id check README for how to use with curl
      all_questions = Question.query.filter(Question.category == body['quiz_category'])
      unique_questions = [question for question in all_questions if question.id not in old_questions]
      if not all_questions:
        abort(404)
      if not unique_questions:
        question = False
      else:
        question = random.choice(unique_questions).format() 
      return jsonify({
        'success': True,
        'question': question
      })
    except:
      abort(400)  
  '''
  @DONE: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
      return jsonify({
          "success": False, 
          "error": 404,
          "message": "resource not found"
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
      return jsonify({
          "success": False, 
          "error": 422,
          "message": "unprocessable"
      }), 422

  @app.errorhandler(400)
  def bad_request(error):
      return jsonify({
          "success": False, 
          "error": 400,
          "message": "bad request"
      }), 400  

  @app.errorhandler(500)
  def server_error(error):
      return jsonify({
          "success": False, 
          "error": 500,
          "message": "Internal server error"
      }), 500      
      
  return app

    