#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import random
import re
import string

from sanic import Sanic, response
from sanic.response import redirect
from sanic_redis import SanicRedis
from sanic_jinja2 import SanicJinja2

KEY_LEN = 8
COOKIE_AUTH = 'pub-list-auth'
HASH_REGEXP = re.compile(r"[^\w]", re.IGNORECASE)
LIMIT_TASK_TITLE = 1000

logging_format = "[%(asctime)s] %(process)d-%(levelname)s "
logging_format += "%(module)s::%(funcName)s():l%(lineno)d: "
logging_format += "%(message)s"

logging.basicConfig(
    format=logging_format,
    level=logging.INFO
)
log = logging.getLogger()

app = Sanic(__name__)
app.config.from_object({'KEEP_ALIVE': False})
app.config.update({'REDIS': {'address': ('127.0.0.1', 6379)}})
app.static('/static', './static')
SanicRedis(app)
jinja = SanicJinja2(app)


# noinspection PyUnresolvedReferences
class Storage:
    @staticmethod
    async def keygen(n, redis, template=lambda x: cleanup_hash_param(x)):
        while True:
            key = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(n))
            if not await redis.exists(template(key)):
                break
        return key

    @classmethod
    async def user_auth(cls, user_uid: str) -> tuple:
        user_uid = cleanup_hash_param(user_uid)
        with await app.redis as redis:
            user_id = await redis.get(redis_user_auth(user_uid), encoding='utf-8')
            if user_id:
                log.info('user already auth %s', user_id)
            else:
                log.info('create user')
                user_uid = await cls.keygen(KEY_LEN, redis, redis_user_auth)
                user_id = await redis.incr('next_user_id')
                await redis.set(redis_user_auth(user_uid), user_id)
                log.info('new user %s %s', user_id, user_uid)
        return user_uid, user_id

    @staticmethod
    async def task_list_exist(list_uid: str) -> bool:
        with await app.redis as redis:
            return await redis.exists(redis_task_list_index(list_uid))

    @classmethod
    async def task_list_save_task(cls, list_uid: str, task_id: int=None, title: str='') -> int:
        with await app.redis as redis:
            if not task_id:
                task_id = await redis.incr('next_task_id')
            await redis.hmset_dict(redis_task_item(task_id), {'title': title, 'checked': 0})
            await redis.sadd(redis_task_list(list_uid), task_id)
        return task_id

    @classmethod
    async def task_list_create(cls):
        with await app.redis as redis:
            list_uid = await cls.keygen(KEY_LEN, redis, redis_task_list_index)
            await redis.hmset_dict(redis_task_list_index(list_uid), {'title': list_uid})
            log.info('new list create %s', list_uid)
        return list_uid

    @staticmethod
    async def task_list_fetch(list_uid: str) -> dict:
        with await app.redis as redis:
            tasks = await redis.smembers(redis_task_list(list_uid), encoding='utf-8')
            log.info('tasks %s', tasks)
            task_data = {'uid': list_uid,
                         'tasks': [dict(id=task_id, **await redis.hgetall(redis_task_item(task_id), encoding='utf-8'))
                                   for task_id in tasks]}
            return task_data


def cleanup_hash_param(hash: str):
    return HASH_REGEXP.sub('', str(hash))


def redis_user_auth(hash: str):
    return 'user:%s' % cleanup_hash_param(hash)


def redis_task_list(hash: str):
    return 'task_list:%s:tasks' % cleanup_hash_param(hash)


def redis_task_list_index(hash: str):
    return 'task_list:%s' % cleanup_hash_param(hash)


def redis_task_item(task_id):
    return 'task_item:%s' % cleanup_hash_param(task_id)


def return_to_create():
    log.info('return to create page')
    url = app.url_for('create')
    return redirect(url)


# todo enable only for auth requests
@app.middleware('request')
async def user_auth(request):
    auth_uid = request.cookies.get(COOKIE_AUTH, '')
    log.info('auth user %s', auth_uid)
    auth_uid, user_id = await Storage.user_auth(auth_uid)
    request.app.auth_uid = auth_uid
    request.app.user_id = user_id


@app.middleware('response')
async def user_auth_cookie(request, response):
    response.cookies[COOKIE_AUTH] = request.app.auth_uid


@app.get("/")
async def create(request):
    log.info('create list')
    list_uid = await Storage.task_list_create()
    url = app.url_for('edit', list_uid=list_uid)
    return redirect(url)


@app.get("/list/<list_uid>/edit")
async def edit(request, list_uid):
    log.info('edit list %s', list_uid)
    if not await Storage.task_list_exist(list_uid):
        return return_to_create()
    else:
        return jinja.render('edit.html', request, task_uid=list_uid)


@app.get("/list/<list_uid>/read")
async def read(request, list_uid):
    log.info('read list %s', list_uid)
    if not await Storage.task_list_exist(list_uid):
        return return_to_create()
    else:
        return jinja.render('read.html', request, task_uid=list_uid)


@app.get("/list/<list_uid>/task")
async def task_list(request, list_uid):
    log.info('fetch tasks for list %s', list_uid)
    if not await Storage.task_list_exist(list_uid):
        return return_to_create()
    task_data = await Storage.task_list_fetch(list_uid)
    return response.json(task_data)


@app.put("/list/<list_uid>/task/<task_uid:int>")
async def task_upsert(request, list_uid, task_uid: int):
    log.info('update task for list %s %s %s', task_uid, list_uid, request.form)
    if not await Storage.task_list_exist(list_uid):
        return return_to_create()
    title = request.form.get('title', '')
    task_uid = await Storage.task_list_save_task(list_uid, task_uid, title[:LIMIT_TASK_TITLE])
    log.info('upsert task %s', task_uid)
    return response.json({'task_uid': task_uid})


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8021, debug=False, workers=1, access_log=False)

