#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import random
import re
import string

from sanic import Sanic, response
from sanic.response import json, redirect
from sanic_redis import SanicRedis
from sanic_jinja2 import SanicJinja2

KEY_LEN = 8
COOKIE_AUTH = 'pub-list-auth'
HASH_REGEXP = re.compile(r"[^\w]", re.IGNORECASE)


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


def cleanup_hash_param(hash: str):
    return HASH_REGEXP.sub('', str(hash))


async def keygen(n, redis, template=lambda x: cleanup_hash_param(x)):
    while True:
        key = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(n))
        if not await redis.exists(template(key)):
            break
    return key


def redis_user_auth(hash: str):
    return 'user:%s' % cleanup_hash_param(hash)


def redis_task_list(hash: str):
    return 'task_list:%s' % cleanup_hash_param(hash)


def redis_task_item(task_id):
    return 'task_item:%s' % cleanup_hash_param(task_id)


def return_to_create():
    log.info('return to create page')
    url = app.url_for('create')
    return redirect(url)


@app.middleware('request')
async def user_auth(request):
    auth_uid = request.cookies.get(COOKIE_AUTH, '')
    log.info('auth user %s', auth_uid)
    with await request.app.redis as redis:
        user_id = await redis.get(redis_user_auth(auth_uid), encoding='utf-8')
        if user_id:
            log.info('user already auth %s', user_id)
        else:
            log.info('create user')
            auth_uid = await keygen(KEY_LEN, redis, redis_user_auth)
            user_id = await redis.incr('next_user_id')
            await redis.set(redis_user_auth(auth_uid), user_id)
            log.info('new user %s %s', user_id, auth_uid)

        request.app.auth_uid = auth_uid
        request.app.user_id = user_id


@app.middleware('response')
async def user_auth_cookie(request, response):
    response.cookies[COOKIE_AUTH] = request.app.auth_uid


@app.get("/")
async def create(request):
    log.info('create list')
    with await request.app.redis as redis:
        task_id = await redis.incr('next_task_id')
        await redis.hmset_dict(redis_task_item(task_id), {'title': '', 'checked': 1})
        list_uid = await keygen(KEY_LEN, redis, redis_task_list)
        await redis.rpush(redis_task_list(list_uid), task_id)
        log.info('new list and task create %s %s', list_uid, task_id)

        url = app.url_for('edit', list_uid=list_uid)
        return redirect(url)


@app.get("/list/<list_uid>/edit")
async def edit(request, list_uid):
    log.info('edit list %s', list_uid)
    with await request.app.redis as redis:
        task_len = await redis.llen(redis_task_list(list_uid))
        log.info('task list %s', task_len)
        if not task_len:
            return return_to_create()
        else:
            return jinja.render('edit.html', request, task_uid=list_uid)


@app.get("/list/<list_uid>/read")
async def read(request, list_uid):
    log.info('read list %s', list_uid)


@app.get("/list/<list_uid>/task")
async def task_list(request, list_uid):
    log.info('task data %s', list_uid)
    with await request.app.redis as redis:
        task_list = await redis.lrange(redis_task_list(list_uid), 0, -1, encoding='utf-8')
        log.info('task list %s', task_list)
        if not task_list:
            return return_to_create()

        task_data = {
            'uid': list_uid,
            'tasks': [dict(id=task_id, **await redis.hgetall(redis_task_item(task_id), encoding='utf-8')) for task_id in
                      task_list]
        }
        return response.json(task_data)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8021, debug=False, workers=1, access_log=False)

