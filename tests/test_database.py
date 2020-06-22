from chocula.database import IssnDatabase


def test_issn_database():

    issn_db = IssnDatabase(issn_issnl_file_path="tests/files/ISSN-to-ISSN-L.txt")

    assert issn_db.issn2issnl("1234-5678") is None
    assert issn_db.issn2issnl("0000-0000") is None

    # "The Lancet"
    assert issn_db.issn2issnl("0140-6736") == "0140-6736"
    assert issn_db.issn2issnl("1474-547X") == "0140-6736"
