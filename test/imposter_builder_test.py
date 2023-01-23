from imposter_builder import ImposterBuilder, Protocol, Method

import requests
from hamcrest import assert_that
from brunns.matchers.response import is_response
from mbtest.matchers import had_request


def test_request_to_mock_server(mock_server):
    builder = ImposterBuilder(port=3000, protocol=Protocol.HTTP, name="MyImposter")
    builder.with_stub().with_predicate(method=Method.GET, path='/test').with_response(body='sausages',
                                                                                      status_code=205).add_stub()
    builder.with_stub().with_predicate(method=Method.POST, path='/sauages').with_response(status_code='CREATED')
    imposter = builder.create()

    with mock_server(imposter):
        # Make request to mock server - exercise code under test here
        response = requests.get(f"{imposter.url}/test")

        assert_that("We got the expected response",
                    response, is_response().with_status_code(200).and_body("sausages"))
        assert_that("The mock server recorded the request",
                    imposter, had_request().with_path("/test").and_method("GET"))
