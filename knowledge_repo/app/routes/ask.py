""" Route for displaying and posting questions
"""
import os

from flask import request, render_template, Blueprint, current_app, jsonify
import requests

from ..models import PageView

blueprint = Blueprint(
    'ask', __name__, template_folder='../templates', static_folder='../static')


@blueprint.route('/ask')
@PageView.logged
def render_ask():
    """ Renders the questions view """
    return render_template("ask.html", questions=get_questions())


def get_questions():
    """Retrieve list of questions for this knowledge repo"""
    uri = 'https://api.github.com/repos/{user}/{repo}/issues'.format(
      user='outlierbio', repo='ob-knowledge')
    issues = requests.get(uri).json()
    return [
        {
            'number': issue['number'],
            'title': issue['title'],
            'body': issue['body'],
            'url': issue['html_url']
        } for issue in issues
    ]


def submit_question(title, body):
    """Submit new question to the knowledge repo"""
    uri = 'https://api.github.com/repos/{user}/{repo}/issues'.format(
      user='outlierbio', repo='ob-knowledge')
    r = requests.post(uri, json={'title': title, 'body': body}, 
                      auth=('obanon', os.environ.get('GITHUB_PWD')))
    return r.json()


@blueprint.route('/questions', methods=['GET', 'POST'])
@PageView.logged
def questions():
    """ Renders the create knowledge view """
    if request.method == 'GET':
        questions = get_questions()
        return jsonify(questions)
    elif request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('body')
        if not title:
          return render_template('error.html')
        response = submit_question(title, body)
        return jsonify({
            'number': response['number'],
            'title': title,
            'body': body})