"""Self-check for the three scrapers' parsers. Run: python test_parsers.py"""
from src.market_data import parse_jpx_index
from src.commodity_data import parse_tanaka_gold, parse_enenpi_fuel


def test_jpx_index():
    payload = {"section1": {"data": {"171": {
        "NAME_DISP": "TOPIX Core30", "ZXD": "2026/10/09", "DPP": "2,152.40", "DYWP": "-7.92",
        "DYRP": "-0.37", "DOP": "2,150.75", "DHP": "2,155.47", "DLP": "2,135.10",
    }}}}
    d = parse_jpx_index(payload, "171")
    assert (d["date"], d["close"], d["change"], d["change_pct"], d["prev_close"]) == (
        "2026-10-09", 2152.40, -7.92, -0.37, 2160.32)


def test_tanaka_gold():
    page = "<table><tr><th>金</th><td>23,311 円</td><td>+206 円</td><td>22,954 円</td><td>-12 円</td></tr></table>"
    assert parse_tanaka_gold(page) == {
        "unit": "円/g", "retail": 23311, "retail_change": 206, "buyback": 22954, "buyback_change": -12}
    assert parse_tanaka_gold("<table></table>") is None


def test_enenpi_fuel():
    page = ('<script>realtime_data = {"prices":{"date":"10\\/10","values":[168.6,157.2],'
            '"0":{"label":"レギュラー","value":"155.9"},"1":{"label":"ハイオク","value":"168.6"}},'
            '"update_time":"2026\\/10\\/11"};</script>')
    assert parse_enenpi_fuel(page) == [
        {"name": "レギュラー", "price": 155.9}, {"name": "ハイオク", "price": 168.6}]
    assert parse_enenpi_fuel("<html></html>") == []


if __name__ == "__main__":
    test_jpx_index()
    test_tanaka_gold()
    test_enenpi_fuel()
    print("OK")
