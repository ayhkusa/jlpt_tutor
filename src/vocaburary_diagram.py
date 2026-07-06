import json
import webbrowser
from pathlib import Path

from gana_data import relationships as gana_relationships
from gana_guide import pronunciation_guide as gana_pronunciation_guide
from kana_data import relationships as kana_relationships
from kana_guide import pronunciation_guide as kana_pronunciation_guide

# CSS font-family stack resolved by the browser; no server-side font detection needed.
JP_FONT = "Noto Sans CJK JP, Yu Gothic, Meiryo, MS Gothic, Hiragino Sans, sans-serif"
# Single font name used for vis-network's font.face option (falls back to system CJK font).
VIS_FONT = "Noto Sans CJK JP"

# ----------------------------
# NODE COLORS
# ----------------------------
color_map = {
    "ア": "#ff6b6b",
    "イ": "#4dabf7",
    "ウ": "#51cf66",
    "エ": "#ffd43b",
    "オ": "#b197fc",
}

letter_map = {
    "a": "ア",
    "e": "エ",
    "i": "イ",
    "o": "オ",
    "u": "ウ",
}

BASE_ROMAJI = {
  "あ": "a", "い": "i", "う": "u", "え": "e", "お": "o",
  "か": "ka", "き": "ki", "く": "ku", "け": "ke", "こ": "ko",
  "さ": "sa", "し": "shi", "す": "su", "せ": "se", "そ": "so",
  "た": "ta", "ち": "chi", "つ": "tsu", "て": "te", "と": "to",
  "な": "na", "に": "ni", "ぬ": "nu", "ね": "ne", "の": "no",
  "は": "ha", "ひ": "hi", "ふ": "fu", "へ": "he", "ほ": "ho",
  "ま": "ma", "み": "mi", "む": "mu", "め": "me", "も": "mo",
  "や": "ya", "ゆ": "yu", "よ": "yo",
  "ら": "ra", "り": "ri", "る": "ru", "れ": "re", "ろ": "ro",
  "わ": "wa", "を": "o", "ん": "n",
  "が": "ga", "ぎ": "gi", "ぐ": "gu", "げ": "ge", "ご": "go",
  "ざ": "za", "じ": "ji", "ず": "zu", "ぜ": "ze", "ぞ": "zo",
  "だ": "da", "ぢ": "ji", "づ": "zu", "で": "de", "ど": "do",
  "ば": "ba", "び": "bi", "ぶ": "bu", "べ": "be", "ぼ": "bo",
  "ぱ": "pa", "ぴ": "pi", "ぷ": "pu", "ぺ": "pe", "ぽ": "po",
  "ゔ": "vu",
  "ぁ": "a", "ぃ": "i", "ぅ": "u", "ぇ": "e", "ぉ": "o",
}

DIGRAPH_ROMAJI = {
  "きゃ": "kya", "きゅ": "kyu", "きょ": "kyo",
  "ぎゃ": "gya", "ぎゅ": "gyu", "ぎょ": "gyo",
  "しゃ": "sha", "しゅ": "shu", "しょ": "sho",
  "じゃ": "ja", "じゅ": "ju", "じょ": "jo",
  "ちゃ": "cha", "ちゅ": "chu", "ちょ": "cho",
  "にゃ": "nya", "にゅ": "nyu", "にょ": "nyo",
  "ひゃ": "hya", "ひゅ": "hyu", "ひょ": "hyo",
  "びゃ": "bya", "びゅ": "byu", "びょ": "byo",
  "ぴゃ": "pya", "ぴゅ": "pyu", "ぴょ": "pyo",
  "みゃ": "mya", "みゅ": "myu", "みょ": "myo",
  "りゃ": "rya", "りゅ": "ryu", "りょ": "ryo",
  "ふぁ": "fa", "ふぃ": "fi", "ふぇ": "fe", "ふぉ": "fo", "ふゅ": "fyu",
  "ゔぁ": "va", "ゔぃ": "vi", "ゔぇ": "ve", "ゔぉ": "vo", "ゔゅ": "vyu",
  "てぃ": "ti", "でぃ": "di", "とぅ": "tu", "どぅ": "du",
  "うぃ": "wi", "うぇ": "we", "うぉ": "wo",
  "しぇ": "she", "じぇ": "je", "ちぇ": "che",
}


def to_hiragana(text: str) -> str:
    chars = []
    for char in text:
        code = ord(char)
        if 0x30A1 <= code <= 0x30F6:
            chars.append(chr(code - 0x60))
        else:
            chars.append(char)
    return "".join(chars)


def last_vowel(roman: str) -> str:
    for char in reversed(roman):
        if char in "aeiou":
            return char
    return ""


def romanize_kana(text: str) -> str:
    normalized = to_hiragana(text)
    parts = []
    index = 0
    while index < len(normalized):
        char = normalized[index]

        if char == "ー":
            if parts:
                vowel = last_vowel(parts[-1])
                if vowel:
                    parts[-1] = parts[-1] + vowel
            index += 1
            continue

        if char == "っ":
            next_roman = ""
            if index + 2 <= len(normalized):
                next_pair = normalized[index + 1:index + 3]
                next_roman = DIGRAPH_ROMAJI.get(next_pair, "")
            if not next_roman and index + 1 < len(normalized):
                next_roman = BASE_ROMAJI.get(normalized[index + 1], "")
            if next_roman:
                parts.append(next_roman[0])
            index += 1
            continue

        pair = normalized[index:index + 2]
        if pair in DIGRAPH_ROMAJI:
            parts.append(DIGRAPH_ROMAJI[pair])
            index += 2
            continue

        base = BASE_ROMAJI.get(char)
        if base:
            parts.append(base)
        else:
            parts.append(char)
        index += 1

    return "".join(parts)

kana_relationship_payload = [
  {"source": start, "target": end, "label": meaning, "phonetic": romanize_kana(end)}
  for start, end, meaning in kana_relationships
]

