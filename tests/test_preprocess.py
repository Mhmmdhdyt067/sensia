from sensia.preprocess import basic_clean, clean_text, normalize_slang


def test_basic_clean_lowercases_and_removes_noise():
    raw = "IHSG ANJLOK!!! 😭😭 cek https://t.co/x @user #IHSG"
    assert basic_clean(raw) == "ihsg anjlok cek ihsg"


def test_basic_clean_keeps_decimal_comma_and_period():
    assert basic_clean("BBCA naik 2,5% hari ini.") == "bbca naik 2,5 hari ini."


def test_basic_clean_emoji_only_returns_empty():
    assert basic_clean("😭😭🚀") == ""


def test_basic_clean_url_only_returns_empty():
    assert basic_clean("https://t.co/abc") == ""


def test_normalize_slang_replaces_whole_words_only():
    assert normalize_slang("gajian gak cair") == "gajian tidak cair"


def test_normalize_slang_multi_variant():
    assert normalize_slang("saham ini udah bgt nyangkut") == "saham ini sudah banget terjebak"


def test_clean_text_applies_both_steps():
    assert clean_text("IHSG ANJLOK bgt 😭") == "ihsg anjlok banget"
