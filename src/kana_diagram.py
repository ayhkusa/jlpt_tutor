import json
import os
import platform
import subprocess
import sys
import webbrowser
from math import cos, pi, sin
from pathlib import Path

import matplotlib

if os.environ.get("DISPLAY", "") == "":
    matplotlib.use("Agg")

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib import font_manager as fm


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
plt.rcParams["font.family"] = [JP_FONT, "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False

# ----------------------------
# DATASET
# ----------------------------
relationships = [
    ("ア", "アニメ", "Anime"),
    ("ア", "アイス", "Ice cream"),
    ("ア", "アメリカ", "America"),
    ("ア", "アパート", "Apartment"),
    ("ア", "アプリ", "App"),
    ("ア", "アクション", "Action"),
    ("ア", "アカウント", "Account"),
    ("ア", "アクセス", "Access"),
    ("ア", "アナログ", "Analog"),
    ("ア", "アンテナ", "Antenna"),

    ("イ", "イカ", "Squid"),
    ("イ", "イヌ", "Dog"),
    ("イ", "イス", "Chair"),
    ("イ", "イタリア", "Italy"),
    ("イ", "イメージ", "Image"),
    ("イ", "インストール", "Install"),
    ("イ", "イノベーション", "Innovation"),
    ("イ", "イベント", "Event"),
    ("イ", "インデックス", "Index"),
    ("イ", "インター", "Inter"),

    ("ウ", "ウマ", "Horse"),
    ("ウ", "ウミ", "Sea"),
    ("ウ", "ウェブ", "Web"),
    ("ウ", "ウイルス", "Virus"),
    ("ウ", "ウォーター", "Water"),
    ("ウ", "ウェア", "Wear"),
    ("ウ", "ウィンドウ", "Window"),
    ("ウ", "ウェーブ", "Wave"),
    ("ウ", "ウォーク", "Walk"),
    ("ウ", "ウクライナ", "Ukraine"),

    ("エ", "エネルギー", "Energy"),
    ("エ", "エアコン", "Air conditioner"),
    ("エ", "エンジン", "Engine"),
    ("エ", "エリア", "Area"),
    ("エ", "エレベーター", "Elevator"),
    ("エ", "エラー", "Error"),
    ("エ", "エッジ", "Edge"),
    ("エ", "エスカレーター", "Escalator"),
    ("エ", "エコ", "Eco"),
    ("エ", "エディション", "Edition"),

    ("オ", "オフィス", "Office"),
    ("オ", "オーケストラ", "Orchestra"),
    ("オ", "オーストラリア", "Australia"),
    ("オ", "オプション", "Option"),
    ("オ", "オンライン", "Online"),
    ("オ", "オブジェクト", "Object"),
    ("オ", "オペレーション", "Operation"),
    ("オ", "オレンジ", "Orange"),
    ("オ", "オート", "Auto"),
    ("オ", "オリジナル", "Original"),
]

# ----------------------------
# BUILD GRAPH
# ----------------------------
G = nx.DiGraph()

for start, end, meaning in relationships:
    G.add_edge(start, end, label=meaning)

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

vowel_map = {
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
output_path = Path(__file__).with_suffix(".html")


def open_html_in_browser(path: Path) -> None:
    preferred_browser = os.environ.get("KANA_BROWSER", "").strip().lower()
    resolved_path = path.resolve()

    if preferred_browser in {"safari", "apple safari"}:
        if sys.platform == "darwin":
            subprocess.Popen(["open", "-a", "Safari", str(resolved_path)])
            return

        safari_candidates = [
            r"C:\Program Files\Safari\Safari.exe",
            r"C:\Program Files (x86)\Safari\Safari.exe",
        ]
        for candidate in safari_candidates:
            if os.path.exists(candidate):
                subprocess.Popen([candidate, str(resolved_path)])
                return

    try:
        webbrowser.open(resolved_path.as_uri())
    except Exception:
        pass


html = f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta http-equiv=\"X-UA-Compatible\" content=\"IE=edge,chrome=1\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1, maximum-scale=1, viewport-fit=cover\" />
  <meta name=\"apple-mobile-web-app-capable\" content=\"yes\" />
  <meta name=\"apple-mobile-web-app-status-bar-style\" content=\"default\" />
  <meta name=\"format-detection\" content=\"telephone=no\" />
  <title>Katakana Vocabulary Network</title>
  <style>
    html, body {{
      height: 100%;
      width: 100%;
      margin: 0;
      overflow: hidden;
    }}
    body {{
      display: flex;
      flex-direction: column;
      font-family: '{JP_FONT}', 'Noto Sans CJK JP', 'Yu Gothic', 'Meiryo', sans-serif;
      background: #f8fafc;
      color: #111827;
      -webkit-text-size-adjust: 100%;
      -webkit-touch-callout: none;
      touch-action: manipulation;
    }}
    .controls {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
      padding: 1rem 1.5rem 0.5rem;
      flex-shrink: 0;
      flex-wrap: wrap;
    }}
    label {{
      font-weight: 600;
      color: #374151;
    }}
    select {{
      padding: 0.4rem 0.7rem;
      border: 1px solid #cbd5e1;
      border-radius: 0.4rem;
      font-size: 0.95rem;
      -webkit-appearance: menulist;
      appearance: auto;
    }}
    button {{
      padding: 0.4rem 0.8rem;
      border: 1px solid #cbd5e1;
      border-radius: 0.4rem;
      background: #ffffff;
      cursor: pointer;
      font-size: 0.95rem;
    }}
    h1 {{
      margin: 0;
      padding: 0 1.5rem 0.25rem;
      font-size: 1.4rem;
    }}
    p {{
      margin: 0;
      padding: 0 1.5rem 0.75rem;
      color: #4b5563;
    }}
    #graphWrap {{
      flex: 1 1 auto;
      position: relative;
      min-height: 320px;
      margin: 0 0.75rem 0.75rem;
      border: 1px solid #e5e7eb;
      background: white;
      overflow: hidden;
      border-radius: 0.5rem;
    }}
    #graph {{
      width: 100%;
      height: 100%;
      display: block;
      touch-action: none;
      background: white;
    }}
    #edgeLabel {{
      position: absolute;
      display: none;
      pointer-events: none;
      background: rgba(255, 255, 255, 0.95);
      color: #111827;
      padding: 0.3rem 0.45rem;
      border: 1px solid #d1d5db;
      border-radius: 0.25rem;
      font-size: 0.8rem;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
      z-index: 10;
      max-width: 220px;
    }}
    .node {{
      cursor: pointer;
    }}
    .edge {{
      stroke: #94a3b8;
      stroke-width: 2;
      fill: none;
      cursor: pointer;
    }}
    .node-label {{
      font-size: 16px;
      fill: #111827;
      text-anchor: middle;
      dominant-baseline: middle;
      pointer-events: none;
      user-select: none;
    }}
    .center-label {{
      font-size: 22px;
      fill: #111827;
      text-anchor: middle;
      dominant-baseline: middle;
      pointer-events: none;
      user-select: none;
    }}
  </style>
