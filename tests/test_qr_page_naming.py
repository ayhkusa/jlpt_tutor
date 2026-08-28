from pathlib import Path


def test_n4_qr_filename_matches_level_aware_page_filename():
    filename = "n4-household-6Zfbufm0WiVd.html"

    qr_path = Path("N4") / f"{Path(filename).stem}_qr.png"

    assert qr_path == Path("N4/n4-household-6Zfbufm0WiVd_qr.png")