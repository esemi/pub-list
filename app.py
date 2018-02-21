#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import random
import re
import string

from sanic import Sanic, response
from sanic.response import redirect
from sanic.exceptions import abort
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
app.static('/static', './www/static')
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

    @staticmethod
    async def task_list_find(list_uid: str) -> dict:
        with await app.redis as redis:
            return await redis.hgetall(redis_task_list_index(list_uid), encoding='utf-8')

    @classmethod
    async def task_upsert(cls, list_uid: str, task_id: int=None, title: str= '') -> int:
        with await app.redis as redis:
            if not task_id:
                task_id = await redis.incr('next_task_id')
                await redis.sadd(redis_task_list(list_uid), task_id)
            await redis.hmset_dict(redis_task_item(task_id), {'title': title})
        return task_id

    @classmethod
    async def task_bind(cls, list_uid: str, task_id: int, state: bool, user_uid: str):
        with await app.redis as redis:
            await redis.hmset_dict(redis_task_item(task_id), {'title': title, 'checked': int(state), 'user_uid': user_uid})
        return task_id

    @classmethod
    async def task_list_create(cls, user_id):
        with await app.redis as redis:
            list_uid = await cls.keygen(KEY_LEN, redis, redis_task_list_index)
            await redis.hmset_dict(redis_task_list_index(list_uid), {'title': list_uid, 'owner_id': user_id})
            log.info('new list create %s', list_uid)
        return list_uid

    @staticmethod
    async def task_list_fetch(list_uid: str) -> dict:
        with await app.redis as redis:
            tasks = await redis.smembers(redis_task_list(list_uid), encoding='utf-8')
            return [dict(id=task_id, **await redis.hgetall(redis_task_item(task_id), encoding='utf-8'))
                    for task_id in tasks]


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
    list_uid = await Storage.task_list_create(request.app.user_id)
    url = app.url_for('edit', list_uid=list_uid)
    return redirect(url)


@app.get("/list/<list_uid>/edit")
async def edit(request, list_uid):
    log.info('edit list %s', list_uid)
    task_list = await Storage.task_list_find(list_uid)
    log.info('list found %s', task_list)

    if not task_list:
        return return_to_create()

    if task_list['owner_id'] != request.app.user_id:
        abort(403)

    return jinja.render('edit.html', request, task_uid=list_uid)


@app.get("/list/<list_uid>/read")
async def read(request, list_uid):
    log.info('read list %s', list_uid)
    if not await Storage.task_list_exist(list_uid):
        return return_to_create()
    else:
        return jinja.render('read.html', request, task_uid=list_uid, current_user=request.app.user_id)


@app.get("/list/<list_uid>/task")
async def task_list(request, list_uid):
    log.info('fetch tasks for list %s', list_uid)
    task_data = await Storage.task_list_fetch(list_uid)
    return response.json({'tasks': task_data})


@app.put("/list/<list_uid>/task/<task_uid:int>/upsert")
async def task_upsert(request, list_uid, task_uid: int):
    log.info('upsert task for list %s %s %s', task_uid, list_uid, request.form)
    task_list = await Storage.task_list_find(list_uid)
    log.info('list found %s', task_list)
    if not task_list:
        abort(404)
    if task_list['owner_id'] != request.app.user_id:
        abort(403)
    if task_uid and task_uid not in [int(i['id']) for i in await Storage.task_list_fetch(list_uid)]:
        log.warning('task not found')
        abort(403)

    title = request.form.get('title', '')
    task_uid = await Storage.task_upsert(list_uid, task_uid, title[:LIMIT_TASK_TITLE])
    log.info('upsert task %s', task_uid)
    return response.json({'task_uid': task_uid})


@app.put("/list/<list_uid>/task/<task_uid:int>/state")
async def task_bind_state(request, list_uid, task_uid: int):
    log.info('bind task for list %s %s %s', task_uid, list_uid, request.form)
    task_list = await Storage.task_list_find(list_uid)
    log.info('list found %s', task_list)
    if not task_list:
        abort(404)

    try:
        task = [i for i in await Storage.task_list_fetch(list_uid) if int(i['id']) == task_uid][0]
    except:
        log.warning('task not found')
        abort(403)

    print(task)

    return response.json({'state': task_uid})


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8021, debug=False, workers=1, access_log=False)

