Fast [todo-list](https://publist.esemi.ru/) [![Build Status](https://travis-ci.org/esemi/pub-list.svg?branch=master)](https://travis-ci.org/esemi/pub-list)
---

Маленький туду-лист для списка подарков с возможностью забиндить подарок на себя. Юра, где макет?!

TODO
---
- [x] use poetry
- [ ] use .env for settings
- [ ] linters + tests to CI
- [ ] deploy to github CI
- [ ] docstrings
- [ ] backend changes for new UX (need check)
- [ ] limit TTL for all storage keys
- [ ] frontend coding (only functionality from UX)
- [ ] UI to freelance
- [ ] up SSL cert


### Pre-requirements
- [redis server up and running](https://redis.io/docs/getting-started/installation/)
- [python 3.9+](https://www.python.org/downloads/)

### Local setup
```shell
$ git clone git@github.com:esemi/pub-list.git
$ cd pub-list
$ python3.9 -m venv venv
$ source venv/bin/activate
$ pip install -U poetry pip setuptools
$ poetry install
```
