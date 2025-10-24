import pytest
from web_scrapping import scraper_inkafarma as scraper


def test_parse_price_simple_dot():
    v, raw = scraper.parse_price('S/ 12.50')
    assert v == 12.50


def test_parse_price_comma_decimal():
    v, raw = scraper.parse_price('12,30')
    assert v == 12.30


def test_parse_price_thousands():
    v, raw = scraper.parse_price('12.345,67')
    assert v == 12345.67
