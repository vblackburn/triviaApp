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

  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={r"/*": {"origins": "*"}})
  
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''

  # CORS Headers 
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,PUT,POST,DELETE,OPTIONS')
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
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
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
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
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
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
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

  @app.route('/questions', methods=['POST'])
  def new_question():
    
    data = request.get_json()

    new_question = data.get('question', None)
    new_answer = data.get('answer', None)
    new_category = data.get('category', None)
    new_difficulty = data.get('difficulty', None)

    if new_question is None or new_answer is None or new_category is None or new_difficulty is None:
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
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
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
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
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
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
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
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
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

    