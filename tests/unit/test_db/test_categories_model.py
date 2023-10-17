from typing import Any

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from contextlib import nullcontext as does_not_raise
from sqlalchemy.exc import IntegrityError, DBAPIError, ProgrammingError

from db.operations.categories_operations import create_category, select_categories, \
    update_category, delete_category, select_category_id, select_categories_with_actions
from db.models.category_model import CategoryModel
from tests.utils import MAIN_USER_ID, OTHER_USER_ID, NONE_USER_ID, \
    ABSENT_IN_DB_USER_ID, INVALID_USER_ID


@pytest.mark.usefixtures('add_data_to_db')
@pytest.mark.asyncio
class TestCategories:
    @pytest.mark.parametrize(
        "user_id, category_name, expectation",
        [
            (MAIN_USER_ID, 'new_cat', does_not_raise()),
            (OTHER_USER_ID, 'other_new_cat', does_not_raise()),
            (OTHER_USER_ID, 'super_long_category_name', pytest.raises(DBAPIError)),
            (MAIN_USER_ID, 'new_category', does_not_raise()),
            (MAIN_USER_ID, 'new_category', pytest.raises(IntegrityError)),
            (OTHER_USER_ID, None, pytest.raises(IntegrityError)),
            (OTHER_USER_ID, '', pytest.raises(IntegrityError)),
            (NONE_USER_ID, 'best_cat', pytest.raises(IntegrityError)),
            (ABSENT_IN_DB_USER_ID, 12345, pytest.raises(DBAPIError)),
            (INVALID_USER_ID, 'some_cat', pytest.raises(DBAPIError)),

        ]
    )
    async def test_create_category(
            self, db_session_fixture: AsyncSession, user_id: int, category_name: str,
            expectation: Any,
    ) -> None:
        with expectation:
            category_obj: CategoryModel = await create_category(
                user_id, category_name, db_session=db_session_fixture
            )
            assert isinstance(category_obj, CategoryModel)
            assert category_obj.category_name == category_name
            assert category_obj.user_id == user_id

    @pytest.mark.parametrize(
        "user_id, expectation",
        [
            (MAIN_USER_ID, does_not_raise()),
            (OTHER_USER_ID, does_not_raise()),
            (ABSENT_IN_DB_USER_ID, pytest.raises(AssertionError)),
            (INVALID_USER_ID, pytest.raises(ProgrammingError)),
            (NONE_USER_ID, pytest.raises(AssertionError)),
        ]
    )
    async def test_select_categories(
            self, db_session_fixture: AsyncSession, user_id: int, expectation: Any,
    ) -> None:
        with expectation:
            categories_fetchall = await select_categories(user_id,
                                                          db_session=db_session_fixture)
            assert categories_fetchall

    @pytest.mark.parametrize(
        "user_id, expectation",
        [
            (MAIN_USER_ID, does_not_raise()),
            (OTHER_USER_ID, does_not_raise()),
            (ABSENT_IN_DB_USER_ID, pytest.raises(AssertionError)),
            (INVALID_USER_ID, pytest.raises(ProgrammingError)),
            (NONE_USER_ID, pytest.raises(AssertionError)),
        ]
    )
    async def test_select_categories_with_actions(
            self, db_session_fixture: AsyncSession, user_id: int, expectation: Any,
    ) -> None:
        with expectation:
            categories_fetchall = await select_categories_with_actions(
                user_id, db_session=db_session_fixture
            )
            assert isinstance(categories_fetchall, list)
            assert categories_fetchall

    @pytest.mark.parametrize(
        "user_id, category_name, expectation",
        [
            (MAIN_USER_ID, 'new_cat', does_not_raise()),
            (OTHER_USER_ID, 'other_new_cat', does_not_raise()),
            (MAIN_USER_ID, None, pytest.raises(AssertionError)),
            (MAIN_USER_ID, '', pytest.raises(AssertionError)),
            (NONE_USER_ID, 'best_cat', pytest.raises(AssertionError)),
            (ABSENT_IN_DB_USER_ID, 12345, pytest.raises(DBAPIError)),
            (INVALID_USER_ID, 'some_cat', pytest.raises(DBAPIError)),

        ]
    )
    async def test_select_category_id(
            self, db_session_fixture: AsyncSession, user_id: int, category_name: str,
            expectation: Any
    ) -> None:
        with expectation:
            category_id = await select_category_id(user_id, category_name,
                                                   db_session_fixture)
            assert isinstance(category_id, int)
            assert category_id

    @pytest.mark.parametrize(
        "user_id, category_id, new_category_name, expectation",
        [
            (MAIN_USER_ID, 1, 'new_name', does_not_raise()),
            (MAIN_USER_ID, '1', 'new_name', pytest.raises(DBAPIError)),
            (OTHER_USER_ID, 1, 'other_new_cat', pytest.raises(AssertionError)),
            (OTHER_USER_ID, 2, 'new_other_cat_name', does_not_raise()),
            (MAIN_USER_ID, 1, 'user_super_best_category_name',
             pytest.raises(DBAPIError)),  # name > 20 chars
            (MAIN_USER_ID, 1, 123, pytest.raises(DBAPIError)),
            (MAIN_USER_ID, 1, '', pytest.raises(IntegrityError)),
            (MAIN_USER_ID, 1, None, pytest.raises(IntegrityError)),
            (MAIN_USER_ID, -1, 'new_name', pytest.raises(AssertionError)),
            (ABSENT_IN_DB_USER_ID, 1, 'new_name', pytest.raises(AssertionError)),
            (NONE_USER_ID, 1, 'new_name', pytest.raises(AssertionError)),
        ]
    )
    async def test_update_category(
            self, db_session_fixture: AsyncSession, user_id: int, category_id: int,
            new_category_name: str, expectation: Any,
    ) -> None:
        with expectation:
            res_id_scalar_one_or_none = await update_category(
                user_id, category_id, new_category_name, db_session_fixture
            )
            assert res_id_scalar_one_or_none == category_id

    @pytest.mark.parametrize(
        "user_id, category_id, expectation",
        [
            (MAIN_USER_ID, 1, does_not_raise()),
            (OTHER_USER_ID, 2, does_not_raise()),
            (MAIN_USER_ID, '1', pytest.raises(DBAPIError)),
            (INVALID_USER_ID, 1, pytest.raises(DBAPIError)),
            (MAIN_USER_ID, -1, pytest.raises(AssertionError)),
            (ABSENT_IN_DB_USER_ID, 1, pytest.raises(AssertionError)),
            (NONE_USER_ID, 1, pytest.raises(AssertionError)),
        ]
    )
    async def test_delete_category(
            self, db_session_fixture: AsyncSession, user_id: int, category_id: int,
            expectation: Any,
    ) -> None:
        with expectation:
            res_id_scalar_one_or_none = await delete_category(user_id, category_id,
                                                              db_session_fixture)
            print(res_id_scalar_one_or_none)
            assert res_id_scalar_one_or_none == category_id
