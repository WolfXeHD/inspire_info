import pytest
import inspire_info.myutils as myutils

@pytest.mark.parametrize("lower_date,upper_date,add_institute,add_collaborations,expected", [
    (None, None, True, None, "https://inspirehep.net/api/literature?sort=mostrecent&size={size}&page={page}&q=(aff:{institute})"),
    (None, None, False, None, "https://inspirehep.net/api/literature?sort=mostrecent&size={size}&page={page}"),
    ("2006-01-01", None, False, None, "https://inspirehep.net/api/literature?sort=mostrecent&size={size}&page={page}&q=(date>2006-01-01)"),
    ("2006-01-01", "2020-01-01", False, None, "https://inspirehep.net/api/literature?sort=mostrecent&size={size}&page={page}&q=(date>2006-01-01%20and%20date<2020-01-01)"),
    ("2006-01-01", "2020-01-01", True, None, "https://inspirehep.net/api/literature?sort=mostrecent&size={size}&page={page}&q=(aff:{institute})%20and%20(date>2006-01-01%20and%20date<2020-01-01)"),
    ("2006-01-01", "2020-01-01", True, None, "https://inspirehep.net/api/literature?sort=mostrecent&size={size}&page={page}&q=(aff:{institute})%20and%20(date>2006-01-01%20and%20date<2020-01-01)"),
    (None, None, True, ["XENON"], "https://inspirehep.net/api/literature?sort=mostrecent&size={size}&page={page}&q=(aff:{institute}%20or%20(collaboration:XENON))"),
    (None, None, True, ["XENON", "LZ"], "https://inspirehep.net/api/literature?sort=mostrecent&size={size}&page={page}&q=(aff:{institute}%20or%20(collaboration:XENON%20or%20collaboration:LZ))"),
    ("2006-01-01", None, True, ["XENON", "LZ"], "https://inspirehep.net/api/literature?sort=mostrecent&size={size}&page={page}&q=(aff:{institute}%20or%20(collaboration:XENON%20or%20collaboration:LZ))%20and%20(date>2006-01-01)"),
    ("2006-01-01", "2020-01-01", True, ["XENON", "LZ"], "https://inspirehep.net/api/literature?sort=mostrecent&size={size}&page={page}&q=(aff:{institute}%20or%20(collaboration:XENON%20or%20collaboration:LZ))%20and%20(date>2006-01-01%20and%20date<2020-01-01)"),
    ("2006-01-01", "2020-01-01", False, ["XENON", "LZ"], "https://inspirehep.net/api/literature?sort=mostrecent&size={size}&page={page}&q=((collaboration:XENON%20or%20collaboration:LZ))%20and%20(date>2006-01-01%20and%20date<2020-01-01)"),
])
def test_build_query_template(lower_date, upper_date, add_institute, add_collaborations, expected):
    query = myutils.build_query_template(
        lower_date=lower_date,
        upper_date=upper_date,
        add_institute=add_institute,
        add_collaborations=add_collaborations
        )
    print("query:", query)
    print("expected:", expected)
    assert query == expected

