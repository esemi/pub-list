import unittest

from app import app, cleanup_hash_param, COOKIE_AUTH


class CleanupParamTest(unittest.TestCase):

    def test_basic(self):
        provider = [
            ('*&$*@&(::;"delete_4564654@*&*(&!(*!~-=_11', 'delete_4564654_11')
        ]
        for test, etalon in provider:
            res = cleanup_hash_param(test)
            self.assertEqual(res, etalon)


class FrontEndpointTest(unittest.TestCase):

    def test_user_auth(self):
        # anon auth
        request, response = app.test_client.get('/random_url')
        auth_token = response.cookies.get(COOKIE_AUTH).value
        self.assertEqual(response.status, 404)
        self.assertEqual(len(auth_token), 8)

        # already auth
        request, response = app.test_client.get('/random_url', cookies={COOKIE_AUTH: auth_token})
        auth_token_2 = response.cookies.get(COOKIE_AUTH).value
        self.assertEqual(response.status, 404)
        self.assertEqual(len(auth_token_2), 8)
        self.assertEqual(auth_token_2, auth_token)

    def test_create(self):
        request, response = app.test_client.get('/', allow_redirects=False)
        self.assertEqual(response.status, 302)
        return response.headers['Location']

    def test_edit(self):
        request, response = app.test_client.get('/list/INVALID/edit', allow_redirects=False)
        self.assertEqual(response.status, 302)

        valid_edit_link = self.test_create()
        request, response = app.test_client.get(valid_edit_link, allow_redirects=False)
        self.assertEqual(response.status, 200)

    def test_read(self):
        request, response = app.test_client.get('/list/INVALID/read', allow_redirects=False)
        self.assertEqual(response.status, 302)

        valid_read_link = self.test_create()[:-4] + 'read'
        request, response = app.test_client.get(valid_read_link, allow_redirects=False)
        self.assertEqual(response.status, 200)

    def test_task_insert(self):
        request, response = app.test_client.put('/list/INVALID/task/0', allow_redirects=False)
        self.assertEqual(response.status, 302)

        list_uid = self.test_create()[:-4]
        insert_link = list_uid + 'task/0'
        request, response = app.test_client.put(insert_link, allow_redirects=False, data={'title': 'unittest task title'})
        self.assertEqual(response.status, 200)
        self.assertIsInstance(response.json, dict)
        self.assertIn('task_uid', response.json)
        self.assertIsInstance(response.json['task_uid'], int)
        return list_uid, response.json['task_uid']

    def test_task_update(self):
        list_link, task_uid = self.test_task_insert()
        update_link = list_link + 'task/' + str(task_uid)
        request, response = app.test_client.put(update_link, allow_redirects=False, data={'title': 'unittest task title updated'})
        self.assertEqual(response.status, 200)
        self.assertIsInstance(response.json, dict)
        self.assertIn('task_uid', response.json)
        self.assertIsInstance(response.json['task_uid'], int)
        self.assertEqual(response.json['task_uid'], task_uid)
        return response.json['task_uid']

    def test_task_list(self):
        request, response = app.test_client.get('/list/INVALID/task', allow_redirects=False)
        self.assertEqual(response.status, 302)

        list_link, _ = self.test_task_insert()

        valid_fetch_link = list_link + 'task'
        request, response = app.test_client.get(valid_fetch_link, allow_redirects=False)
        self.assertEqual(response.status, 200)
        self.assertIsInstance(response.json, dict)
        self.assertIn('uid', response.json)
        self.assertIn('tasks', response.json)
        self.assertIsInstance(response.json['tasks'], list)
        self.assertEqual(len(response.json['tasks']), 1)
        for i in response.json['tasks']:
            self.assertIsInstance(i, dict)
            self.assertIn('id', i)
            self.assertIn('title', i)
            self.assertIn('checked', i)
            self.assertEqual(i['title'], 'unittest task title')
            self.assertEqual(i['checked'], '0')


if __name__ == '__main__':
    unittest.main()
