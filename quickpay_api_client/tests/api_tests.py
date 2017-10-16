import base64, json
from nose.tools import assert_equal, assert_raises
import requests
from quickpay_api_client.api import QPApi
from quickpay_api_client.exceptions import ApiError
import responses

class TestApi(object):
    def setup(self):
        self.api = QPApi(secret="foo:bar")
        self.url = "{0}{1}".format(self.api.base_url, '/test')

    def setup_request(self):
        responses.add(responses.GET, self.url,
                    json={'id': 123},
                    headers={"x-quickpay-server" : "QP-TEST"})

    @responses.activate
    def test_perform_success(self):
        self.setup_request()
        res = self.api.perform('get', "/test")
        assert_equal(res['id'], 123)

    @responses.activate
    def test_perform_failure(self):
        responses.add(responses.GET, self.url,
                               status=500,
                               json={'message': 'dummy'})

        assert_raises(ApiError, self.api.perform, 'get', '/test')

    @responses.activate
    def test_headers(self):
        self.setup_request()
        res = self.api.perform('get', '/test')

        req_headers = responses.calls[0].request.headers
        assert_equal(req_headers['Authorization'], 'Basic Zm9vOmJhcg==')
        assert_equal(req_headers['Accept-Version'], 'v10')
        assert req_headers['User-Agent']

    @responses.activate
    def test_perform_when_raw(self):
        self.setup_request()
        res = self.api.perform('get', '/test', raw=True)

        assert_equal(res[0], 200)
        assert_equal(res[1], '{"id": 123}')
        assert_equal(res[2]['x-quickpay-server'], 'QP-TEST')
        assert_equal(res[2]['content-type'], 'application/json')
