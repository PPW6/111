from flask import Flask, request, render_template
from flask_paginate import Pagination, get_page_args, get_page_parameter
from elasticsearch import Elasticsearch
from Hybrid_search import hybrid_search, extract_filters
from transformers import BertTokenizer, BertModel
app = Flask(__name__)
def handle_search(query, size,
                  min_strength=None, max_strength=None, min_conductivity=None, max_conductivity=None):
    # Extract filters from the query
    filters = extract_filters(min_strength, max_strength, min_conductivity, max_conductivity)
    if query:
        # from_ = (page - 1) * size  # 计算偏移量
        results = es.search(
            index=index_name,  # 替换为你的Elasticsearch索引名
            body={
                'query': {
                    'bool': {
                        "must":{
                            "match":
                                {'text': query}
                               },
                        **filters
                    }
                },
                'size': size,
                # 'from': from_
            }
        )
        hits = results['hits']['hits']
        total = results['hits']['total']['value']
        total_pages = (total + size - 1) // size  # 计算总页数
    else:
        hits = []
        total = 0
        total_pages = 1
    return hits, total, total_pages

@app.route('/', methods=['GET', 'POST'])
def index():
    # Load pre-trained BERT model and tokenizer
    tokenizer = BertTokenizer.from_pretrained('MatsciBERT')
    model = BertModel.from_pretrained('MatsciBERT')

    # Ensure the model is in evaluation mode
    model.eval()

    query = request.form.get('query', '')
    min_strength = request.form.get('min_strength', type=float)
    max_strength = request.form.get('max_strength', type=float)
    min_conductivity = request.form.get('min_conductivity', type=float)
    max_conductivity = request.form.get('max_conductivity', type=float)
    page = request.form.get('page', type=int, default=1)
    size = 10  # 每页显示的结果数量
    from_ = request.form.get('from_', type=int, default=0)
    # page = request.args.get(get_page_parameter(), type=int, default=1)
    hits, total, total_pages = handle_search(
        query,
        size=6000,
        min_strength=min_strength,
        max_strength=max_strength,
        min_conductivity=min_conductivity,
        max_conductivity=max_conductivity,)
    # hits, aggs, total = hybrid_search(
    # es,
    # index_name,
    # model,
    # tokenizer,
    # query,
    # min_strength = 10,
    # )
    pagination = Pagination(page=page, per_page=size, total=total, css_framework='bootstrap4')

    total_pages = (total + size - 1) // size  # 计算总页数
    offset = (page - 1) * size
    paginated_results = hits[offset:offset + size]
    return render_template(
        'index.html',
        from_= from_,
        results=paginated_results,
        query=query,
        page=page,
        size=size,
        total=total,
        total_pages=total_pages,
        min_strength=min_strength,
        max_strength=max_strength,
        min_conductivity=min_conductivity,
        max_conductivity=max_conductivity,
        # pagination=pagination,
    )

if __name__ == '__main__':
    index_name = 'documents'
    # Initialize Elasticsearch client
    es = Elasticsearch(hosts="https://localhost:9200",
                       ca_certs="D:\Program Files\elasticsearch-8.14.3-windows-x86_64/elasticsearch-8.14.3/config/certs/http_ca.crt",
                       basic_auth=("elastic", "XzwLB9kJxnEe0pr8r_eN"))
    app.run(debug=True)
