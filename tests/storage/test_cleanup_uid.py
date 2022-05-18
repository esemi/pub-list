from typing import Optional

import pytest

from publist import storage


@pytest.mark.parametrize('test, expected', [
    (None, ''),
    ('', ''),
    ('valid_uid_123456_AZ', 'valid_uid_123456_AZ'),
    ('!@#$%RF DDljj09( ', 'RFDDljj09'),
])
def test_cleanup_uid_happy_path(test: Optional[str], expected: str):
    response = storage.cleanup_uid(test)

    assert response == expected
