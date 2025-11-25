import pytest

from utils import substitute_uuid_in_string


def test_replaces_single_uuid():
    s = "prefix 123e4567-e89b-12d3-a456-426614174000 suffix"
    replaced = substitute_uuid_in_string(s, "<UUID>")
    assert "123e4567-e89b-12d3-a456-426614174000" not in replaced
    assert replaced == "prefix <UUID> suffix"


def test_replaces_multiple_uuids():
    s = (
        "one 123e4567-e89b-12d3-a456-426614174000 two "
        "abcdefAB-1234-5678-9abc-1234567890ab three"
    )
    replaced = substitute_uuid_in_string(s, "X")
    assert "123e4567-e89b-12d3-a456-426614174000" not in replaced
    assert "abcdefAB-1234-5678-9abc-1234567890ab" not in replaced
    assert replaced.count("X") == 2


def test_no_uuid_returns_same_string():
    s = "this string contains no uuid"
    replaced = substitute_uuid_in_string(s, "<UUID>")
    assert replaced == s


def test_replaces_uppercase_uuid():
    s = "UPPER ABCDEF12-3456-7890-ABCD-1234567890AB end"
    replaced = substitute_uuid_in_string(s, "U")
    assert "ABCDEF12-3456-7890-ABCD-1234567890AB" not in replaced
    assert replaced == "UPPER U end"


def test_empty_replacement_removes_uuid():
    s = "start 123e4567-e89b-12d3-a456-426614174000 end"
    replaced = substitute_uuid_in_string(s, "")
    assert "123e4567-e89b-12d3-a456-426614174000" not in replaced
    assert replaced == "start  end"


def test_partial_or_broken_uuid_not_replaced():
    # missing hyphens -> should not match
    s = "broken 123e4567e89b12d3a456426614174000 end"
    replaced = substitute_uuid_in_string(s, "Z")
    assert replaced == s
