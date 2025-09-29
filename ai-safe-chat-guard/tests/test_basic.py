from src.common.text_utils import normalize

def test_normalize():
    assert normalize("Hello!!! https://x.com") == "hello _url_"
