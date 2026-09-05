from src.vocab_objects import build_household_object_html, generate_household_object_pages, sentence_to_base62_hash


def test_n4_household_page_filename_contains_level_and_topic():
    word_hash = sentence_to_base62_hash("テーブル")

    assert f"n4-household-{word_hash}.html" == "n4-household-6Zfbufm0WiVd.html"


def test_level_buttons_link_available_pages_and_message_unavailable_levels():
    page = build_household_object_html(
        {
            "word": "テーブル",
            "hiragana": "てーぶる",
            "english_word": "table",
            "sentence": "テーブルを使います。",
            "english_sentence": "I use a table.",
            "breakdown": [],
        },
        level_pages={"n4": "../n4/n4-household-6Zfbufm0WiVd.html"},
    )

    assert page.count('class="level-button') == 5
    assert 'data-url="../n4/n4-household-6Zfbufm0WiVd.html"' in page
    assert 'data-level="N5"' in page
    assert "level sentence not available yet" in page


def test_page_template_has_fluid_mobile_layout_rules():
    page = build_household_object_html(
        {
            "word": "テーブル",
            "hiragana": "てーぶる",
            "english_word": "table",
            "sentence": "テーブルを使います。",
            "english_sentence": "I use a table.",
            "breakdown": [],
        },
    )

    assert ".page-tabs, .app { width: 100%; max-width: 980px;" in page
    assert ".table-wrap { overflow-x: auto; }" in page
    assert "th:first-child, td:first-child { width: 1%; white-space: nowrap; }" in page
    assert "@media (max-width: 600px)" in page


def test_n5_generator_uses_level_in_page_filename(tmp_path):
    paths = generate_household_object_pages(tmp_path / "n5", limit=1, level="N5")

    assert paths[0].name == "n5-household-6Zfbufm0WiVd.html"


def test_page_template_underlines_the_target_word_in_its_sentence():
    page = build_household_object_html(
        {
            "word": "テーブル",
            "hiragana": "てーぶる",
            "english_word": "table",
            "sentence": "このテーブルは私のテーブルです。",
            "english_sentence": "This table is my table.",
            "breakdown": [],
        },
    )

    assert page.count('<span class="target-word">テーブル</span>') == 2
    assert ".target-word { text-decoration: underline;" in page


def test_page_template_marks_the_displayed_level_button_active():
    page = build_household_object_html(
        {
            "word": "テーブル",
            "hiragana": "てーぶる",
            "english_word": "table",
            "sentence": "テーブルを使います。",
            "english_sentence": "I use a table.",
            "breakdown": [],
        },
        level_pages={"n5": "../n5/example.html", "n4": "../n4/example.html"},
        active_level="N5",
    )

    assert 'class="level-button active" type="button" data-url="../n5/example.html">N5' in page
    assert 'class="level-button" type="button" data-url="../n4/example.html">N4' in page
    assert ".level-button.active { color: #ffffff;" in page


def test_page_template_links_to_its_level_sticky_notes_pdf():
    page = build_household_object_html(
        {
            "word": "テーブル",
            "hiragana": "てーぶる",
            "english_word": "table",
            "sentence": "テーブルを使います。",
            "english_sentence": "I use a table.",
            "breakdown": [],
        },
        active_level="N5",
    )

    assert 'href="../sticky_notes_n5.pdf" download title="Download Sticky Notes"' in page
    assert page.count('class="qr-cell') == 9