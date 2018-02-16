import hashlib
import logging
import random
import re
import string
import urllib.parse

from sanic import Sanic, response
from sanic.response import json
from sanic_redis import SanicRedis


KEY_LEN = 8
COOKIE_AUTH = 'pub-list-auth'


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


# todo update expire for lists


def keygen(n):
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(n))


@app.middleware('request')
async def user_auth(request):
    auth_hash = request.cookies.get(COOKIE_AUTH, '')
    log.info('auth user %s', auth_hash)
    if auth_hash or not isinstance(auth_hash, str):
        with await request.app.redis as redis:
            user_id = await redis.exists('user:%s' % auth_hash)
            if user_id:
                log.info('user already auth %s', user_id)
                request.user_id = user_id
                request.auth_hash = auth_hash
            else:
                log.info('create user')
                while True:
                    new_key = keygen(KEY_LEN)
                    if not await redis.exists('user:%s' % new_key):
                        break
                user_id = redis.incr('next_user_id')
                log.info('new user id %s', user_id)


@app.middleware('response')
async def user_auth_cookie(request, response):
    pass



@app.get("/")
async def create(request):
    log.info('create list')


    with await request.app.redis as cache:
        # fixme
        while True:
            new_key = keygen(KEY_LEN)
            if not await cache.exists(new_key):
                break

        log.info('new key gen %s', new_key)

        # create empty list
        # set cookie for owner
        # redirect to edit


@app.get("/edit/<key>")
async def edit(request, key):
    log.info('edit list %s', key)
    # check cookie auth (allow edit or not)


@app.get("/read/<key>")
async def read(request, key):
    log.info('read list %s', key)


@app.get("/toggle-state/<key>/<num:int>")
async def toggle(request, key, num: int):
    log.info('toggle state list %s', key)





if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8021, debug=False, workers=1, access_log=False)

