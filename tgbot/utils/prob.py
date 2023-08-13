from copy import deepcopy
from datetime import timedelta
from itertools import zip_longest

# менять только в случае изменения значений дня результата get_report функции
DOWS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


async def _get_raw_data_from_report(report):
    raw_data: list[dict] = []
    for field in report:
        d = {}
        title = field[0]
        duration = round(field[2].seconds / 3600, 2)
        dow = field[1]
        d[dow] = {title: duration}
        raw_data.append(d)
    return raw_data


async def _get_headers(report) -> list[str]:
    headers = []
    for field in report:
        if field[0] not in headers:
            headers.append(field[0])
    return headers


async def _create_blank_matrix(headers) -> dict[str, list[dict]]:
    # TODO поставить вместо числа длину headers
    lst_works = []
    for unzip_item in zip_longest(headers, (0 for _ in range(len(headers))), fillvalue=None):
        lst_works.append({unzip_item[0]: unzip_item[1]})
    blank_matrix = {}
    for dow in DOWS:
        blank_matrix[dow] = deepcopy(lst_works)
    return blank_matrix


async def _insert_data_into_matrix(data_from_db, blank_matrix):
    for item in data_from_db:
        # Ключ - день недели
        work_of_week = list(item.keys())[0]
        # Значения принадлежащие каждому дню
        dict_values_of_day = list(item.values())[0]
        # Ключ значения для каждого дня
        key_of_value = list(dict_values_of_day.keys())[0]
        # Значение ключа значения для каждого дня
        val_of_value = list(dict_values_of_day.values())[0]
        for dow in blank_matrix:
            if work_of_week == dow:
                for level_3 in blank_matrix[work_of_week]:
                    if key_of_value in level_3:
                        level_3[key_of_value] = val_of_value
    return blank_matrix


async def _matrix_for_excel(blank_matrix) -> list:
    list_of_work = []
    for dow in DOWS:
        tmp_list = [dow]
        for item in blank_matrix[dow]:
            val_of_value = list(item.values())[0]
            tmp_list.append(val_of_value)
        list_of_work.append(tuple(tmp_list))
    return list_of_work


async def adjust_data_main(report):
    headers = await _get_headers(report)
    blank_matrix = await _create_blank_matrix(headers)
    data_from_db = await _get_raw_data_from_report(report)
    matrix_with_data_ = await _insert_data_into_matrix(data_from_db, blank_matrix)
    data_for_excel = await _matrix_for_excel(matrix_with_data_)
    headers.insert(0, "dow")
    data_for_excel.insert(0, tuple(headers))
    return data_for_excel

# Eсли нужно добавить одинаковые данные по какому-то полю, создай список с этим полем
# и проходись по нему добавляя данные в новый список


# for dow in dows:
#     lll = []
#     for k in lst:
#         if dow in k:
#             lll.append(k[dow])
#         s += f'{dow}: {lll}, '
#         res.append({dow: lll})
#     res = {"my_json": [s]}
