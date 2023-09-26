import pytest
from contextlib import nullcontext as does_not_raise

from tests.unit_tests.utils import MAIN_USER_ID


@pytest.mark.usefixtures('add_data_to_db')
@pytest.mark.asyncio
class TestActionsHandlers:
    USER_WITHOUT_TRACKER = 555555
    @pytest.mark.parametrize(
            "user_id, data, answer_text, expectation",
            [
                (MAIN_USER_ID, 'data', 'rgdsg', does_not_raise()),
            ]
    )
    async def test_ppppp(self, expectation):

        with expectation:
            pass


