from flask_restful import Api, Resource
from flask import Flask, request
from covidqa import covid_qa_system
from http import HTTPStatus


class CovidQA(Resource):
    """This is the Flask API object for the QA system."""

    def get(self):
        if 'question' in request.args:
            incoming_question = request.args.get('question')
            outgoing_answers = covid_qa_system(question=incoming_question)
            return ({'response': outgoing_answers}, int(HTTPStatus.OK))
        else:
            return ({
                'response': [],
                'error_message': 'Could not find "question" as a query parameter for GET!'},
                int(HTTPStatus.BAD_REQUEST))


app = Flask(__name__)
# Configure flask_restful to jsonify arbitrary objects.
app.config['RESTFUL_JSON'] = {
    'default': lambda x: x.__dict__,
    'ensure_ascii': False,
    'sort_keys': True,
    'indent': 4
}
api = Api(app)
# GET the available responses for an input question.
api.add_resource(CovidQA, '/respond')
