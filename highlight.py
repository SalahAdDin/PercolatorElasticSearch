import re

from collections import defaultdict

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Query

class Percolate(Query):
    name = 'percolate'

client = Elasticsearch()

index = 'titles'
text = "Bireylerin bir arada bulunması, iletişime geçmesi, kendi sosyal mekânlarını oluşturmasıyla kamusal özellik kazanan kentsel açık mekânlar küreselleşme ve yeni yaşam biçimlerinin ortaya çıkmasıyla birlikte zedelenmeye ve önemini kaybetmeye başlamıştır. Özellikle 1990’lı yıllardan itibaren inşa edilen kapalı konut sitelerinin çevresinde kalan bu alanlarda insan-çevre ilişkisi göz ardı edilmiş ve kentten kopuk, atıl durumda kalan sorunlu alanlar ortaya çıkmıştır. Çalışmanın amacı kapalı konut sitelerinin dışında kalan kamusal açık mekânların insan ve çevre ilişkisi açısından barındırdığı sorunlara dikkat çekmek, teorik bulguları İzmir kenti Mavişehir örnekleminde gerçekleştirilen ve sistematik gözlem çalışmasına dayanan bir alan çalışması ile test etmektir. Araştırma sonucunda kapalı konut sitelerinin bulunduğu yerlerde kamusal açık alanların sürdürülebilirliğinin tehdit altında olduğu, söz konusu problemin kapalı sitelerin yarattığı fiziksel ve sosyal ayrışmadan kaynaklandığı belirlenmiştir. Bunların sonucu olarak kamusal açık alanlarda etkileşime olanak vermeyen mekânlar ortaya çıkmakta, kullanım yoksunluğuna bağlı olarak güvensiz mekânlar oluşmaktadır. İzmir Mavişehir’de gerçekleştirilen alan çalışmasında farklı dönemde inşa edilen ve farklı tasarım niteliklerine sahip iki site karşılaştırmalı olarak incelendiğinde teorik bulgular sistematik gözlem verileriyle de desteklenmiştir. Mavişehir’de site sınırlarının olmadığı ve yaya erişiminin engellenmediği 1. etap konut yerleşiminin bulunduğu alanda yer alan park ve rekreasyon alanlarının, Albayrak kapalı konut sitesinin bulunduğu alandaki kamusal açık alanlara göre gece ve gündüz çok daha etkin kullanıldığı, tasarım ve peyzaj elemanlarının daha nitelikli olduğu tespit edilmiştir. Albayrak konut sitesi yakın çevresindeki açık kamusal alanların tasarım ve peyzaj donatısının çok yetersiz olduğu, etkin biçimde kullanılmadığı, atıl, güvensiz ve suça meyil oluşturan ortamlar hazırladığı gözlenmiştir. Araştırma sonuçları kapalı konut sitelerinin insan ve andçevre ilişkilerini zedelediğini, kamusal açık mekânların ve kamusal yaşamın sürdürülebilirliği açısından önemli açmazlar barındırdığını ortaya çıkarmıştır. Anahtar sözcükler: İnsan-çevre ilişkisi; kamusal açık alanlar; kapalı konut siteleri."

# s = Search().using(client).index(index).query("percolate", field='query', document={'title': text}).highlight('title', number_of_fragments=0)
# s = s.highlight_options(pre_tags='<a href=\"\">', post_tags='</a>')

s = Search().using(client).index(index).query("percolate", field='query', document={'title': text})

# print(s.to_dict())

response = s.execute()

"""
results = []
for hit in response:
    for fragment in hit.meta.highlight.title:
        results.append(fragment)

results = list(dict.fromkeys(results))
print(results)
"""

def get_response(client, index, query):
    s = Search().using(client).index(index).query("percolate", field='query', document={'title': query})
    response = s.execute()
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

"""
for term in terms:
    text = text.replace(term, "<a href=\"\">{}</a>".format(term))
"""

def get_highlighted_text(terms, text, links):
    for term, link in zip(terms, links):
        insensitive_term = re.compile(re.escape(term), re.IGNORECASE)
        text = insensitive_term.sub('<a href="{}">\g<0></a>'.format(link), text)
    return text

def get_highlighted_text_2(dic_results, text):
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
