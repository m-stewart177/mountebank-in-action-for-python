import requests

from .imposters import create_content_imposter, create_product_imposter
from hamcrest import assert_that, equal_to, contains_inanyorder, has_length, is_in
from brunns.matchers.response import is_response
from mbtest.matchers import had_request

web_facade_url = 'http://127.0.0.1:5000'
products_end_point = '/products'

keys = ['id', 'name', 'description', 'copy', 'image']


def check_product(product):
    assert_that(product, has_length(len(keys)))
    assert_that(product.keys(), contains_inanyorder(*keys))


def test_product_with_content(mock_server):
    products_imposter = create_product_imposter()
    content_imposter = create_content_imposter()
    with mock_server([products_imposter, content_imposter]):
        response = requests.get(f'{web_facade_url}{products_end_point}')
        assert_that(response, is_response().with_status_code(200))
        products = response.json()
        assert_that(products, has_length(2))
        for product in products:
            check_product(product)
        assert_that(products_imposter, had_request().with_path("/products").and_method("GET"))
        assert_that(content_imposter, had_request().with_path("/content").and_method("GET"))
