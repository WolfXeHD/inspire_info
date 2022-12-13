import pytest
import inspire_info.myutils as myutils


@pytest.mark.parametrize("lower_date,upper_date,add_institute,add_collaborations,expected", [
    (None, None, True, None,
     "https://inspirehep.net/api/literature?sort=mostrecent&size={size}&page={page}"
     + "&q=(aff:{institute})"),
    (None, None, False, None,
     "https://inspirehep.net/api/literature?sort=mostrecent&size={size}&page={page}"),
    ("2006-01-01", None, False, None,
     "https://inspirehep.net/api/literature?sort=mostrecent&size={size}&page={page}"
     + "&q=(date>2006-01-01)"),
    ("2006-01-01", "2020-01-01", False, None,
     "https://inspirehep.net/api/literature?sort=mostrecent&size={size}&page={page}"
     + "&q=(date>2006-01-01%20and%20date<2020-01-01)"),
    ("2006-01-01", "2020-01-01", True, None,
     "https://inspirehep.net/api/literature?sort=mostrecent&size={size}&page={page}"
     + "&q=(aff:{institute})%20and%20(date>2006-01-01%20and%20date<2020-01-01)"),
    ("2006-01-01", "2020-01-01", True, None,
     "https://inspirehep.net/api/literature?sort=mostrecent&size={size}&page={page}"
     + "&q=(aff:{institute})%20and%20(date>2006-01-01%20and%20date<2020-01-01)"),
    (None, None, True, [
     "XENON"], "https://inspirehep.net/api/literature?sort=mostrecent&size={size}&page={page}"
     + "&q=(aff:{institute}%20or%20(collaboration:XENON))"),
    (None, None, True, [
     "XENON", "LZ"], "https://inspirehep.net/api/literature?sort=mostrecent&size={size}&page={page}"
     + "&q=(aff:{institute}%20or%20(collaboration:XENON%20or%20collaboration:LZ))"),
    ("2006-01-01", None, True,
     ["XENON", "LZ"], "https://inspirehep.net/api/literature?sort=mostrecent&size={size}"
     + "&page={page}&q=(aff:{institute}%20or%20(collaboration:XENON%20or%20collaboration:LZ))"
     + "%20and%20(date>2006-01-01)"),
    ("2006-01-01", "2020-01-01", True,
     ["XENON", "LZ"], "https://inspirehep.net/api/literature?sort=mostrecent&size={size}"
     + "&page={page}&q=(aff:{institute}%20or%20(collaboration:XENON%20or%20collaboration:LZ))"
     + "%20and%20(date>2006-01-01%20and%20date<2020-01-01)"),
    ("2006-01-01", "2020-01-01", False,
     ["XENON", "LZ"], "https://inspirehep.net/api/literature?sort=mostrecent&size={size}"
     + "&page={page}&q=((collaboration:XENON%20or%20collaboration:LZ))"
     + "%20and%20(date>2006-01-01%20and%20date<2020-01-01)"),
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


@pytest.mark.parametrize("lower_date,upper_date,expected", [
    ("2006-01-01", "2020-01-01", "date>2006-01-01%20and%20date<2020-01-01"),
    ("2006-01-01", None, "date>2006-01-01"),
])
def test_build_time_query(lower_date, upper_date, expected):
    query = myutils.build_time_query(lower_date, upper_date)
    print("query:", query)
    print("expected:", expected)
    assert query == expected


@pytest.mark.parametrize("person,size,search_type,expected", [
    ("TestAuthor.1", "25", "mytypo", "raises ValueError"),
    ("TestAuthor.1", "25", "author",
     "https://inspirehep.net/api/literature?sort=mostrecent&size={size}"
     + "&page={page}&q=(author:TestAuthor.1)"),
])
def test_build_person_query(person, size, search_type, expected):
    if search_type not in ["authors", "literature"]:
        pytest.raises(ValueError)

    else:
        query = myutils.build_person_query(
            person=person, size=size, search_type=search_type)
        print("query:", query)
        print("expected:", expected)
        assert query == expected


@pytest.mark.parametrize("id_list,size,expected", [
    ([12345, 23456], "500", "https://inspirehep.net/api/literature?fields=titles,authors,id"
     + "&sort=mostrecent&size=500&page=1&q=recid%3A12345%20or%20recid%3A23456"),
])
def test_get_publication_by_id(id_list, size, expected):
    query = myutils.get_publication_by_id(id_list, size)
    print("query:", query)
    print("expected:", expected)
    assert query == expected

# def test_get_data():
#     assert 1 == 2
