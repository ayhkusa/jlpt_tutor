# JLPT Learning Data

`vocabulary/words.json` is the canonical catalog. A word has one stable `id`,
its Japanese forms, English gloss, first teaching level, and topics.

`sentences/<level>.json` contains sentences that teach a particular JLPT level.
Each sentence links its primary word with `word_id`; additional vocabulary and
grammar references can be added as `word_ids` and `grammar_ids` when those
catalogs are expanded.

`grammar/<level>.json` is reserved for grammar-point records. Existing N4
explanations remain in each sentence's `breakdown` until they are normalized.

Generated HTML, QR codes, and printable notes belong in `docs/`, not here.

Generated sentence pages use `docs/household_objects/<level>/` and filenames
such as `n4-household-6Zfbufm0WiVd.html`. The level and topic make a page URL
unique when the same word is reused by another JLPT level.