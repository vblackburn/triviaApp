import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(selection, request=None):
  if request:
    page = request.args.get('page', 1, type=int)
  else:
    page = 1

  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  formatted_questions = questions[start:end]
  return formatted_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app, resources={r"/*": {"origins": "*"}})
  
  # CORS Headers 
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,PUT,POST,DELETE,OPTIONS')
    return response

  '''
  This endpoint gets a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category and the success value.
  '''
  @app.route('/categories', methods=['GET'])
  def get_categories():
    try:
      categories = Category.query.order_by(Category.id).all()
      cat_dict = {cat.id:cat.type for cat in categories}

      return jsonify({
        'success': True,
        'categories': cat_dict
      })
    except:
      abort(404)


  '''
  This endpoint gets a list of question objects, total number of question, current categories of selected questions, a dictionary of all the categories, and the success value.
  - Optional request argument 'page' can be use to navigate paginated questions, default is page=1
  '''

  @app.route('/questions', methods=['GET'])
  def get_questions():
    questions = Question.query.order_by(Question.id).all()
    formatted_questions = paginate_questions(questions, request)

    categories = Category.query.order_by(Category.id).all()
    cat_dict = {cat.id:cat.type for cat in categories}

    if len(formatted_questions) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'questions': formatted_questions,
      'total_questions': len(questions),
      'current_category': None,
      'categories': cat_dict
    })


  '''
  This endpoint deletes the questions realted to the passed `question_id` and returns the deleted id and the success value.
  - Required Arguments: `question_id` imust be provided in URL
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id==question_id).one_or_none()
      if question is None:
        abort(404)

      question.delete()

      return jsonify({
          'success': True,
          'deleted': question_id
      })
    except:
      abort(422)

  '''
  This endpoint creates and persists a new question to the database.
  - Required Arguments: `question`, `answer`, `difficulty`, and `category` must all be provided in a JSON object
  '''

  @app.route('/questions', methods=['POST'])
  def new_question():
    
    data = request.get_json()

    new_question = data.get('question', '')
    new_answer = data.get('answer', '')
    new_category = data.get('category', None)
    new_difficulty = data.get('difficulty', None)

    if new_question == '' or new_answer == '' or new_category is None or new_difficulty is None:
      abort(400)
    
    try:
      question = Question(
        question=new_question, 
        answer=new_answer, 
        category=new_category, 
        difficulty=new_difficulty)

      question.insert()

      return jsonify({
          'success': True,
          'created': question.id,
          'message': 'Question Created!'
      }), 201
    except:
      abort(422)

  '''
  This endpoint gets questions that related to submitted search term, number of questions found and the success value.
  - Required Arguments: `searchTerm` in a JSON object
  '''

  @app.route('/questions/search', methods=['POST'])
  def questions_search():
    try:
      data = request.get_json()
      search_term = data.get('searchTerm', None)
      if search_term:
        questions = Question.query.filter(Question.question.ilike('%{}%'.format(search_term))).all()
        formatted_questions = paginate_questions(questions)

        return jsonify({
          'success': True,
          'questions': formatted_questions,
          'total_questions': len(questions)
        })
    except:
      abort(422)


  '''
  This endpoint gets questions related to a selected category, the total number of questions in that category, current category, a dictionary of all the categories, and the success value.
  - Required Arguments: `category_id` must be provided in URL
  '''

  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_questions_by_category(category_id):
    try:
      questions = Question.query.order_by(Question.id).filter(Question.category==category_id).all()
      formatted_questions = paginate_questions(questions, request)

      categories = Category.query.order_by(Category.id).all()
      cat_dict = {cat.id:cat.type for cat in categories}

      if len(formatted_questions) == 0:
        abort(404)

      return jsonify({
        'success': True,
        'questions': formatted_questions,
        'total_questions': len(questions),
        'current_category': category_id,
        'categories': cat_dict
      })
    except:
      abort(422)

  '''
  This endpoint gets a random question that the user has not had previously from the selected category and the success value.
  - Required Arguments: `prevuous_questions` and `quiz_category`
  '''
  @app.route("/quizzes", methods=['POST'])
  def get_question_for_quiz():
    try:
      data = request.get_json()
      previous_questions = data.get('previous_questions',[])
      quiz_category = data.get('quiz_category', None)

      if quiz_category['id'] == 0:
        questions = Question.query.filter(Question.id.notin_(previous_questions)).all()
      else:
        questions = Question.query.filter(Question.category==quiz_category['id']).filter(Question.id.notin_(previous_questions)).all()
      
      available_questions = len(questions)

      if available_questions > 0:
        return jsonify({
            'success': True,
            'question': Question.format(questions[random.randrange(0, available_questions)])
          })
      else:
        return jsonify({
            'success': True,
            'question': None
          })

    except:
      abort(422) 

  '''
  The following endpoint handle return JSON objects for the following errors
  - 400
  - 404
  - 405
  - 422
  - 500
  '''
  
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': 'Bad Request'
    }),400

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'Not Found'
    }),404

  @app.errorhandler(405)
  def not_found(error):
    return jsonify({
        'success': False,
        'error': 405,
        'message': 'Method Not Allowed'
    }),405

  @app.errorhandler(422)
  def uproccessable(error):
    return jsonify({
        'success': False,
        'error': 422,
        'message': 'Unproccessable'
    }),422

  @app.errorhandler(500)
  def internal_server_error(error):
    return jsonify({
        'success': False,
        'error': 500,
        'message': 'Internal Server Error'
    }),500

  return app

    