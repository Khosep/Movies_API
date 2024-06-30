# шаблон для поиска по вложенным документам (nested type в elasticsearch)
# значения передаются nested_path: str, nested_match: dict''
NESTED_QUERY = """
            {
                "nested": {
                    "path": "%(key_path)s",
                    "query": {
                        "bool": {
                            "filter": [
                                {"term": {"%(key)s": "%(value)s"}}
                            ]
                        }
                    }
                }
            }"""

# используется если matches отсутствует
MATCH_ALL = """"must": {"match_all": {}}"""

# значения передаются параметрами matches: dict
# {поле в индексе: значение по которому ищем}
MATCH_QUERY = """{"match": {"%(key)s": "%(value)s"}}"""

# передаем (bool_operator "must"|"should"|"must_not",
# bool_base|bool_nested MATCH_ALL|MATCH_QUERY|NESTED_QUERY)
BOOL = """"%(bool_operator)s": [%(bool)s]"""

# значения передаются параметром sorts: dict
SORT = """{"%(key)s": {"order": "%(value)s"}}"""

# шаблон верхнего уровня
# значения передаются параметрами from_: int, size: int, sort: str, bool: str
# sort = "SORT, SORT..."
# bool_ = "BOOL, BOOL..."
QUERY_BASE = """{
    "from": %(from_)d,
    "size": %(page_size)d,
    "sort": [%(sort)s],
    "query": {
        "bool": {
            %(bool)s
        }
    }
}"""
