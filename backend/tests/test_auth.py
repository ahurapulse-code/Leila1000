from app.auth import hash_password, normalize_email, verify_password


def test_password_hash_is_not_reversible_and_verifies():
    encoded = hash_password("long-secure-password")
    assert encoded != "long-secure-password"
    assert verify_password("long-secure-password", encoded)
    assert not verify_password("wrong-password", encoded)


def test_email_normalization():
    assert normalize_email("  Owner@Example.COM ") == "owner@example.com"
