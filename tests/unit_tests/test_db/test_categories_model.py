import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from contextlib import nullcontext as does_not_raise
from sqlalchemy.exc import IntegrityError, DBAPIError, ProgrammingError

from db.categories.categories_commands import create_category, select_categories, update_category, delete_category, \
    select_category_id
from db.categories.categories_model import CategoriesModel
from tests.unit_tests.utils import MAIN_USER_ID


@pytest.mark.usefixtures('add_data_to_db')
@pytest.mark.asyncio
class TestCategories:
    @pytest.mark.parametrize(
        "user_id, category_name, expectation",
        [
            (MAIN_USER_ID, 'new_cat', does_not_raise()),
            (MAIN_USER_ID, 'new_category', does_not_raise()),
            (MAIN_USER_ID, 'new_category', pytest.raises(IntegrityError)),
            (MAIN_USER_ID, None, pytest.raises(IntegrityError)),
            (MAIN_USER_ID, '', pytest.raises(IntegrityError)),
            (None, 'best_cat', pytest.raises(IntegrityError)),
            (1111111112, 12345, pytest.raises(DBAPIError)),
            ('abc', 'some_cat', pytest.raises(DBAPIError)),

        ]
    )
    async def test_create_category(
            self,
            db_session: async_sessionmaker[AsyncSession],
            user_id: int,
            category_name: str,
            expectation: does_not_raise,
    ):
        with expectation:
            category_obj: CategoriesModel = await create_category(user_id, category_name, db_session=db_session)
            assert isinstance(category_obj, CategoriesModel)
            assert category_obj.category_name == category_name
            assert category_obj.user_id == user_id

    @pytest.mark.parametrize(
        "user_id, expectation",
        [
            (MAIN_USER_ID, does_not_raise()),
            (-1, pytest.raises(AssertionError)),
            ('1', pytest.raises(ProgrammingError)),
            (None, pytest.raises(AssertionError)),
        ]
    )
    async def test_select_categories(
            self, db_session: async_sessionmaker[AsyncSession], user_id: int, expectation: does_not_raise,
    ):
        with expectation:
            categories_fetchall = await select_categories(user_id, db_session=db_session)
            assert categories_fetchall

    @pytest.mark.parametrize(
        "user_id, expectation",
        [
            (MAIN_USER_ID, does_not_raise()),
            (-1, pytest.raises(AssertionError)),
            ('1', pytest.raises(ProgrammingError)),
            (None, pytest.raises(AssertionError)),
        ]
    )
    async def test_select_categories_with_actions(
            self, db_session: async_sessionmaker[AsyncSession], user_id: int, expectation: does_not_raise,
    ):
        with expectation:
            categories_fetchall = await select_categories(user_id, db_session=db_session)
            assert isinstance(categories_fetchall, list)
            assert categories_fetchall

    @pytest.mark.parametrize(
        "user_id, category_name, expectation",
        [
            (MAIN_USER_ID, 'new_cat', does_not_raise()),
            (MAIN_USER_ID, 'new_category', does_not_raise()),
            (MAIN_USER_ID, None, pytest.raises(AssertionError)),
            (MAIN_USER_ID, '', pytest.raises(AssertionError)),
            (None, 'best_cat', pytest.raises(AssertionError)),
            (1111111112, 12345, pytest.raises(DBAPIError)),
            ('abc', 'some_cat', pytest.raises(DBAPIError)),

        ]
    )
    async def test_select_category_id(
            self, db_session: async_sessionmaker[AsyncSession], user_id: int, category_name: str,
            expectation: does_not_raise
    ):
        with expectation:
            category_id = await select_category_id(user_id, category_name, db_session)
            assert isinstance(category_id, int)
            assert category_id

    @pytest.mark.parametrize(
        "user_id, category_id, new_category_name, expectation",
        [
            (MAIN_USER_ID, 1, 'new_name', does_not_raise()),
            (MAIN_USER_ID, '1', 'new_name', pytest.raises(DBAPIError)),
            (MAIN_USER_ID, 1, 'user_super_best_category_name', pytest.raises(DBAPIError)),  # name > 20 chars
            ('MAIN_USER_ID', 1, 'new_name', pytest.raises(DBAPIError)),
            (MAIN_USER_ID, 1, 123, pytest.raises(DBAPIError)),
            (MAIN_USER_ID, 1, '', pytest.raises(IntegrityError)),
            (MAIN_USER_ID, 1, None, pytest.raises(IntegrityError)),
            (MAIN_USER_ID, None, 'new_name', pytest.raises(AssertionError)),
            (MAIN_USER_ID, -1, 'new_name', pytest.raises(AssertionError)),
            (-1, 1, 'new_name', pytest.raises(AssertionError)),
            (None, 1, 'new_name', pytest.raises(AssertionError)),
        ]
    )
    async def test_update_category(
            self,
            db_session: async_sessionmaker[AsyncSession],
            user_id: int,
            category_id: int,
            new_category_name: str,
            expectation: does_not_raise,
    ):
        with expectation:
            res_id_scalar_one_or_none = await update_category(user_id, category_id, new_category_name, db_session)
            assert res_id_scalar_one_or_none == 1

    @pytest.mark.parametrize(
        "user_id, category_id, expectation",
        [
            (MAIN_USER_ID, 1, does_not_raise()),
            (MAIN_USER_ID, '1', pytest.raises(DBAPIError)),
            ('MAIN_USER_ID', 1, pytest.raises(DBAPIError)),
            (MAIN_USER_ID, None, pytest.raises(AssertionError)),
            (MAIN_USER_ID, -1, pytest.raises(AssertionError)),
            (-1, 1, pytest.raises(AssertionError)),
            (None, 1, pytest.raises(AssertionError)),
        ]
    )
    async def test_delete_category(
            self,
            db_session: async_sessionmaker[AsyncSession],
            user_id: int,
            category_id: int,
            expectation: does_not_raise,
    ):
        with expectation:
            res_id_scalar_one_or_none = await delete_category(user_id, category_id, db_session)
            assert res_id_scalar_one_or_none == 1