</head>
<body>
  <div class=\"controls\">
    <label for=\"vowelSelect\">Choose vowel</label>
    <select id=\"vowelSelect\">
      <option value=\"a\">A (ア)</option>
      <option value=\"e\">E (エ)</option>
      <option value=\"i\">I (イ)</option>
      <option value=\"o\">O (オ)</option>
      <option value=\"u\">U (ウ)</option>
    </select>
    <button id="pronounceButton" type="button">Play pronunciation</button>
  </div>
  <h1>Katakana Vocabulary Network</h1>
  <p>Select a vowel to view its words arranged evenly around a circle.</p>
  <div id="graphWrap">
    <svg id="graph" viewBox="0 0 1000 700" xmlns="http://www.w3.org/2000/svg"></svg>
    <div id="edgeLabel"></div>
  </div>
  <script>
    const relationships = {json.dumps(relationship_payload)};
    const vowelMap = {json.dumps(vowel_map)};
    const colorMap = {json.dumps(color_map)};
    const svg = document.getElementById('graph');
    const edgeLabel = document.getElementById('edgeLabel');
    const select = document.getElementById('vowelSelect');
    const pronounceButton = document.getElementById('pronounceButton');
    const ns = 'http://www.w3.org/2000/svg';

    function speakText(text, lang = 'ja-JP') {{
      if (!('speechSynthesis' in window)) {{
        alert('Speech synthesis is not supported in this browser.');
        return;
      }}
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = lang;
      utterance.rate = 0.9;
      utterance.pitch = 1.05;
      const voices = window.speechSynthesis.getVoices();
      const japaneseVoice = voices.find((voice) => voice.lang.startsWith('ja')) || voices[0];
      if (japaneseVoice) {{
        utterance.voice = japaneseVoice;
      }}
      window.speechSynthesis.cancel();
      window.speechSynthesis.speak(utterance);
    }}

    function speakPronunciation(selectedKey) {{
      const centerVowel = vowelMap[selectedKey];
      speakText(centerVowel);
    }}

    function shuffle(items) {{
      const arr = items.slice();
      for (let i = arr.length - 1; i > 0; i--) {{
        const j = Math.floor(Math.random() * (i + 1));
        [arr[i], arr[j]] = [arr[j], arr[i]];
      }}
      return arr;
    }}

    function showEdgeLabel(text, x, y) {{
      edgeLabel.textContent = text;
      edgeLabel.style.display = 'block';
      edgeLabel.style.left = Math.min(Math.max(x + 12, 8), window.innerWidth - 240) + 'px';
      edgeLabel.style.top = Math.min(Math.max(y + 8, 8), window.innerHeight - 60) + 'px';
    }}

    function hideEdgeLabel() {{
      edgeLabel.style.display = 'none';
    }}

    function buildGraph(selectedKey) {{
      const centerVowel = vowelMap[selectedKey];
      const relations = relationships.filter((rel) => rel.source === centerVowel);
      const centerX = 500;
      const centerY = 340;
      const radius = 240;
      const childCount = Math.max(relations.length, 1);
      const shuffledIndices = shuffle([...Array(childCount).keys()]);
      const centerLabel = centerVowel + ' / ' + selectedKey.toUpperCase();

      svg.innerHTML = '';

      relations.forEach((rel, index) => {{
        const positionIndex = shuffledIndices[index];
        const angle = ((positionIndex / childCount) * 2 * Math.PI) - (Math.PI / 2);
        const nodeX = centerX + Math.cos(angle) * radius;
        const nodeY = centerY + Math.sin(angle) * radius;

        const line = document.createElementNS(ns, 'line');
        line.setAttribute('x1', centerX);
        line.setAttribute('y1', centerY);
        line.setAttribute('x2', nodeX);
        line.setAttribute('y2', nodeY);
        line.setAttribute('class', 'edge');
        line.addEventListener('mouseenter', (event) => showEdgeLabel(rel.label, event.clientX, event.clientY));
        line.addEventListener('mousemove', (event) => showEdgeLabel(rel.label, event.clientX, event.clientY));
        line.addEventListener('mouseleave', hideEdgeLabel);
        line.addEventListener('click', () => speakText(rel.target));
        svg.appendChild(line);

        const group = document.createElementNS(ns, 'g');
        group.setAttribute('class', 'node');
        group.setAttribute('data-word', rel.target);
        group.addEventListener('click', () => speakText(rel.target));

        const box = document.createElementNS(ns, 'rect');
        box.setAttribute('x', nodeX - 92);
        box.setAttribute('y', nodeY - 24);
        box.setAttribute('width', 184);
        box.setAttribute('height', 48);
        box.setAttribute('rx', 14);
        box.setAttribute('fill', '#f8fafc');
        box.setAttribute('stroke', '#94a3b8');
        box.setAttribute('stroke-width', 2);
        group.appendChild(box);

        const label = document.createElementNS(ns, 'text');
        label.setAttribute('class', 'node-label');
        label.setAttribute('x', nodeX);
        label.setAttribute('y', nodeY + 2);
        label.textContent = rel.target;
        group.appendChild(label);
        svg.appendChild(group);
      }});

      const centerGroup = document.createElementNS(ns, 'g');
      const centerNode = document.createElementNS(ns, 'circle');
      centerNode.setAttribute('cx', centerX);
      centerNode.setAttribute('cy', centerY);
      centerNode.setAttribute('r', 58);
      centerNode.setAttribute('fill', colorMap[centerVowel] || '#dbeafe');
      centerNode.setAttribute('stroke', '#111827');
      centerNode.setAttribute('stroke-width', 2);
      centerGroup.appendChild(centerNode);

      const centerText = document.createElementNS(ns, 'text');
      centerText.setAttribute('class', 'center-label');
      centerText.setAttribute('x', centerX);
      centerText.setAttribute('y', centerY + 2);
      centerText.textContent = centerLabel;
      centerGroup.appendChild(centerText);
      svg.appendChild(centerGroup);
    }}

    function initializeGraph() {{
      select.addEventListener('change', (event) => buildGraph(event.target.value));
      pronounceButton.addEventListener('click', () => speakPronunciation(select.value));
      buildGraph(select.value);
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

output_path.write_text(html, encoding="utf-8")
print(f"Interactive HTML created at: {output_path}")
open_html_in_browser(output_path)