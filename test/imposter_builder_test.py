from imposter_builder import ImposterBuilder, Protocol, Method

from hamcrest import assert_that
from brunns.matchers.response import is_response
from mbtest.matchers import had_request

import requests

name = 'world'


def check_template(imposter, mock_server):
    with mock_server(imposter):
        response = requests.get(f"{imposter.url}/test")

        assert_that(response, is_response().with_status_code(200).and_body(f'Hello, {name}!'))
        assert_that(imposter, had_request(path='/test', method='GET'))


def test_request_to_mock_server(mock_server):
    builder = ImposterBuilder(port=3000, protocol=Protocol.HTTP, name="MyImposter")
    builder.with_stub().with_predicate(method=Method.GET, path='/test').with_response(body='sausages').add_stub()
    imposter = builder.create()

    with mock_server(imposter):
        # Make request to mock server - exercise code under test here
        response = requests.get(f"{imposter.url}/test")

        assert_that(response, is_response().with_status_code(200).and_body('sausages'))
        assert_that(imposter, had_request(path='/test', method='GET'))


def test_template_string(mock_server):
    imposter = ImposterBuilder(name="MyImposter").from_template("""{
      "protocol": "http",
      "port": 3000,
      "stubs": [{
        "predicates": [{
            "deepEquals": {
                "method": "GET",
                "path": "/test"
            }
        }],
        "responses": [{
          "is": {
            "statusCode": 200,
            "headers": { "Content-Type": "text/plain" },
            "body": "Hello, {{ name }}!"
          }
        }]
      }]
    }
    """, {'name': name})

    check_template(imposter, mock_server)


def test_template_file_from_default_location(mock_server):
    imposter = ImposterBuilder(name="MyImposter").from_template('templates/hello.son', {'name': name})

    check_template(imposter, mock_server)


def test_template_file_from_named_location(mock_server):
    imposter = ImposterBuilder(name="MyImposter",
                               templates="/Users/michael.stewart/PycharmProjects/mountebank-in-action-for-python/test/templates")\
        .from_template('hello.son', {'name': name})

    check_template(imposter, mock_server)


def test_template_file_from_named_location_property(mock_server):
    builder = ImposterBuilder(name="MyImposter")
    builder.templates = "/Users/michael.stewart/PycharmProjects/mountebank-in-action-for-python/test/templates"
    imposter = builder.from_template('hello.son', {'name': name})

    check_template(imposter, mock_server)


def test_stubs_from_template_string(mock_server):
    builder = ImposterBuilder(port=3000, protocol=Protocol.HTTP, name="MyImposter")
    builder.with_stub().from_template("""{
      "stubs": [{
        "predicates": [{
            "deepEquals": {
                "method": "GET",
                "path": "/test"
            }
        }],
        "responses": [{
          "is": {
            "statusCode": 200,
            "headers": { "Content-Type": "text/plain" },
            "body": "Hello, {{ name }}!"
          }
        }]
      }]
    }
    """, {'name': name})
    imposter = builder.create()

    check_template(imposter, mock_server)


def test_stubs_from_template_file_default_location(mock_server):
    builder = ImposterBuilder(port=3000, protocol=Protocol.HTTP, name="MyImposter")
    builder.with_stub().from_template('templates/hello_stubs.json', {'name': name})
    imposter = builder.create()

    check_template(imposter, mock_server)


def test_stubs_from_template_from_named_location(mock_server):
    builder = ImposterBuilder(port=3000, protocol=Protocol.HTTP, name="MyImposter",
                              templates="/Users/michael.stewart/PycharmProjects/mountebank-in-action-for-python/test/templates")
    builder.with_stub().from_template('hello_stubs.json', {'name': name})
    imposter = builder.create()

    check_template(imposter, mock_server)


def test_stubs_from_template_from_named_location_property(mock_server):
    builder = ImposterBuilder(port=3000, protocol=Protocol.HTTP, name="MyImposter")
    builder.templates = "/Users/michael.stewart/PycharmProjects/mountebank-in-action-for-python/test/templates"
    builder.with_stub().from_template('hello_stubs.json', {'name': name})
    imposter = builder.create()

    check_template(imposter, mock_server)


def test_two_stubs(mock_server):
    builder = ImposterBuilder(port=3000, protocol=Protocol.HTTP, name="MyImposter")
    builder.with_stub().with_predicate(method=Method.GET, path='/food').with_response(body='sausages').add_stub()
    builder.with_stub().from_template('templates/hello_stubs.json', {'name': name})
    imposter = builder.create()

    with mock_server(imposter):
        response = requests.get(f"{imposter.url}/test")

        assert_that(response, is_response().with_status_code(200).and_body(f'Hello, {name}!'))
        assert_that(imposter, had_request(path='/test', method='GET'))

        response = requests.get(f"{imposter.url}/food")

        assert_that(response, is_response().with_status_code(200).and_body('sausages'))
        assert_that(imposter, had_request(path='/food', method='GET'))
