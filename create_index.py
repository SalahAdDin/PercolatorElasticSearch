import json

from time import clock

from elasticsearch.helpers import bulk
from elasticsearch_dsl import (
    analysis,
    analyzer,
    connections,
    DocType,
    Integer,
    Percolator,
    Text
)
from elasticsearch_dsl.query import (
    SpanNear,
    SpanTerm
)

# Read the json File
json_data = open('titles.json').read()
data = json.loads(json_data)

docs = data['response']['docs']


# create a new default elasticsearch connection
connections.configure(
    default={'hosts': 'localhost:9200'},
)

# create a new custom filter for lowercase in turkish
turkish = analysis.token_filter('turkish_lowercase', type="lowercase", language="turkish")

# create a custom analyzer for turkish lowercase
turkish_lowercase = analyzer('turkish_lowercase',
    type = "custom",
    tokenizer="whitespace",
    filter=[turkish],
)

class Document(DocType):
    title = Text(
        analyzer = turkish_lowercase,
        # term_vector = "with_positions_offsets",
    )
    doc_id = Integer()
    query = Percolator()    # query is a percolator

    class Meta:
        index = 'titles' # index name
        doc_type = '_doc'

    def save(self, **kwargs):
        return super(Document, self).save(**kwargs)


# create the mappings in elasticsearch
Document.init()

# create a list for storing all documents
documents = []

# index the query
start = clock()
regex = "(.*)(\(.*)\)?"
for doc in docs:
    # convert title to a string
    terms = doc['title'].split(" ")
    print(terms)
    doc_id = doc['id']
    # crate a list for clauses
    clauses = []
    for term in terms:
        # each word in terms going to be a SpanTerm
        field = SpanTerm(title=term.lower())
        # add each SpanTerm to clauses
        clauses.append(field)
    # query going to be a SpanNear query
    if len(clauses) <2:
        query = clauses[0]
    else:
        query = SpanNear(clauses=clauses, slop=0, in_order=True)
    # create a new Document item with SpanNear query
    item = Document(query=query, doc_id=doc_id) # title=doc['title'],
    # add item to the list
    documents.append(item)
print("Total time (getting titles as index documents): ", clock()-start)

# register all documents in the index using bulk
start = clock()
bulk(connections.get_connection(), (d.to_dict(True) for d in documents))
print("Total time (putting documents in index using bulk): ", clock()-start)
