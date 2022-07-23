import os
from select import select
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random


from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_all(request, select):

    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    ques = [view.format() for view in select]
    current_ques = ques[start:end]

    return current_ques


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
    @DONE: Set up CORS. Allow '*' for origins.
    Delete the sample route after completing the TODOs
    '''
    CORS(app, resources={r'/api/*': {'origins': '*'}})
    '''
    @DONE: Use the after_request decorator to set Access-Control-Allow
    '''
    @app.after_request
    def after_request(response):
        response.headers.add(
          'Access-Control-Allow-Headers', 'Content-Type,Authorization,true'
        )
        response.headers.add(
          'Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS'
        )
        return response
    '''
    @DONE:
    Create an endpoint to handle GET requests
    for all available categories.
    '''
    @app.route('/categories')
    def get_all():
        show = Category.query.order_by(Category.id).all()

        if len(show) == 0:
            abort(404)

        fmt_category = {category.id: category.type for category in show}

        return jsonify({
          'success': True,
          'categories': fmt_category
        })

    '''
    @DONE:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom
    of the screen for three pages.
    Clicking on the page numbers should update the questions.
    '''
    @app.route('/questions')
    def get_questions():
        category = Category.query.all()
        fmt_category = {new.id: new.type for new in category}

        select = Question.query.all()
        current_ques = paginate_all(request, select)

        if len(current_ques) == 0:
            abort(404)

        return jsonify({
          'success': True,
          'questions': current_ques,
          'total_questions': len(select),
          'categories': fmt_category,
          'current_category': None
        })
    '''
    @DONE:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question,
    the question will be removed.
    This removal will persist in the database and when you refresh the page.
    '''
    @app.route('/questions/<int:id>', methods=['DELETE'])
    def trash_question(id):
        try:
            get_question = Question.query.get(id)

            if get_question is None:
                abort(404)

            get_question.delete()

            return jsonify({
                  'success': True,
                  'deleted': get_question.id
            })

        except:
            abort(422)

    '''
    @DONE:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will
    appear at the end of the last page
    of the questions list in the "List" tab.
    '''
    @app.route('/questions', methods=['POST'])
    def add_new():
        try:
            body = request.get_json()
            if not body:
                abort(404)

            new_question = body.get('question', None)
            new_answer = body.get('answer', None)

            new_difficulty = body.get('difficulty', None)
            new_category = body.get('category', None)

            questions = Question(question=new_question,
                                 answer=new_answer,
                                 category=new_category,
                                 difficulty=new_difficulty)
            questions.insert()

            return jsonify({
                  'success': True,
                  'created': questions.id
            })

        except:
            abort(422)
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
    def search_term():
        try:
            body = request.get_json()
            search = body.get('searchTerm', None)

            if not search:
                abort(400)

            fmt_search = '%{}%'.format(search)
            select = Question.query.filter(Question.question.ilike
                                           (fmt_search)).all()
            current_ques = paginate_all(request, select)

            return jsonify({
              'success': True,
              'questions': current_ques,
              'total_questions': len(select),
              'current_category': None
            })

        except:
            abort(422)
    '''
    @DONE:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    '''
    @app.route('/categories/<int:id>/questions')
    def cat_questions(id):
        try:
            get_cat = Category.query.filter_by(id=id)
            current_cat = [add.type for add in get_cat]

            select = Question.query.filter_by(category=id).all()
            current_ques = [set.format() for set in select]

            return jsonify({
              'success': True,
              'questions': current_ques,
              'total_questions': len(select),
              'current_category': current_cat
            })

        except:
            abort(404)
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
    def get_quiz():
        try:
            body = request.get_json()
            if not body:
                abort(422)

            cat = body.get('quiz_category')
            pre_questions = body.get('previous_questions')

            if cat['type'] == 'click':
                new_ques = Question.query.filter(
                  Question.id.notin_((pre_questions))
                ).all()

            else:
                new_ques = Question.query.filter_by(
                  category=cat['id']).filter(
                    Question.id.notin_((pre_questions))).all()
            send_question = random.choice(
                  new_ques).format()if new_ques else None

            return jsonify({
              'success': True,
              'question': send_question
            })

        except:
            abort(422)
    '''
    @DONE:
    Create error handlers for all expected errors
    including 404 and 422.
    '''
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
          'message': 'bad_request'
        }), 400

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
          'success': False,
          'error': 405,
          'message': 'method not allowed'
        }), 405

    @app.errorhandler(500)
    def internal_server_error(error):

        return jsonify({
          'success': False,
          'error': 500,
          'message': 'internal server error'
        }), 500

    return app
