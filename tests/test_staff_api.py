
from publist import webapp


def test_health():
    response = webapp.healthz()

    assert response == 'OK'