gana_relationship_payload = [
  {"source": start, "target": end, "label": meaning, "phonetic": romanize_kana(end)}
  for start, end, meaning in gana_relationships
]

# ----------------------------
# EXPORT INTERACTIVE HTML
# ----------------------------
output_path = Path(__file__).resolve().parent.parent / "docs" / "index.html"


def open_html_in_browser(path: Path) -> None:
    resolved_path = path.resolve()

    try:
        webbrowser.open(resolved_path.as_uri())
    except Exception:
        pass


html = f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>Katakana Vocabulary Network</title>
  <script type=\"text/javascript\" src=\"https://unpkg.com/vis-network/standalone/umd/vis-network.min.js\"></script>
  <style>
    html, body {{
      height: 100%;
      width: 100%;
      overflow: hidden;
    }}
    body {{
      margin: 0;
      display: flex;
      flex-direction: column;
      font-family: {JP_FONT};
      background: #f8fafc;
      color: #111827;
    }}
      .page-header {{
        text-align: center;
      }}
    .controls {{
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 1rem 1.5rem 0.5rem;
      flex-shrink: 0;
      width: 100%;
    }}
    .control-panel {{
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 0.65rem;
      text-align: center;
    }}
    .control-inputs {{
      display: flex;
      align-items: stretch;
      justify-content: center;
      gap: 0.75rem;
      flex-wrap: wrap;
    }}
    .gojuon-wrap {{
      border: 1px solid #d1d5db;
      border-radius: 0.6rem;
      background: #ffffff;
      padding: 0.3rem;
      overflow-x: auto;
      max-width: min(620px, 94vw);
    }}
    .gojuon-table {{
      border-collapse: collapse;
      table-layout: fixed;
      width: 100%;
      min-width: 540px;
    }}
    .gojuon-table td {{
      border: 1px solid #e5e7eb;
      padding: 0;
      width: 20%;
      background: #ffffff;
    }}
    .gojuon-cell {{
      width: 100%;
      border: 0;
      background: transparent;
      padding: 0.32rem 0.2rem;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 0.06rem;
      cursor: pointer;
      color: #111827;
      min-height: 2.35rem;
    }}
    .gojuon-cell:hover {{
      background: #f8fafc;
    }}
    .gojuon-cell.active {{
      background: #dbeafe;
      outline: 2px solid #2563eb;
      outline-offset: -2px;
    }}
    .gojuon-kana {{
      font-size: 0.92rem;
      font-weight: 700;
      line-height: 1;
    }}
    .gojuon-roma {{
      font-size: 0.68rem;
      color: #4b5563;
      text-transform: lowercase;
      letter-spacing: 0.02em;
    }}
    .gojuon-empty {{
      height: 100%;
      min-height: 2.35rem;
      background: #f8fafc;
    }}
    .auto-pronounce-button {{
      min-width: 150px;
      align-self: center;
      margin-top: 0.25rem;
    }}
    .button-row {{
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      flex-wrap: nowrap;
      overflow-x: auto;
      width: min(100%, 980px);
      padding-bottom: 0.1rem;
    }}
    .button-row .auto-pronounce-button {{
      margin-top: 0;
    }}
    .pause-control {{
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 0.25rem;
      width: min(320px, 94vw);
      padding: 0.35rem 0.5rem;
      border: 1px solid #d1d5db;
      border-radius: 0.5rem;
      background: #ffffff;
      color: #1f2937;
      font-size: 0.86rem;
    }}
    .pause-control label {{
      font-weight: 600;
    }}
    .pause-control input[type="range"] {{
      width: 100%;
      accent-color: #2563eb;
    }}
    .auto-pronounce-button.stop-state {{
      background: #dc2626;
      border-color: #b91c1c;
      color: #ffffff;
    }}
    .auto-pronounce-button.stop-state:hover {{
      background: #b91c1c;
    }}
    .table-toggle-button {{
      min-width: 150px;
      align-self: center;
    }}
    button {{
      padding: 0.4rem 0.8rem;
      border: 1px solid #cbd5e1;
      border-radius: 0.4rem;
      background: #ffffff;
      cursor: pointer;
      font-size: 0.95rem;
    }}
    .letter-help {{
      padding: 0.6rem 0.8rem;
      border: 1px solid #d1d5db;
      border-radius: 0.5rem;
      background: #ffffff;
      color: #374151;
      font-size: 0.84rem;
      line-height: 1.35;
      max-width: 440px;
      width: min(440px, 100%);
      text-align: center;
    }}
    .letter-help strong {{
      color: #111827;
    }}
    .letter-help ul {{
      margin: 0.35rem 0 0;
      padding-left: 1.1rem;
    }}
    .letter-help li {{
      margin: 0.08rem 0;
    }}
    .help-line {{
      margin-top: 0.35rem;
      color: #1f2937;
    }}
    .help-example {{
      margin-top: 0.2rem;
      color: #4b5563;
    }}
    h1 {{
      margin: 0;
      padding: 0 1.5rem 0.25rem;
      font-size: 1.4rem;
      text-align: center;
    }}
    p {{
      margin: 0;
      padding: 0 1.5rem 0.75rem;
      color: #4b5563;
      text-align: center;
    }}
    #mynetwork {{
      width: 100%;
      flex: 1 1 auto;
      min-height: 320px;
      height: min(62vh, 560px);
      max-height: 70vh;
      border: 1px solid #e5e7eb;
      background: white;
      position: relative;
      overflow: hidden;
    }}
    .vis-network canvas {{
      touch-action: none;
    }}
    .dark-mode-button {{
      min-width: 120px;
      align-self: center;
    }}
    .definitions-toggle-button {{
      min-width: 150px;
      align-self: center;
    }}
    body.dark-mode {{
      background: #111827;
      color: #f9fafb;
    }}
    body.dark-mode h1 {{
      color: #f9fafb;
    }}
    body.dark-mode p {{
      color: #9ca3af;
    }}
    body.dark-mode .gojuon-wrap {{
      border-color: #374151;
      background: #1f2937;
    }}
    body.dark-mode .gojuon-table td {{
      border-color: #374151;
      background: #1f2937;
    }}
    body.dark-mode .gojuon-cell {{
      color: #f9fafb;
    }}
    body.dark-mode .gojuon-cell:hover {{
      background: #374151;
    }}
    body.dark-mode .gojuon-cell.active {{
      background: #1e3a5f;
      outline-color: #3b82f6;
    }}
    body.dark-mode .gojuon-roma {{
      color: #9ca3af;
    }}
    body.dark-mode .gojuon-empty {{
      background: #1f2937;
    }}
    body.dark-mode button {{
      background: #374151;
      border-color: #4b5563;
      color: #f9fafb;
    }}
    body.dark-mode button:hover {{
      background: #4b5563;
    }}
    body.dark-mode .auto-pronounce-button.stop-state {{
      background: #dc2626;
      border-color: #b91c1c;
      color: #ffffff;
    }}
    body.dark-mode .auto-pronounce-button.stop-state:hover {{
      background: #b91c1c;
    }}
    body.dark-mode .pause-control {{
      border-color: #374151;
      background: #1f2937;
      color: #d1d5db;
    }}
    body.dark-mode .letter-help {{
      border-color: #374151;
      background: #1f2937;
      color: #d1d5db;
    }}
    body.dark-mode .letter-help strong {{
      color: #f9fafb;
    }}
    body.dark-mode .help-line {{
      color: #e5e7eb;
    }}
    body.dark-mode .help-example {{
      color: #9ca3af;
    }}
    body.dark-mode #mynetwork {{
      border-color: #374151;
      background: #1f2937;
    }}
  </style>
