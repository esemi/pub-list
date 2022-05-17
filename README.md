Fast [todo-list](https://publist.esemi.ru/) [![Build Status](https://travis-ci.org/esemi/pub-list.svg?branch=master)](https://travis-ci.org/esemi/pub-list)
---

Маленький туду-лист для списка подарков с возможностью забиндить подарок на себя. Юра, где макет?!

TODO
---
- [x] use poetry
- [x] backend API todos
- [x] backend API tests todos
- [x] linters + tests to CI
 
- [ ] frontend coding (only functionality from UX)
- [ ] impl backend API

- [ ] user aut by cookie+hash-salt

- [ ] use .env for settings
- [ ] deploy by github CI (up server-side config too)

- [ ] limit TTL for all storage keys

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


Links
---
- [UI/UX](https://www.figma.com/file/z1taXmL6mSvkDak4I6eXRm/todo-list?node-id=90%3A410)
