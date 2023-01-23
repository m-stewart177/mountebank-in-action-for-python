from flask import abort, Flask, jsonify
import requests


app = Flask(__name__)

products_url = 'http://localhost:3000/products'
content_url = 'http://localhost:4000/content'


def add_content_to_product(product, content):
    product['copy'] = content['copy']
    product['image'] = content['image']
    return product


@app.route('/products')
def get_products_with_content():
    products_response = requests.get(products_url)
    if products_response.status_code != requests.codes.ok:
        abort(404)
    products = products_response.json()['products']

    content_response = requests.get(content_url, params={'ids': ','.join([str(product['id']) for product in products])})
    if content_response.status_code != requests.codes.ok:
        abort(400)
    content = {content['id']: content for content in content_response.json()['content']}

    return jsonify([add_content_to_product(product, content[product['id']]) for product in products])


if __name__ == "__main__":
    app.run()
