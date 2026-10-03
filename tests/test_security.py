from app.security import canonical_hash
def test_canonical_hash():
    assert canonical_hash({"a":1,"b":2})==canonical_hash({"b":2,"a":1})
