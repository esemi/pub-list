import hashlib
import logging
import random
import re
import string
import urllib.parse

from sanic import Sanic, response
from sanic.response import json, redirect
from sanic_redis import SanicRedis


KEY_LEN = 8
COOKIE_AUTH = 'pub-list-auth'
HASH_REGEXP = re.compile(r"[^\w]", re.IGNORECASE)

STATUS_VALID = 'valid'
STATUS_INVALID = 'invalid'
STATUS_FAIL = 'fail'
VIES_WSDL = 'http://ec.europa.eu/taxation_customs/vies/checkVatService.wsdl'
VAT_NUM_PATTERN = re.compile("^[A-Z]{2}[0-9A-Z\+\*\.]{2,12}$")
CACHE_EXPIRE = 30 * 24 * 60 * 60
CACHE_ENABLE = True
TIMEOUT = 10

logging_format = "[%(asctime)s] %(process)d-%(levelname)s "
logging_format += "%(module)s::%(funcName)s():l%(lineno)d: "
logging_format += "%(message)s"

logging.basicConfig(
    format=logging_format,
    level=logging.INFO
)
log = logging.getLogger()

app = Sanic(__name__)
app.config.update({'REDIS': {'address': ('127.0.0.1', 6379)}})
SanicRedis(app)


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

        url = app.url_for('edit', key=list_uid)
        return redirect(url)


@app.get("/list/<key>/edit")
async def edit(request, key):
    log.info('edit list %s', key)
    with await request.app.redis as redis:
        task_list = await redis.lrange(redis_task_list(key), 0, -1, encoding='utf-8')
        log.info('task list %s', task_list)
        if not task_list:
            url = app.url_for('create')
            return redirect(url)
        else:
            task_data = {
                'uid': key,
                'tasks': [dict(id=task_id, **await redis.hgetall(redis_task_item(task_id), encoding='utf-8')) for task_id in task_list]
            }
    print(task_data)
    # todo template
    return response.text('edit %s' % task_data)


@app.get("/list/<key>/read")
async def read(request, key):
    log.info('read list %s', key)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8021, debug=False, workers=1, access_log=False)

