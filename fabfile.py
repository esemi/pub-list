#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
from shutil import copy, rmtree

from fabric.api import cd, env, run, local, lcd, put
from fabric.contrib.files import exists


env.user = 'publist'
env.app_env = 'default'

BUILD_FILENAME = 'build.tar.gz'
BUILD_FILES = ['requirements.txt', 'app.py']
LOCAL_APP_PATH = os.path.dirname(__file__)
LOCAL_BUILD_PATH = os.path.join(LOCAL_APP_PATH, 'build')
LOCAL_BUILD_BUNDLE = os.path.join(LOCAL_APP_PATH, BUILD_FILENAME)

REMOTE_HOME_PATH = os.path.join('/home', env.user)
APP_PATH = os.path.join(REMOTE_HOME_PATH, 'publist')
DEPLOY_PATH = os.path.join(REMOTE_HOME_PATH, 'publist-deploy')
BACKUP_PATH = os.path.join(REMOTE_HOME_PATH, 'publist-backup')
VENV_PATH = os.path.join(REMOTE_HOME_PATH, 'venv')
LOG_PATH = os.path.join(REMOTE_HOME_PATH, 'logs')


def production():
    env.hosts = ['publist.esemi.ru']


def deploy():
    # init remote host
    if not exists(APP_PATH):
        run('mkdir -p %s' % APP_PATH)
    if not exists(VENV_PATH):
        with cd(REMOTE_HOME_PATH):
            run('python3.6 -m venv %s' % VENV_PATH)
            run('%s/bin/pip install --upgrade pip' % VENV_PATH)
    if not exists(LOG_PATH):
        run('mkdir -p %s' % LOG_PATH)

    # make local build
    if os.path.exists(LOCAL_BUILD_PATH):
        rmtree(LOCAL_BUILD_PATH)
    os.mkdir(LOCAL_BUILD_PATH)
    for filename in BUILD_FILES:
        copy(os.path.join(LOCAL_APP_PATH, filename), os.path.join(LOCAL_BUILD_PATH, filename))
    with lcd(LOCAL_BUILD_PATH):
        local('find . -name \*.pyc -delete')
        local('tar -czf %s .' % LOCAL_BUILD_BUNDLE)
    rmtree(LOCAL_BUILD_PATH)

    # load build
    if exists(DEPLOY_PATH):
        run('rm -rf %s' % DEPLOY_PATH)
    run('mkdir -p %s' % DEPLOY_PATH)
    put(LOCAL_BUILD_BUNDLE, DEPLOY_PATH)

    with cd(DEPLOY_PATH):
        run('tar -xzf %s' % BUILD_FILENAME)
        run('%s/bin/pip install -r requirements.txt' % VENV_PATH)

    # deploy (move build to production)
    if exists(BACKUP_PATH):
        run('rm -rf %s' % BACKUP_PATH)
    run('mv %s %s' % (APP_PATH, BACKUP_PATH))
    run('mv %s %s' % (DEPLOY_PATH, APP_PATH))
    run('supervisorctl restart publist')
