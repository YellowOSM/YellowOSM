"""Tests for Geo58 geo-encoding"""
import pytest

from backend.lib.geo58 import Geo58


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("ND8CaShUu", (19.00, 47.10379, 15.38160)),
        ("2k86MwTm5x", (15.00, 87.07071, 175.43951)),
        ("NzpRz3GST", (19, 90.0, -180.0)),
        ("JaqxqcLEB", (19, -90.0, -180.0)),
        ("TQnu8UCej", (19, -90.0, 180.0)),
        ("3eug79ATTD", (12, 90.0, 180.0)),
        ("2yKzdW3Net", (14, -89.12346, 179.12345)),
        ("2tv2eGq6jN", (14, 89.12346, -179.12345)),
        ("2pW58yD5eC", (14, -89.12346, -179.12345)),
        ("vkwB9Kagt", (17, -47.12346, -15.12345)),
        ("LhywHZspp", (19, 47.12346, -15.12345)),
        ("2ZRm4AGLc8", (15, -47.12346, 15.12345)),
        ("3VJ2dVZHsv", (12, 47.12346, 15.12345)),
        ("3BQicuKeq6", (13, 7.12346, 1.12345)),
        ("2snAX6GEG8", (14, -17.12346, 150.12345)),
        ("2acokS56Xz", (15, 77.12346, 15.12345)),
        ("yNopJWdk7", (17, 47.12346, 15.12346)),
        ("yNopJWdk3", (17, 47.12346, 15.12344)),
        ("yNopJWdk4", (17, 47.12346, 15.12345)),
        ("fVfNrFoR4", (18, 10.12347, 0.12345)),
        ("MupR1eUBr", (19, 10.12346, 0.12345)),
    ],
)
def test_geo58_to_geocoordinates(test_input, expected):
    """Test geo58 encoding to geocoordinates"""
    g58 = Geo58(g58=test_input)
    assert g58.get_coordinates() == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ((19.00, 47.10379, 15.38160), "ND8CaShUu"),
        ((15, 87.07071, 175.43951), "2k86MwTm5x"),
        ((19, 90.0, -180.0), "NzpRz3GST"),
        ((19, -90.0, -180.0), "JaqxqcLEB"),
        ((19, -90.0, 180.0), "TQnu8UCej"),
        ((12, 90.0, 180.0), "3eug79ATTD"),
        ((14, -89.12346, 179.12345), "2yKzdW3Net"),
        ((14, 89.12346, -179.12345), "2tv2eGq6jN"),
        ((14, -89.12346, -179.12345), "2pW58yD5eC"),
        ((17, -47.12346, -15.12345), "vkwB9Kagt"),
        ((19, 47.12346, -15.12345), "LhywHZspp"),
        ((15, -47.12346, 15.12345), "2ZRm4AGLc8"),
        ((12, 47.12346, 15.12345), "3VJ2dVZHsv"),
        ((13, 7.12346, 1.12345), "3BQicuKeq6"),
        ((14, -17.12346, 150.12345), "2snAX6GEG8"),
        ((15, 77.12346, 15.12345), "2acokS56Xz"),
        ((17, 47.12346, 15.12346), "yNopJWdk7"),
        ((17, 47.12346, 15.12344), "yNopJWdk3"),
        ((17, 47.12346, 15.12345), "yNopJWdk4"),
        ((18, 10.12347, 0.12345), "fVfNrFoR4"),
        ((19, 10.12346, 0.12345), "MupR1eUBr"),
    ],
)
def test_geocoordinates_to_geo58(test_input, expected):
    """Test geocoordinates to geo58 encoding"""
    g58 = Geo58(zoom=test_input[0], x=test_input[1], y=test_input[2])
    assert g58.get_geo58() == expected