</head>
<body>
  <div class="page-header">
    <h1 id="pageTitle">Hiragana Vocabulary Tutor</h1>
    <p id="pageSubtitle">Select a character to learn 10 words using it.</p>
  </div>
  <div class=\"controls\">
    <div class=\"control-panel\">
      <div class="button-row">
        <button id="vocabularyToggleButton" class="table-toggle-button" type="button">Switch to Kana</button>
        <button id="tableToggleButton" class="table-toggle-button" type="button">Hide Table</button>
        <button id="autoPronounceButton" class="auto-pronounce-button" type="button">Auto Speak</button>
        <button id="definitionsToggleButton" class="definitions-toggle-button" type="button">Definition On</button>
        <button id="darkModeButton" class="dark-mode-button" type="button">Light Mode</button>
      </div>
      <div class=\"control-inputs\">
        <div id="gojuonWrap" class="gojuon-wrap">
          <table id="gojuonTable" class="gojuon-table" aria-label="Katakana gojuon table"></table>
        </div>
      </div>
      <div class=\"letter-help\">
        <strong>Pronunciation Quick Guide</strong>
        <div id="helpLine" class="help-line"></div>
        <div id="helpExample" class="help-example"></div>
      </div>
      <div class="pause-control">
        <label for="pauseSlider">Pause Between Pronunciations: <span id="pauseValue">1.0</span>s</label>
        <input id="pauseSlider" type="range" min="0.5" max="2" step="0.5" value="1.0" />
      </div>
    </div>
  </div>

  <div id="mynetwork"></div>
  <script>
    const relationshipSets = {{
      kana: {json.dumps(kana_relationship_payload)},
      gana: {json.dumps(gana_relationship_payload)}
    }};
    const letterMap = {json.dumps(letter_map)};
    const colorMap = {json.dumps(color_map)};
    const container = document.getElementById('mynetwork');
    const gojuonWrap = document.getElementById('gojuonWrap');
    const gojuonTable = document.getElementById('gojuonTable');
    const vocabularyToggleButton = document.getElementById('vocabularyToggleButton');
    const tableToggleButton = document.getElementById('tableToggleButton');
    const autoPronounceButton = document.getElementById('autoPronounceButton');
    const definitionsToggleButton = document.getElementById('definitionsToggleButton');
    const darkModeButton = document.getElementById('darkModeButton');
    const pageTitle = document.getElementById('pageTitle');
    const pageSubtitle = document.getElementById('pageSubtitle');
    const pauseSlider = document.getElementById('pauseSlider');
    const pauseValue = document.getElementById('pauseValue');
    const helpLine = document.getElementById('helpLine');
    const helpExample = document.getElementById('helpExample');
    const nodes = new vis.DataSet();
    const edges = new vis.DataSet();
    const pronunciationGuides = {{
      kana: {json.dumps(kana_pronunciation_guide)},
      gana: {json.dumps(gana_pronunciation_guide)}
    }};
    const synth = window.speechSynthesis;
    let preferredJapaneseVoice = null;
    let speechPrewarmed = false;
    let currentVocabulary = 'gana';
    let activeKana = 'あ';
    let activeRoman = 'a';
    let autoPronounceRunning = false;
    let autoPronounceTimerId = null;
    let autoPronounceToken = 0;
    let autoPronounceIndex = 0;
    let highlightedNodeId = null;
    let highlightedNodeColor = null;
    let highlightedNodeFont = null;
    let graphNetwork = null;
    let wakeLockSentinel = null;
    let speechToken = 0;
    let tableHidden = false;
    let darkMode = true;
    let definitionsVisible = false;
    let autoPronouncePauseSeconds = 1.0;
    const centerX = 500;
    const centerY = 300;
    const kanaGojuonRows = [
      [{{ kana: 'ア', roman: 'a' }}, {{ kana: 'イ', roman: 'i' }}, {{ kana: 'ウ', roman: 'u' }}, {{ kana: 'エ', roman: 'e' }}, {{ kana: 'オ', roman: 'o' }}],
      [{{ kana: 'カ', roman: 'ka' }}, {{ kana: 'キ', roman: 'ki' }}, {{ kana: 'ク', roman: 'ku' }}, {{ kana: 'ケ', roman: 'ke' }}, {{ kana: 'コ', roman: 'ko' }}],
      [{{ kana: 'サ', roman: 'sa' }}, {{ kana: 'シ', roman: 'shi' }}, {{ kana: 'ス', roman: 'su' }}, {{ kana: 'セ', roman: 'se' }}, {{ kana: 'ソ', roman: 'so' }}],
      [{{ kana: 'タ', roman: 'ta' }}, {{ kana: 'チ', roman: 'chi' }}, {{ kana: 'ツ', roman: 'tsu' }}, {{ kana: 'テ', roman: 'te' }}, {{ kana: 'ト', roman: 'to' }}],
      [{{ kana: 'ナ', roman: 'na' }}, {{ kana: 'ニ', roman: 'ni' }}, {{ kana: 'ヌ', roman: 'nu' }}, {{ kana: 'ネ', roman: 'ne' }}, {{ kana: 'ノ', roman: 'no' }}],
      [{{ kana: 'ハ', roman: 'ha' }}, {{ kana: 'ヒ', roman: 'hi' }}, {{ kana: 'フ', roman: 'fu' }}, {{ kana: 'ヘ', roman: 'he' }}, {{ kana: 'ホ', roman: 'ho' }}],
      [{{ kana: 'マ', roman: 'ma' }}, {{ kana: 'ミ', roman: 'mi' }}, {{ kana: 'ム', roman: 'mu' }}, {{ kana: 'メ', roman: 'me' }}, {{ kana: 'モ', roman: 'mo' }}],
      [{{ kana: 'ヤ', roman: 'ya' }}, null, {{ kana: 'ユ', roman: 'yu' }}, null, {{ kana: 'ヨ', roman: 'yo' }}],
      [{{ kana: 'ラ', roman: 'ra' }}, {{ kana: 'リ', roman: 'ri' }}, {{ kana: 'ル', roman: 'ru' }}, {{ kana: 'レ', roman: 're' }}, {{ kana: 'ロ', roman: 'ro' }}],
      [{{ kana: 'ワ', roman: 'wa' }}, null, null, null, {{ kana: 'ヲ', roman: 'wo' }}],
      [{{ kana: 'ン', roman: 'n' }}, null, null, null, null],
    ];

    const ganaGojuonRows = [
      [{{ kana: 'あ', roman: 'a' }}, {{ kana: 'い', roman: 'i' }}, {{ kana: 'う', roman: 'u' }}, {{ kana: 'え', roman: 'e' }}, {{ kana: 'お', roman: 'o' }}],
      [{{ kana: 'か', roman: 'ka' }}, {{ kana: 'き', roman: 'ki' }}, {{ kana: 'く', roman: 'ku' }}, {{ kana: 'け', roman: 'ke' }}, {{ kana: 'こ', roman: 'ko' }}],
      [{{ kana: 'さ', roman: 'sa' }}, {{ kana: 'し', roman: 'shi' }}, {{ kana: 'す', roman: 'su' }}, {{ kana: 'せ', roman: 'se' }}, {{ kana: 'そ', roman: 'so' }}],
      [{{ kana: 'た', roman: 'ta' }}, {{ kana: 'ち', roman: 'chi' }}, {{ kana: 'つ', roman: 'tsu' }}, {{ kana: 'て', roman: 'te' }}, {{ kana: 'と', roman: 'to' }}],
      [{{ kana: 'な', roman: 'na' }}, {{ kana: 'に', roman: 'ni' }}, {{ kana: 'ぬ', roman: 'nu' }}, {{ kana: 'ね', roman: 'ne' }}, {{ kana: 'の', roman: 'no' }}],
      [{{ kana: 'は', roman: 'ha' }}, {{ kana: 'ひ', roman: 'hi' }}, {{ kana: 'ふ', roman: 'fu' }}, {{ kana: 'へ', roman: 'he' }}, {{ kana: 'ほ', roman: 'ho' }}],
      [{{ kana: 'ま', roman: 'ma' }}, {{ kana: 'み', roman: 'mi' }}, {{ kana: 'む', roman: 'mu' }}, {{ kana: 'め', roman: 'me' }}, {{ kana: 'も', roman: 'mo' }}],
      [{{ kana: 'や', roman: 'ya' }}, null, {{ kana: 'ゆ', roman: 'yu' }}, null, {{ kana: 'よ', roman: 'yo' }}],
      [{{ kana: 'ら', roman: 'ra' }}, {{ kana: 'り', roman: 'ri' }}, {{ kana: 'る', roman: 'ru' }}, {{ kana: 'れ', roman: 're' }}, {{ kana: 'ろ', roman: 'ro' }}],
      [{{ kana: 'わ', roman: 'wa' }}, null, null, null, {{ kana: 'を', roman: 'wo' }}],
      [{{ kana: 'ん', roman: 'n' }}, null, null, null, null],
      [{{ kana: 'が', roman: 'ga' }}, {{ kana: 'ぎ', roman: 'gi' }}, {{ kana: 'ぐ', roman: 'gu' }}, {{ kana: 'げ', roman: 'ge' }}, null],
    ];

    const vocabularyMeta = {{
      kana: {{
        label: 'Kana',
        title: 'Katakana Vocabulary Tutor',
        subtitle: 'Select a character to learn 10 words using it.',
        tableAria: 'Katakana gojuon table',
        defaultKana: 'ア',
        defaultRoman: 'a',
        rows: kanaGojuonRows
      }},
      gana: {{
        label: 'Gana',
        title: 'Hiragana Vocabulary Tutor',
        subtitle: 'Select a character to learn 10 words using it.',
        tableAria: 'Hiragana gojuon table',
        defaultKana: 'あ',
        defaultRoman: 'a',
        rows: ganaGojuonRows
      }}
    }};

    function getActiveRelationships() {{
      return relationshipSets[currentVocabulary] || [];
    }}

    function getActiveVocabularyMeta() {{
      return vocabularyMeta[currentVocabulary] || vocabularyMeta.gana;
    }}

    function getActivePronunciationGuide() {{
      return pronunciationGuides[currentVocabulary] || pronunciationGuides.gana;
    }}

    function updateVocabularyToggleButton() {{
      if (!vocabularyToggleButton) {{
        return;
      }}
      vocabularyToggleButton.textContent = currentVocabulary === 'gana' ? 'Switch to Kana' : 'Switch to Gana';
    }}

    function updateVocabularyHeading() {{
      const meta = getActiveVocabularyMeta();
      if (pageTitle) {{
        pageTitle.textContent = meta.title;
      }}
      if (pageSubtitle) {{
        pageSubtitle.textContent = meta.subtitle;
      }}
      if (gojuonTable) {{
        gojuonTable.setAttribute('aria-label', meta.tableAria);
      }}
    }}

    function getletterFromRoman(roman) {{
      if (!roman) {{
        return 'a';
      }}
      const lowered = roman.toLowerCase();
      const letter = lowered[lowered.length - 1];
      return ['a', 'i', 'u', 'e', 'o'].includes(letter) ? letter : 'a';
    }}

    function setSelection(kana, roman, buttonElement, shouldSpeak = false) {{
      activeKana = kana;
      activeRoman = roman;
      autoPronounceIndex = 0;
      updatePronunciationHelp(roman);
      buildGraph(kana, roman);
      document.querySelectorAll('.gojuon-cell.active').forEach((btn) => btn.classList.remove('active'));
      if (buttonElement) {{
        buttonElement.classList.add('active');
      }}
      if (shouldSpeak) {{
        speakText(kana, 'ja-JP', null, `center_${{kana}}`);
      }}
      if (autoPronounceRunning) {{
        autoPronounceToken += 1;
        if (autoPronounceTimerId) {{
          clearTimeout(autoPronounceTimerId);
          autoPronounceTimerId = null;
        }}
        runAutoPronounceStep(autoPronounceToken);
      }}
    }}

    function renderGojuonTable() {{
      if (!gojuonTable) {{
        return;
      }}
      const meta = getActiveVocabularyMeta();
      const activeRows = meta.rows || [];
      const fragment = document.createDocumentFragment();
      activeRows.forEach((row) => {{
        const tr = document.createElement('tr');
        row.forEach((cell) => {{
          const td = document.createElement('td');
          if (!cell) {{
            const empty = document.createElement('div');
            empty.className = 'gojuon-empty';
            td.appendChild(empty);
            tr.appendChild(td);
            return;
          }}

          const btn = document.createElement('button');
          btn.type = 'button';
          btn.className = 'gojuon-cell';
          btn.dataset.kana = cell.kana;
          btn.dataset.roman = cell.roman;
          btn.innerHTML = `<span class="gojuon-kana">${{cell.kana}}</span><span class="gojuon-roma">${{cell.roman}}</span>`;
          btn.addEventListener('click', () => setSelection(cell.kana, cell.roman, btn, true));
          td.appendChild(btn);
          tr.appendChild(td);
        }});
        fragment.appendChild(tr);
      }});
      gojuonTable.innerHTML = '';
      gojuonTable.appendChild(fragment);

      const defaultButton = gojuonTable.querySelector(`.gojuon-cell[data-kana="${{meta.defaultKana}}"]`);
      if (defaultButton) {{
        setSelection(meta.defaultKana, meta.defaultRoman, defaultButton);
      }}
    }}

    function toggleVocabulary() {{
      currentVocabulary = currentVocabulary === 'gana' ? 'kana' : 'gana';
      updateVocabularyHeading();
      updateVocabularyToggleButton();
      renderGojuonTable();
    }}

    function refreshVoices() {{
      if (!synth) {{
        return;
      }}
      const voices = synth.getVoices();
      preferredJapaneseVoice = voices.find((voice) => voice.lang && voice.lang.startsWith('ja')) || voices[0] || null;
    }}

    function prewarmSpeech() {{
      if (!synth || speechPrewarmed) {{
        return;
      }}
      refreshVoices();
      try {{
        const warmupUtterance = new SpeechSynthesisUtterance('あ');
        warmupUtterance.lang = 'ja-JP';
        warmupUtterance.volume = 0;
        if (preferredJapaneseVoice) {{
          warmupUtterance.voice = preferredJapaneseVoice;
        }}
        synth.speak(warmupUtterance);
        synth.cancel();
      }} catch (error) {{
        // Ignore warmup failures and continue with normal playback.
      }}
      speechPrewarmed = true;
    }}

    if (synth) {{
      refreshVoices();
      if ('onvoiceschanged' in synth) {{
        synth.onvoiceschanged = refreshVoices;
      }}
      window.addEventListener('pointerdown', prewarmSpeech, {{ once: true }});
      window.addEventListener('keydown', prewarmSpeech, {{ once: true }});
    }}

    function updatePronunciationHelp(selectedRoman) {{
      const activeGuide = getActivePronunciationGuide();
      const info = activeGuide[selectedRoman];
      if (!info) {{
        helpLine.textContent = '';
        helpExample.textContent = '';
        return;
      }}
      helpLine.textContent = `${{info.label}}: ${{info.sound}}`;
      helpExample.textContent = `Example: ${{info.example}}`;
    }}

    function updateAutoPronounceButton() {{
      if (!autoPronounceButton) {{
        return;
      }}
      autoPronounceButton.textContent = autoPronounceRunning ? 'Stop' : 'Auto Speak';
      autoPronounceButton.classList.toggle('stop-state', autoPronounceRunning);
    }}

    function updatePauseDisplay() {{
      if (pauseValue) {{
        pauseValue.textContent = autoPronouncePauseSeconds.toFixed(1);
      }}
    }}

    function updatePauseFromSlider() {{
      if (!pauseSlider) {{
        return;
      }}
      const parsed = Number.parseFloat(pauseSlider.value);
      autoPronouncePauseSeconds = Number.isFinite(parsed) ? parsed : 1;
      updatePauseDisplay();
    }}

    function updateTableToggleButton() {{
      if (!tableToggleButton) {{
        return;
      }}
      tableToggleButton.textContent = tableHidden ? 'Show Table' : 'Hide Table';
    }}

    function toggleTableVisibility() {{
      tableHidden = !tableHidden;
      if (gojuonWrap) {{
        gojuonWrap.style.display = tableHidden ? 'none' : 'block';
      }}
      updateTableToggleButton();
    }}

    function updateDarkModeButton() {{
      if (!darkModeButton) {{
        return;
      }}
      darkModeButton.textContent = darkMode ? 'Light Mode' : 'Dark Mode';
    }}

    function updateDefinitionsToggleButton() {{
      if (!definitionsToggleButton) {{
        return;
      }}
      definitionsToggleButton.textContent = definitionsVisible ? 'Definition Off' : 'Definition On';
    }}

    function toggleDefinitionsVisibility() {{
      definitionsVisible = !definitionsVisible;
      updateDefinitionsToggleButton();
      buildGraph(activeKana, activeRoman);
    }}

    function toggleDarkMode() {{
      darkMode = !darkMode;
      document.body.classList.toggle('dark-mode', darkMode);
      updateDarkModeButton();
      buildGraph(activeKana, activeRoman);
    }}

    function cloneColor(colorValue) {{
      if (!colorValue) {{
        return null;
      }}
      return JSON.parse(JSON.stringify(colorValue));
    }}

    function clearPronunciationHighlight() {{
      if (!highlightedNodeId) {{
        return;
      }}
      const existingNode = nodes.get(highlightedNodeId);
      if (existingNode) {{
        nodes.update({{ id: highlightedNodeId, color: highlightedNodeColor, font: highlightedNodeFont }});
      }}
      highlightedNodeId = null;
      highlightedNodeColor = null;
      highlightedNodeFont = null;
    }}

    function clearNetworkSelection() {{
      if (graphNetwork) {{
        graphNetwork.unselectAll();
      }}
    }}

    function highlightNodeForPronunciation(nodeId) {{
      clearPronunciationHighlight();
      const node = nodes.get(nodeId);
      if (!node) {{
        return;
      }}
      highlightedNodeId = nodeId;
      highlightedNodeColor = cloneColor(node.color);
      highlightedNodeFont = cloneColor(node.font);
      nodes.update({{
        id: nodeId,
        color: {{
          background: '#1e3a8a',
          border: '#1e40af',
          highlight: {{ background: '#1d4ed8', border: '#1e3a8a' }}
        }},
        font: {{ ...node.font, color: '#ffffff' }}
      }});
    }}

    function getClockwiseTargets() {{
      const allNodes = nodes.get();
      const outerNodes = allNodes.filter((node) => node.nodeType === 'word' && Number.isFinite(node.x) && Number.isFinite(node.y));
      const withAngles = outerNodes.map((node) => {{
        const theta = Math.atan2(node.y - centerY, node.x - centerX);
        const clockwiseFromTop = (Math.PI / 2 - theta + 2 * Math.PI) % (2 * Math.PI);
        return {{ id: node.id, angle: clockwiseFromTop }};
      }});
      withAngles.sort((a, b) => a.angle - b.angle);
      return withAngles.map((item) => item.id);
    }}

    async function requestWakeLock() {{
      if (!autoPronounceRunning || wakeLockSentinel || !('wakeLock' in navigator)) {{
        return;
      }}
      try {{
        wakeLockSentinel = await navigator.wakeLock.request('screen');
        wakeLockSentinel.addEventListener('release', () => {{
          wakeLockSentinel = null;
        }});
      }} catch (error) {{
        wakeLockSentinel = null;
      }}
    }}

    async function releaseWakeLock() {{
      if (!wakeLockSentinel) {{
        return;
      }}
      try {{
        await wakeLockSentinel.release();
      }} catch (error) {{
        // Ignore release failures.
      }}
      wakeLockSentinel = null;
    }}

    function stopAutoPronounce() {{
      autoPronounceRunning = false;
      autoPronounceToken += 1;
      speechToken += 1;
      autoPronounceIndex = 0;
      if (autoPronounceTimerId) {{
        clearTimeout(autoPronounceTimerId);
        autoPronounceTimerId = null;
      }}
      clearPronunciationHighlight();
      clearNetworkSelection();
      if (synth) {{
        synth.cancel();
      }}
      releaseWakeLock();
      updateAutoPronounceButton();
    }}

    function runAutoPronounceStep(token) {{
      if (!autoPronounceRunning || token !== autoPronounceToken) {{
        return;
      }}

      const clockwiseTargets = getClockwiseTargets();
      if (!clockwiseTargets.length) {{
        stopAutoPronounce();
        return;
      }}

      const wordNodeId = clockwiseTargets[autoPronounceIndex % clockwiseTargets.length];
      autoPronounceIndex = (autoPronounceIndex + 1) % clockwiseTargets.length;
      const wordNode = nodes.get(wordNodeId);
      const wordText = wordNode && typeof wordNode.label === 'string' ? wordNode.label : wordNodeId;
      speakText(wordText, 'ja-JP', () => {{
        if (!autoPronounceRunning || token !== autoPronounceToken) {{
          return;
        }}
        autoPronounceTimerId = setTimeout(() => runAutoPronounceStep(token), autoPronouncePauseSeconds * 1000);
      }}, wordNodeId);
    }}

    function startAutoPronounce() {{
      if (autoPronounceRunning) {{
        return;
      }}
      autoPronounceRunning = true;
      autoPronounceIndex = 0;
      autoPronounceToken += 1;
      requestWakeLock();
      updateAutoPronounceButton();
      runAutoPronounceStep(autoPronounceToken);
    }}

    function toggleAutoPronounce() {{
      if (autoPronounceRunning) {{
        stopAutoPronounce();
        return;
      }}
      startAutoPronounce();
    }}

    function speakText(text, lang = 'ja-JP', onComplete = null, highlightNodeId = null) {{
      if (!('speechSynthesis' in window)) {{
        alert('Speech synthesis is not supported in this browser.');
        if (typeof onComplete === 'function') {{
          onComplete();
        }}
        return;
      }}
      prewarmSpeech();
      const utterance = new SpeechSynthesisUtterance(text);
      const currentSpeechToken = ++speechToken;
      let settled = false;
      const settleSpeech = () => {{
        if (settled || currentSpeechToken !== speechToken) {{
          return;
        }}
        settled = true;
        clearPronunciationHighlight();
        clearNetworkSelection();
        if (typeof onComplete === 'function') {{
          onComplete();
        }}
      }};
      utterance.lang = lang;
      utterance.rate = 0.9;
      utterance.pitch = 1.05;
      utterance.onend = settleSpeech;
      utterance.onerror = settleSpeech;
      if (preferredJapaneseVoice) {{
        utterance.voice = preferredJapaneseVoice;
      }}
      clearNetworkSelection();
      const targetHighlightId = highlightNodeId || text;
      highlightNodeForPronunciation(targetHighlightId);
      synth.cancel();
      synth.speak(utterance);
    }}

    function buildGraph(selectedKana, selectedRoman) {{
      const childRelations = getActiveRelationships().filter((rel) => rel.source === selectedKana);
      const childTargets = childRelations.map((rel) => rel.target);
      const nodeList = [];
      const edgeList = [];
      const centerNodeId = `center_${{selectedKana}}`;
      const wordNodeIdByTarget = new Map();
      const selectedletter = getletterFromRoman(selectedRoman);
      const centerColor = darkMode ? '#1e3a5f' : (colorMap[letterMap[selectedletter]] || '#dbeafe');
      const fontColor = darkMode ? '#f9fafb' : '#111827';
      const borderColor = darkMode ? '#60a5fa' : '#111827';
      const childBg = darkMode ? '#1f2937' : '#f8fafc';
      const childBorder = darkMode ? '#4b5563' : '#94a3b8';
      const edgeFontColor = darkMode ? '#9ca3af' : '#374151';
      const edgeColor = darkMode ? '#4b5563' : '#64748b';

      const centerLabel = `${{selectedKana}}\n(${{selectedRoman.toLowerCase()}})`;

      nodeList.push({{
        id: centerNodeId,
        label: centerLabel,
        title: centerLabel,
        nodeType: 'center',
        x: centerX,
        y: centerY,
        shape: 'box',
        margin: {{ top: 10, right: 14, bottom: 10, left: 14 }},
        widthConstraint: {{ minimum: 120 }},
        fixed: {{ x: true, y: true }},
        color: {{
          background: centerColor,
          border: borderColor,
          highlight: {{ background: '#fde68a', border: '#92400e' }}
        }},
        font: {{ size: 20, face: '{VIS_FONT}', color: fontColor, align: 'center', vadjust: 0, multi: false }},
        labelHighlightBold: false
      }});

      const childCount = childTargets.length || 1;
      const radius = 160;
      const order = [...Array(childTargets.length).keys()].sort(() => Math.random() - 0.5);
      const childPositionByTarget = new Map();
      childTargets.forEach((target, index) => {{
        const relation = childRelations.find((rel) => rel.target === target);
        const phoneticLine = relation && relation.phonetic ? `\nPhonetic: ${{relation.phonetic}}` : '';
        const shuffledIndex = order[index];
        const angle = ((shuffledIndex / childCount) * 2 * Math.PI) - (Math.PI / 2);
        const x = centerX + Math.cos(angle) * radius;
        const y = centerY + Math.sin(angle) * radius;
        const wordNodeId = `word_${{selectedKana}}_${{target}}`;
        wordNodeIdByTarget.set(target, wordNodeId);
        childPositionByTarget.set(target, {{ x, y }});
        nodeList.push({{
          id: wordNodeId,
          label: target,
          title: `${{target}}${{phoneticLine}}`,
          nodeType: 'word',
          x,
          y,
          fixed: {{ x: true, y: true }},
          shape: 'box',
          size: 18,
          color: {{
            background: childBg,
            border: childBorder,
            highlight: {{ background: '#fde68a', border: '#92400e' }}
          }},
          font: {{ size: 16, face: '{VIS_FONT}', color: fontColor }}
        }});
      }});

      childRelations.forEach((rel, relIndex) => {{
        if (!definitionsVisible) {{
          const targetNodeId = wordNodeIdByTarget.get(rel.target);
          if (!targetNodeId) {{
            return;
          }}
          edgeList.push({{
            from: centerNodeId,
            to: targetNodeId,
            label: '',
            title: `${{selectedKana}} → ${{rel.target}}: ${{rel.label}}`,
            font: {{ size: 12, face: '{VIS_FONT}', color: edgeFontColor, align: 'middle' }},
            color: {{ color: edgeColor, highlight: '#ef4444' }}
          }});
          return;
        }}

        const targetPosition = childPositionByTarget.get(rel.target);
        const targetNodeId = wordNodeIdByTarget.get(rel.target);
        if (!targetPosition || !targetNodeId) {{
          return;
        }}
        const dx = targetPosition.x - centerX;
        const dy = targetPosition.y - centerY;
        const length = Math.hypot(dx, dy) || 1;
        const radialX = dx / length;
        const radialY = dy / length;
        const tangentX = -radialY;
        const tangentY = radialX;
        const sideOffset = relIndex % 2 === 0 ? 10 : -10;
        const estimatedWordHalfSize = 26;
        const estimatedDefinitionHalfWidth = Math.max(54, rel.label.length * 4.2);
        const minimumSeparation = estimatedWordHalfSize + estimatedDefinitionHalfWidth + 16;
        const radialOffset = Math.max(76, minimumSeparation);
        const defX = targetPosition.x + radialX * radialOffset + tangentX * sideOffset;
        const defY = targetPosition.y + radialY * radialOffset + tangentY * sideOffset;
        const definitionNodeId = `def_${{selectedKana}}_${{relIndex}}_${{rel.target}}`;
        nodeList.push({{
          id: definitionNodeId,
          label: rel.label,
          title: rel.label,
          nodeType: 'definition',
          x: defX,
          y: defY,
          fixed: {{ x: true, y: true }},
          shape: 'box',
          margin: {{ top: 6, right: 10, bottom: 6, left: 10 }},
          color: {{
            background: darkMode ? '#0f172a' : '#eef2ff',
            border: darkMode ? '#334155' : '#6366f1',
            highlight: {{ background: darkMode ? '#1e293b' : '#dbeafe', border: darkMode ? '#475569' : '#4f46e5' }}
          }},
          font: {{ size: 16, face: '{VIS_FONT}', color: fontColor, align: 'center' }}
        }});

        edgeList.push({{
          from: centerNodeId,
          to: targetNodeId,
          label: '',
          title: `${{selectedKana}} → ${{rel.target}}: ${{rel.label}}`,
          font: {{ size: 12, face: '{VIS_FONT}', color: edgeFontColor, align: 'middle' }},
          color: {{ color: edgeColor, highlight: '#ef4444' }}
        }});
        edgeList.push({{
          from: targetNodeId,
          to: definitionNodeId,
          label: '',
          length: 40,
          title: `${{rel.target}}: ${{rel.label}}`,
          font: {{ size: 12, face: '{VIS_FONT}', color: edgeFontColor, align: 'middle' }},
          color: {{ color: edgeColor, highlight: '#ef4444' }}
        }});
      }});

      const pairToIndexes = new Map();
      edgeList.forEach((edge, index) => {{
        const key = `${{edge.from}}->${{edge.to}}`;
        if (!pairToIndexes.has(key)) {{
          pairToIndexes.set(key, []);
        }}
        pairToIndexes.get(key).push(index);
      }});

      pairToIndexes.forEach((indexes) => {{
        const count = indexes.length;
        indexes.forEach((edgeIndex, idx) => {{
          const offset = idx - (count - 1) / 2;
          const roundness = offset === 0 ? 0.08 : Math.min(0.45, 0.12 + Math.abs(offset) * 0.1);
          edgeList[edgeIndex].smooth = {{
            enabled: true,
            type: offset >= 0 ? 'curvedCW' : 'curvedCCW',
            roundness
          }};
        }});
      }});

      clearPronunciationHighlight();
      nodes.clear();
      edges.clear();
      nodes.add(nodeList);
      edges.add(edgeList);
    }}

    const options = {{
      interaction: {{ hover: true, navigationButtons: true, keyboard: true }},
      physics: {{
        enabled: true,
        solver: 'barnesHut',
        barnesHut: {{
          gravitationalConstant: -2600,
          springLength: 105,
          springConstant: 0.05,
          damping: 0.14,
          avoidOverlap: 1
        }},
        stabilization: {{ iterations: 300, fit: true }}
      }},
      nodes: {{
        shapeProperties: {{ interpolation: false }},
        font: {{ multi: true }}
      }},
      edges: {{
        length: 95,
        smooth: false,
        font: {{ align: 'middle' }}
      }}
    }};

    function initializeGraph() {{
      graphNetwork = new vis.Network(container, {{ nodes, edges }}, options);
      const network = graphNetwork;
      document.body.classList.toggle('dark-mode', darkMode);
      const recenterOnCenterNode = () => {{
        const currentScale = network.getScale();
        network.moveTo({{
          position: {{ x: centerX, y: centerY }},
          scale: currentScale,
          animation: false
        }});
      }};
      const refreshLayout = () => {{
        if (container) {{
          container.style.height = window.innerHeight < 700 ? '60vh' : '62vh';
        }}
        network.redraw();
        network.fit({{ animation: false }});
        recenterOnCenterNode();
      }};

      network.on('click', (params) => {{
        if (params.nodes.length > 0) {{
          const clickedNodeId = params.nodes[0];
          const clickedNode = nodes.get(clickedNodeId);
          if (clickedNodeId && clickedNode && clickedNode.nodeType === 'word') {{
            speakText(clickedNode.label, 'ja-JP', null, clickedNodeId);
          }}
        }}
      }});
      if (autoPronounceButton) {{
        autoPronounceButton.addEventListener('click', toggleAutoPronounce);
      }}
      if (vocabularyToggleButton) {{
        vocabularyToggleButton.addEventListener('click', toggleVocabulary);
      }}
      if (tableToggleButton) {{
        tableToggleButton.addEventListener('click', toggleTableVisibility);
      }}
      if (darkModeButton) {{
        darkModeButton.addEventListener('click', toggleDarkMode);
      }}
      if (definitionsToggleButton) {{
        definitionsToggleButton.addEventListener('click', toggleDefinitionsVisibility);
      }}
      if (pauseSlider) {{
        pauseSlider.addEventListener('input', updatePauseFromSlider);
      }}
      document.addEventListener('visibilitychange', () => {{
        if (document.visibilityState === 'visible' && autoPronounceRunning) {{
          requestWakeLock();
        }}
      }});
      window.addEventListener('beforeunload', () => releaseWakeLock());
      window.addEventListener('resize', refreshLayout);
      window.addEventListener('orientationchange', refreshLayout);
      renderGojuonTable();
      updatePauseFromSlider();
      updateVocabularyHeading();
      updateVocabularyToggleButton();
      updateTableToggleButton();
      updateAutoPronounceButton();
      updateDefinitionsToggleButton();
      updateDarkModeButton();
      recenterOnCenterNode();
      setTimeout(refreshLayout, 50);
      setTimeout(refreshLayout, 250);
    }}

    if (document.readyState === 'loading') {{
      document.addEventListener('DOMContentLoaded', initializeGraph);
    }} else {{
      initializeGraph();
    }}
  </script>
</body>
</html>
"""

output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(html, encoding="utf-8")
print(f"Interactive HTML created at: {output_path}")
open_html_in_browser(output_path)