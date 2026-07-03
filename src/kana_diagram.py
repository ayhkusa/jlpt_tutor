import json
import os
import webbrowser
from pathlib import Path

import matplotlib

if os.environ.get("DISPLAY", "") == "":
    matplotlib.use("Agg")

from matplotlib import font_manager as fm

from dataset import relationships
from pronounciationguide import pronunciation_guide


def get_japanese_font():
    candidates = [
        "Noto Sans CJK JP",
        "Yu Gothic",
        "Meiryo",
        "MS Gothic",
        "Arial Unicode MS",
        "Hiragino Sans",
        "TakaoPGothic",
        "DejaVu Sans",
    ]
    available_fonts = {font.name for font in fm.fontManager.ttflist}
    for candidate in candidates:
        if candidate in available_fonts:
            return candidate
    return "DejaVu Sans"


JP_FONT = get_japanese_font()
matplotlib.rcParams["font.family"] = [JP_FONT, "sans-serif"]
matplotlib.rcParams["axes.unicode_minus"] = False

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

relationship_payload = [
    {"source": start, "target": end, "label": meaning}
    for start, end, meaning in relationships
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
      font-family: '{JP_FONT}', 'Noto Sans CJK JP', 'Yu Gothic', 'Meiryo', sans-serif;
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
    .auto-pronounce-button.stop-state {{
      background: #dc2626;
      border-color: #b91c1c;
      color: #ffffff;
    }}
    .auto-pronounce-button.stop-state:hover {{
      background: #b91c1c;
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
  </style>
</head>
<body>
  <div class="page-header">
    <h1>Katakana Vocabulary Tutor</h1>
    <p>Select a character to learn 10 words using it.</p>
  </div>
  <div class=\"controls\">
    <div class=\"control-panel\">
      <div class=\"control-inputs\">
        <div class="gojuon-wrap">
          <table id="gojuonTable" class="gojuon-table" aria-label="Katakana gojuon table"></table>
        </div>
      </div>
      <div class=\"letter-help\">
        <strong>Pronunciation Quick Guide</strong>
        <div id="helpLine" class="help-line"></div>
        <div id="helpExample" class="help-example"></div>
      </div>
      <button id="autoPronounceButton" class="auto-pronounce-button" type="button">Start</button>
    </div>
  </div>

  <div id="mynetwork"></div>
  <script>
    const relationships = {json.dumps(relationship_payload)};
    const letterMap = {json.dumps(letter_map)};
    const colorMap = {json.dumps(color_map)};
    const container = document.getElementById('mynetwork');
    const gojuonTable = document.getElementById('gojuonTable');
    const autoPronounceButton = document.getElementById('autoPronounceButton');
    const helpLine = document.getElementById('helpLine');
    const helpExample = document.getElementById('helpExample');
    const nodes = new vis.DataSet();
    const edges = new vis.DataSet();
    const pronunciationGuide = {json.dumps(pronunciation_guide)};
    const synth = window.speechSynthesis;
    let preferredJapaneseVoice = null;
    let speechPrewarmed = false;
    let activeKana = 'ア';
    let autoPronounceRunning = false;
    let autoPronounceTimerId = null;
    let autoPronounceToken = 0;
    let autoPronounceIndex = 0;
    let highlightedNodeId = null;
    let highlightedNodeColor = null;
    let speechToken = 0;
    const centerX = 500;
    const centerY = 300;
    const gojuonRows = [
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
      autoPronounceIndex = 0;
      updatePronunciationHelp(roman);
      buildGraph(kana, roman);
      document.querySelectorAll('.gojuon-cell.active').forEach((btn) => btn.classList.remove('active'));
      if (buttonElement) {{
        buttonElement.classList.add('active');
      }}
      if (shouldSpeak) {{
        speakText(kana);
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
      const fragment = document.createDocumentFragment();
      gojuonRows.forEach((row) => {{
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

      const defaultButton = gojuonTable.querySelector('.gojuon-cell[data-kana="ア"]');
      if (defaultButton) {{
        setSelection('ア', 'a', defaultButton);
      }}
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
      const info = pronunciationGuide[selectedRoman];
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
        nodes.update({{ id: highlightedNodeId, color: highlightedNodeColor }});
      }}
      highlightedNodeId = null;
      highlightedNodeColor = null;
    }}

    function highlightNodeForPronunciation(nodeId) {{
      clearPronunciationHighlight();
      const node = nodes.get(nodeId);
      if (!node) {{
        return;
      }}
      highlightedNodeId = nodeId;
      highlightedNodeColor = cloneColor(node.color);
      nodes.update({{
        id: nodeId,
        color: {{
          background: '#bbf7d0',
          border: '#16a34a',
          highlight: {{ background: '#86efac', border: '#15803d' }}
        }}
      }});
    }}

    function getClockwiseTargets() {{
      const allNodes = nodes.get();
      const outerNodes = allNodes.filter((node) => node.id !== activeKana && Number.isFinite(node.x) && Number.isFinite(node.y));
      const withAngles = outerNodes.map((node) => {{
        const theta = Math.atan2(node.y - centerY, node.x - centerX);
        const clockwiseFromTop = (Math.PI / 2 - theta + 2 * Math.PI) % (2 * Math.PI);
        return {{ id: node.id, angle: clockwiseFromTop }};
      }});
      withAngles.sort((a, b) => a.angle - b.angle);
      return withAngles.map((item) => item.id);
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
      if (synth) {{
        synth.cancel();
      }}
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

      const word = clockwiseTargets[autoPronounceIndex % clockwiseTargets.length];
      autoPronounceIndex = (autoPronounceIndex + 1) % clockwiseTargets.length;
      speakText(word, 'ja-JP', () => {{
        if (!autoPronounceRunning || token !== autoPronounceToken) {{
          return;
        }}
        autoPronounceTimerId = setTimeout(() => runAutoPronounceStep(token), 1000);
      }});
    }}

    function startAutoPronounce() {{
      if (autoPronounceRunning) {{
        return;
      }}
      autoPronounceRunning = true;
      autoPronounceIndex = 0;
      autoPronounceToken += 1;
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

    function speakText(text, lang = 'ja-JP', onComplete = null) {{
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
      highlightNodeForPronunciation(text);
      synth.cancel();
      synth.speak(utterance);
    }}

    function buildGraph(selectedKana, selectedRoman) {{
      const childRelations = relationships.filter((rel) => rel.source === selectedKana);
      const childTargets = childRelations.map((rel) => rel.target);
      const nodeList = [];
      const edgeList = [];
      const selectedletter = getletterFromRoman(selectedRoman);
      const centerColor = colorMap[letterMap[selectedletter]] || '#dbeafe';

      const centerLabel = `${{selectedKana}}\n(${{selectedRoman.toLowerCase()}})`;

      nodeList.push({{
        id: selectedKana,
        label: centerLabel,
        title: centerLabel,
        x: centerX,
        y: centerY,
        shape: 'box',
        margin: {{ top: 10, right: 14, bottom: 10, left: 14 }},
        widthConstraint: {{ minimum: 120 }},
        fixed: {{ x: true, y: true }},
        color: {{
          background: centerColor,
          border: '#111827',
          highlight: {{ background: '#fde68a', border: '#92400e' }}
        }},
        font: {{ size: 20, face: '{JP_FONT}', color: '#111827', align: 'center', vadjust: 0, multi: false }},
        labelHighlightBold: false
      }});

      const childCount = childTargets.length || 1;
      const radius = 220;
      const order = [...Array(childTargets.length).keys()].sort(() => Math.random() - 0.5);
      childTargets.forEach((target, index) => {{
        const shuffledIndex = order[index];
        const angle = ((shuffledIndex / childCount) * 2 * Math.PI) - (Math.PI / 2);
        const x = centerX + Math.cos(angle) * radius;
        const y = centerY + Math.sin(angle) * radius;
        nodeList.push({{
          id: target,
          label: target,
          title: target,
          x,
          y,
          shape: 'box',
          size: 18,
          fixed: {{ x: true, y: true }},
          color: {{
            background: '#f8fafc',
            border: '#94a3b8',
            highlight: {{ background: '#fde68a', border: '#92400e' }}
          }},
          font: {{ size: 16, face: '{JP_FONT}', color: '#111827' }}
        }});
      }});

      childRelations.forEach((rel) => {{
        edgeList.push({{
          from: selectedKana,
          to: rel.target,
          label: '',
          title: `${{selectedKana}} → ${{rel.target}}: ${{rel.label}}`,
          arrows: 'to',
          font: {{ size: 12, face: '{JP_FONT}', color: '#374151', align: 'middle' }},
          color: {{ color: '#64748b', highlight: '#ef4444' }},
          smooth: {{ type: 'dynamic' }}
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
      physics: {{ enabled: false }},
      nodes: {{
        shapeProperties: {{ interpolation: false }},
        font: {{ multi: true }}
      }},
      edges: {{
        arrows: {{ to: {{ enabled: true, scaleFactor: 0.8 }} }},
        smooth: {{ type: 'dynamic' }},
        font: {{ align: 'middle' }}
      }}
    }};

    function initializeGraph() {{
      const network = new vis.Network(container, {{ nodes, edges }}, options);
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
          if (clickedNodeId && clickedNodeId !== activeKana) {{
            speakText(clickedNodeId);
          }}
        }}
      }});
      if (autoPronounceButton) {{
        autoPronounceButton.addEventListener('click', toggleAutoPronounce);
      }}
      window.addEventListener('resize', refreshLayout);
      window.addEventListener('orientationchange', refreshLayout);
      renderGojuonTable();
      updateAutoPronounceButton();
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