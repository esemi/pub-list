import random
import unittest

from app import app, STATUS_INVALID, cleanup_hash_param


class CleanupParamTest(unittest.TestCase):
    def test_basic(self):
        provider = [
            ('*&$*@&(::;"delete_4564654@*&*(&!(*!~-=_11', 'delete_4564654_11')
        ]
        for test, etalon in provider:
            res = cleanup_hash_param(test)
            self.assertEqual(res, etalon)


class FrontEndpointTest(unittest.TestCase):

    def test_create(self):

        request, response = app.test_client.get('/')
        self.assertEqual(response.status, 200)

        data = response.json
        self.assertIsInstance(data, dict)
        self.assertIn('code', data)
        self.assertIn('number', data)
        self.assertIn('result', data)
        self.assertEqual(STATUS_INVALID, data['result'])
        self.assertEqual('IT', data['code'])

    def test_cache(self):
        vat_num = 'iT%d' % random.randint(10, 101010101010)
        request, response1 = app.test_client.get('/validate/%s' % vat_num)
        self.assertEqual(response1.status, 200)

        request, response2 = app.test_client.get('/validate/%s' % vat_num)
        self.assertEqual(response2.status, 200)

        self.assertEqual(response1.json, response2.json)

    def test_cache_regress_pool_bug(self):
        vat_num = 'iT%d' % random.randint(10, 101010101010)

        for i in range(15):
            request, response1 = app.test_client.get('/validate/%s' % vat_num)
            self.assertEqual(response1.status, 200)
            request, response2 = app.test_client.get('/validate/%s' % vat_num)
            self.assertEqual(response2.status, 200)
            self.assertEqual(response1.json, response2.json)


if __name__ == '__main__':
    unittest.main()
