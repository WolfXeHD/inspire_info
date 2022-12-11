import pytest
import inspire_info.myutils as myutils

@pytest.mark.parametrize("lower_date,upper_date,add_institute,expected", [
    (None, None, True, "https://inspirehep.net/api/literature?sort=mostrecent&size={size}&page={page}&q=(aff:{institute})"),
    (None, None, False, "https://inspirehep.net/api/literature?sort=mostrecent&size={size}&page={page}"),
    ("2006-01-01", None, False, "https://inspirehep.net/api/literature?sort=mostrecent&size={size}&page={page}&q=(date>2006-01-01)"),
])
def test_build_query_template(lower_date, upper_date, add_institute, expected):
    query = myutils.build_query_template(
        lower_date=lower_date,
        upper_date=upper_date,
        add_institute=add_institute
        )
    print(query)
    print(expected)
    assert query == expected

