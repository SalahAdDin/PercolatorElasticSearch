Wikification Elasticsearch/Python
=================================

This project aims setting hyperlink to given input with Elasticsearch stored queries which means Wikification with Elasticsearch Percolate query.

Getting Started
---------------

### Prerequisites

-	Unix-like operating system (macOS or Linux) is better.
-	`python3` should be installed(using `virtualenv` is recommended)
-	`elasticsearch` should be installed.

### Installing

First, clone the project and go to the project directory

```
git clone https://github.com/SalahAdDin/PercolatorElasticSearch.git && cd PercolatorElasticSearch
```

Install project dependencies

```
pip install -r requirements.txt
```

Finally, most important step is to start `elasticsearch`

-	on macOS (If you used `brew` to install)

```
elasticsearch
```

-	on Ubuntu

```
sudo systemctl start elasticsearch
```

-	To check `elasticsearch` is working fine, `curl localhost:9200`. Expected result like this:

```
{
  "name" : "CWs7tki",
  "cluster_name" : "elasticsearch",
  "cluster_uuid" : "-UDHbLFBQS-JdatHqtfRHw",
  "version" : {
    "number" : "6.2.2",
    "build_hash" : "10b1edd",
    "build_date" : "2018-02-16T19:01:30.685723Z",
    "build_snapshot" : false,
    "lucene_version" : "7.2.1",
    "minimum_wire_compatibility_version" : "5.6.0",
    "minimum_index_compatibility_version" : "5.0.0"
  },
  "tagline" : "You Know, for Search"
}
```

Great! We're ready to go!

Usage
-----

-	Please make sure, `elasticsearch` is working fine and you're at `PercolatorElasticSearch` directory.
-	First, you need to add mapping and create all queries.

	-	`titles.json` file should be located at `PercolatorElasticSearch` directory and json schema should be like this:

		```
		{
		    "responseHeader":{
		        "status":0,
		        "QTime":95,
		        "params":{
		        "q":"*:*",
		        "indent":"on",
		        "fl":"CourseId, UnitId, title, CourseName, id, FieldId, field",
		        "rows":"170109",
		        "wt":"json"}},
		    "response":{"numFound":170109,"start":0,"docs":[
		        {
		         "CourseId":...,
		         "UnitId":...,
		         "title":"...",
		         "id":"...",
		         "CourseName":"...",
		         "FieldId":...,
		         "field":"..."},
		         {
		         "CourseId":...,
		         "UnitId":...,
		         "title":"...",
		         "id":"...",
		         "CourseName":"...",
		         "FieldId":...,
		         "field":"..."},
		         ...
		         ]
		}}
		```

	-	Just run `python create_index.py` and sit back. This process depends on your setup(approximately ~10 min). To check process is working fine,`$ curl -X GET "localhost:9200/_cat/indices?v"` and you should see `doc.count` is counting.

-	After adding all indexes, run the main application with `flask`:

	-	run `flask`

	```
	FLASK_APP=search_link_by_id.py flask run
	```

	-	Go to `http://localhost:5000/`
	-	Paste your document
	-	See the magic!

To-do list
==========

-	[ ] Pick longest hit if results are nested e.g. if dünya, dünya mirası sözleşmesi are being bit by Percolator, choose "dünya mirası sözleşmesi"
-	[ ] Prompt all choices if there are many e.g. "kamu" word in titles are to be found 5-6 times. There should be a menu for all results.
