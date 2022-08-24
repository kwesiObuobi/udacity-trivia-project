import os
from flask import Flask, request, abort, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @DONE: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs - Completed
    """
    cors = CORS(app, resources={r'*': {'origins': '*'}})
    #CORS(app, resources={"/": {"origins": "*"}})    

    """
    @DONE: Use the after_request decorator to set Access-Control-Allow - Completed
    """
    @app.after_request
    def after_request(response):
        #response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, GET, PATCH, DELETE')
        return response


    """
    @DONE:
    Create an endpoint to handle GET requests
    for all available categories. - Completed
    """
    @app.route('/categories')
    def get_categories():
        categories = Category.query.all()
        
        cat_dict = {}
        for cat in categories:
            cat_dict[cat.id] = cat.type

        return jsonify({
            'success': True,
            'categories': cat_dict,
            'total_categories': len(categories)
        })


    def paginate_questions(request, selection):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE
        questions = [question.format() for question in selection]
        current_questions = questions[start:end]
        return current_questions

    """
    @DONE:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories. - completed

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions')
    def get_questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        categories = Category.query.all()
        cat_dict = {}
        for cat in categories:
            cat_dict[cat.id] = cat.type

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(Question.query.all()),
            #'current_category': 'sports',
            'categories': cat_dict
        })


    """
    @DONE:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page. - Completed
    """ 
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.filter(Question.id == question_id).one_or_none()

        if question is None:
            abort(404)

        question.delete()
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)
        return jsonify({
            'success': True,
            'deleted': question.id,
            'questions': current_questions,
            'total_questions': len(Question.query.all())
        })

    """
    @DONE:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score. - Completed

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()
        new_question = body.get('question', None)
        new_answer= body.get('answer', None)
        new_category = body.get('category', None)
        new_difficulty = body.get('difficulty', None)

        try:
            question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
            question.insert()

            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'added': question.id,
                'questions': current_questions,
                'total_questions': len(Question.query.all())
            })
        
        except:
            abort(400)

    """
    @DONE:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question. - Completed

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        body = request.get_json()
        search = body.get('searchTerm', None)

        if search is None:
            abort(422)

        selection = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search))).all()
        current_questions = paginate_questions(request, selection)
        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_searched_questions': len(selection)
        })
        
        
    """
    @DONE:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions')
    def get_questions_by_category(category_id):
        selection = Question.query.order_by(Question.id).filter(Question.category == category_id).all()
        current_questions = paginate_questions(request, selection)
        category = Category.query.filter(Category.id == category_id).one_or_none()

        if category is None:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(current_questions),
            'current_category': category.type
        })

    """
    @DONE:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions. - not tested with curl

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def play():
        try:
            body = request.get_json()
            category = body.get('quiz_category', None)
            prev_questions = body.get('previous_questions', None)
            category_id = category['id']
            selection = []

            if category_id == 0:
                selection = Question.query.all()
            else:
                selection = Question.query.filter(Question.category == category_id).all()

            def get_next_random_question():
                question = random.choice(selection).format()
                return question
            
            current_question = get_next_random_question()
            answered_question = False       

            if current_question['id'] in prev_questions:
                answered_question = True
            
            while answered_question:
                current_question = get_next_random_question()

                if (len(prev_questions) == len(selection)):
                    return jsonify({
                        'success': True,
                        'message': 'no new questions'
                    })

            return jsonify({
                'success': True,
                'question': current_question
            })

        except Exception as e:
            print(e)
            abort(422)

    """
    @DONE:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'resource not found'
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'unprocessable'
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'bad request'
        }), 400

    @app.errorhandler(405)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': 'method not allowed'
        }), 405

    @app.errorhandler(500)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'internal server error'
        }), 500

    return app
