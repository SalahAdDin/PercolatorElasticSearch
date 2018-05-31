import os
import re
import webbrowser

from collections import defaultdict

from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Query
from flask import (
    Flask,
    request,
    render_template
)

app = Flask(__name__)


class Percolate(Query):
    name = 'percolate'

def get_response(client, index, query):
    s = Search().using(client).index(index).query("percolate", field='query', document={'title': query})
    response = s.execute()
    # get all matches: s.scan() https://elasticsearch-dsl.readthedocs.io/en/latest/search_dsl.html#pagination
    return response

def get_highlighted_term(response):
    dic_results = defaultdict(list)
    for hit in response:
        for query in hit.query:
            if query == 'span_term':
                dic_results[hit.query.span_term.title].append(hit.doc_id)
            if query == 'span_near':
                phrase = ''
                for title in hit.query.span_near.clauses:
                    phrase += title.span_term.title + ' '
                dic_results[phrase[:-1]].append(hit.doc_id)
    return dic_results

def get_highlighted_text(dic_results, text):
    for term, doc_ids in dic_results.items():
        insensitive_term = re.compile(re.escape(term), re.IGNORECASE)
        if len(doc_ids) > 1:
            result_text = "<ul id='multiple-links'>"
            for doc_id in doc_ids:
                result_text += "<li><a href='http://localhost/{0}'>{1}</a></li>".format(doc_id, term)
            result_text += "</ul>"
            text = insensitive_term.sub(result_text, text)
        else:
            text = insensitive_term.sub('<a href="http://localhost/{}">\g<0></a>'.format(doc_ids[0]), text)
    return text

@app.route('/')
def my_form():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def my_form_post():
    client = Elasticsearch()
    index = 'titles'
    query = request.form['text']
    response = get_response(client, index, query)
    result_dict = get_highlighted_term(response)
    final_text = get_highlighted_text(result_dict, query)


    try:
        message = final_text
    except:
        message = "No result!"

    return message
