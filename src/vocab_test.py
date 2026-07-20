import json
from pathlib import Path

from gana_speed_test_data import HIRAGANA_ENTRIES

STARTER_SET_SIZE = 25

def build_html(entries: list[dict[str, str]]) -> str:
    payload = json.dumps(entries, ensure_ascii=False)
    return f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>Hiragana Matching Practice</title>
  <style>
    :root {{
      --bg: #f7f8f3;
      --panel: #ffffff;
      --ink: #1f2937;
      --muted: #6b7280;
      --accent: #0f766e;
      --accent-soft: #ccfbf1;
      --ok: #166534;
      --ok-soft: #dcfce7;
      --bad: #991b1b;
      --bad-soft: #fee2e2;
      --line: #d1d5db;
    }}

    * {{ box-sizing: border-box; }}

    body {{
      margin: 0;
      font-family: "Trebuchet MS", "Segoe UI", sans-serif;
      color: var(--ink);
      background:
        radial-gradient(circle at 10% 10%, #d1fae5 0%, transparent 35%),
        radial-gradient(circle at 90% 15%, #fde68a 0%, transparent 30%),
        var(--bg);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 0.65rem;
      padding: 1rem;
    }}

    .page-tabs {{
      width: min(980px, 100%);
      display: flex;
      gap: 0.5rem;
      padding: 0.25rem;
      background: #ffffff;
      border: 1px solid var(--line);
      border-radius: 12px;
      box-shadow: 0 6px 16px rgba(15, 23, 42, 0.06);
    }}

    .page-tab {{
      flex: 1;
      text-align: center;
      padding: 0.55rem 0.8rem;
      border-radius: 9px;
      text-decoration: none;
      font-weight: 700;
      font-size: 0.92rem;
      color: #134e4a;
      background: #f0fdfa;
      border: 1px solid #99f6e4;
    }}

    .page-tab.active {{
      background: linear-gradient(135deg, #0f766e, #0ea5a4);
      color: #ffffff;
      border-color: transparent;
    }}

    .app {{
      width: min(980px, 100%);
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 16px;
      box-shadow: 0 16px 40px rgba(15, 23, 42, 0.08);
      overflow: hidden;
    }}

    .header {{
      padding: 1rem 1.25rem;
      background: linear-gradient(135deg, #0f766e, #0ea5a4);
      color: #f0fdfa;
    }}

    h1 {{
      margin: 0;
      font-size: 1.4rem;
      letter-spacing: 0.02em;
    }}

    .sub {{
      margin: 0.35rem 0 0;
      font-size: 0.95rem;
      opacity: 0.95;
    }}

    .stats {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.75rem;
      align-items: center;
      justify-content: space-between;
      padding: 0.85rem 1.25rem;
      border-bottom: 1px solid var(--line);
    }}

    .status {{
      font-size: 0.95rem;
      color: var(--muted);
    }}

    .actions button {{
      border: 0;
      border-radius: 10px;
      padding: 0.55rem 0.8rem;
      background: var(--accent);
      color: #ffffff;
      cursor: pointer;
      font-weight: 600;
    }}

    .actions {{
      display: flex;
      gap: 0.5rem;
      flex-wrap: wrap;
      justify-content: flex-end;
    }}

    .actions button:hover {{
      filter: brightness(1.05);
    }}

    .board {{
      display: grid;
      grid-template-columns: 1fr;
      gap: 0.8rem;
      padding: 1rem;
    }}

    .col {{
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 0.8rem;
      background: #fcfcfb;
    }}

    .col h2 {{
      margin: 0 0 0.65rem;
      font-size: 1rem;
      color: #334155;
    }}

    .grid {{
      display: grid;
      --grid-cols: 5;
      grid-template-columns: repeat(var(--grid-cols), minmax(0, 1fr));
      gap: 0.5rem;
    }}

    .card {{
      border: 1px solid #cbd5e1;
      border-radius: 10px;
      background: #ffffff;
      padding: 0.6rem 0.45rem;
      cursor: pointer;
      text-align: center;
      transition: transform 120ms ease, background-color 120ms ease;
      min-height: 56px;
    }}

    .card:hover {{
      transform: translateY(-1px);
      background: #f8fafc;
    }}

    .card.selected {{
      border-color: var(--accent);
      background: var(--accent-soft);
    }}

    .card.correct {{
      border-color: var(--ok);
      background: var(--ok-soft);
      color: var(--ok);
      cursor: default;
    }}

    .card.wrong {{
      border-color: var(--bad);
      background: var(--bad-soft);
      color: var(--bad);
    }}

    .card.known {{
      border-color: #047857;
      background: #d1fae5;
      color: #065f46;
    }}

    .kana {{
      font-size: 1.6rem;
      line-height: 1;
      margin-bottom: 0.15rem;
    }}

    .hint {{
      font-size: 0.72rem;
      color: var(--muted);
    }}

    .romaji-reveal {{
      margin-top: 0.2rem;
      font-size: 0.78rem;
      font-weight: 700;
      color: #0f766e;
      letter-spacing: 0.02em;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.3rem;
      flex-wrap: wrap;
    }}

    .romaji-text {{
      text-transform: lowercase;
    }}

    .romaji-helper {{
      font-size: 0.72rem;
      color: #0b5f58;
      font-weight: 600;
    }}

    body.dark-mode {{
      color: #e5e7eb;
      background:
        radial-gradient(circle at 10% 10%, #134e4a 0%, transparent 40%),
        radial-gradient(circle at 90% 15%, #78350f 0%, transparent 35%),
        #0b1220;
    }}

    body.dark-mode .page-tabs {{
      background: #111827;
      border-color: #334155;
      box-shadow: 0 6px 16px rgba(2, 6, 23, 0.5);
    }}

    body.dark-mode .page-tab {{
      background: #172554;
      border-color: #1d4ed8;
      color: #dbeafe;
    }}

    body.dark-mode .app {{
      background: #111827;
      border-color: #334155;
      box-shadow: 0 16px 40px rgba(2, 6, 23, 0.55);
    }}

    body.dark-mode .stats {{
      border-bottom-color: #334155;
    }}

    body.dark-mode .status {{
      color: #9ca3af;
    }}

    body.dark-mode .actions button {{
      background: #0e7490;
      color: #ecfeff;
    }}

    body.dark-mode .col {{
      border-color: #334155;
      background: #0f172a;
    }}

    body.dark-mode .col h2 {{
      color: #cbd5e1;
    }}

    body.dark-mode .card {{
      border-color: #475569;
      background: #1e293b;
      color: #e2e8f0;
    }}

    body.dark-mode .card:hover {{
      background: #273449;
    }}

    body.dark-mode .card.selected {{
      border-color: #2dd4bf;
      background: #134e4a;
      color: #ccfbf1;
    }}

    body.dark-mode .card.correct {{
      border-color: #22c55e;
      background: #14532d;
      color: #bbf7d0;
    }}

    body.dark-mode .card.wrong {{
      border-color: #ef4444;
      background: #7f1d1d;
      color: #fecaca;
    }}

    body.dark-mode .card.known {{
      border-color: #34d399;
      background: #064e3b;
      color: #a7f3d0;
    }}

    body.dark-mode .hint {{
      color: #94a3b8;
    }}

    body.dark-mode .romaji-reveal {{
      color: #5eead4;
    }}

    body.dark-mode .romaji-helper {{
      color: #99f6e4;
    }}

    @media (max-width: 760px) {{
      .page-tabs {{
        width: 100%;
      }}

      .board {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <nav class=\"page-tabs\" aria-label=\"Page tabs\">
    <a class=\"page-tab\" href=\"index.html\">Vocabulary Network</a>
    <a class=\"page-tab active\" href=\"hiragana_match.html\" aria-current=\"page\">Hiragana Match</a>
  </nav>

  <main class=\"app\">
    <section class=\"header\">
      <h1>Hiragana 1st/2nd Set Practice</h1>
      <p class=\"sub\" id=\"setLabel\">Set: vowels (a, i, u, e, o) + k, s, t, n rows</p>
    </section>

    <section class=\"stats\">
      <div class="status" id="status">Click a Hiragana card to mark it known and reveal romaji.</div>
      <div class=\"actions\">
        <button id="switchSetBtn" type="button">Switch to 2nd Set</button>
        <button id="modeBtn" type="button">Switch to Match Romaji</button>
        <button id="themeBtn" type="button">Dark Mode</button>
        <button id=\"resetBtn\" type=\"button\">Shuffle / Reset</button>
      </div>
    </section>

    <section class=\"board\">
      <article class=\"col\">
        <h2>Hiragana</h2>
        <div id=\"kanaGrid\" class=\"grid\"></div>
      </article>
    </section>
  </main>

  <script>
    const entries = {payload};

    const statusEl = document.getElementById("status");
    const setLabelEl = document.getElementById("setLabel");
    const kanaGrid = document.getElementById("kanaGrid");
    const switchSetBtn = document.getElementById("switchSetBtn");
    const modeBtn = document.getElementById("modeBtn");
    const themeBtn = document.getElementById("themeBtn");
    const resetBtn = document.getElementById("resetBtn");
    const GRID_MIN_CARD_WIDTH = 108;
    const GRID_MIN_COLS = 1;
    const GRID_MAX_COLS = 8;
    const ATTEMPT_HISTORY_KEY = "hiraganaMatchAttemptHistory";
    const MATCH_MODE_KEY = "hiraganaMatchMode";
    const MAX_ATTEMPT_HISTORY = 5;
    const STARTER_SET_SIZE = {STARTER_SET_SIZE};
    const STARTER_SET_TEXT = "vowels (a, i, u, e, o) + k, s, t, n rows";
    const REMAINING_SET_TEXT = "remaining rows: h, m, y, r, w + n, g (ga gi gu ge)";

    let attemptStartMs = Date.now();
    let roundCompleted = false;
    let activeEntries = [];
    let showingRemainingSet = false;
    let matchingRomaji = localStorage.getItem(MATCH_MODE_KEY) === "romaji";

    function getStarterEntries() {{
      return entries.slice(0, Math.min(STARTER_SET_SIZE, entries.length));
    }}

    function getRemainingEntries() {{
      if (entries.length <= STARTER_SET_SIZE) {{
        return [];
      }}
      return entries.slice(STARTER_SET_SIZE);
    }}

    function setSetButtonLabel() {{
      switchSetBtn.textContent = showingRemainingSet ? "Switch to 1st Set" : "Switch to 2nd Set";
    }}

    function setSetSubtitle() {{
      setLabelEl.textContent = showingRemainingSet
        ? `Set: ${{REMAINING_SET_TEXT}}`
        : `Set: ${{STARTER_SET_TEXT}}`;
    }}

    function setModeButtonLabel() {{
      modeBtn.textContent = matchingRomaji ? "Switch to Match Hiragana" : "Switch to Match Romaji";
    }}

    function setMatchingMode(enabled) {{
      matchingRomaji = enabled;
      localStorage.setItem(MATCH_MODE_KEY, enabled ? "romaji" : "kana");
      setModeButtonLabel();
    }}

    function setThemeButtonLabel() {{
      themeBtn.textContent = document.body.classList.contains("dark-mode") ? "Light Mode" : "Dark Mode";
    }}

    function setDarkMode(enabled) {{
      document.body.classList.toggle("dark-mode", enabled);
      localStorage.setItem("hiraganaMatchTheme", enabled ? "dark" : "light");
      setThemeButtonLabel();
    }}

    function shuffle(items) {{
      const copy = [...items];
      for (let i = copy.length - 1; i > 0; i -= 1) {{
        const j = Math.floor(Math.random() * (i + 1));
        [copy[i], copy[j]] = [copy[j], copy[i]];
      }}
      return copy;
    }}

    function updateStatus(message) {{
      statusEl.textContent = message;
    }}

    function updateGridColumns() {{
      const availableWidth = Math.floor(kanaGrid.getBoundingClientRect().width);
      const calculatedCols = Math.floor(availableWidth / GRID_MIN_CARD_WIDTH);
      const cols = Math.max(GRID_MIN_COLS, Math.min(GRID_MAX_COLS, calculatedCols || GRID_MIN_COLS));
      kanaGrid.style.setProperty("--grid-cols", String(cols));
    }}

    function loadAttemptHistory() {{
      try {{
        const raw = localStorage.getItem(ATTEMPT_HISTORY_KEY);
        if (!raw) {{
          return [];
        }}

        const parsed = JSON.parse(raw);
        if (!Array.isArray(parsed)) {{
          return [];
        }}

        return parsed
          .filter((item) => Number.isFinite(item?.seconds))
          .map((item) => ({{ seconds: Math.max(0, Math.round(item.seconds)) }}))
          .slice(0, MAX_ATTEMPT_HISTORY);
      }} catch (_error) {{
        return [];
      }}
    }}

    function saveAttemptHistory(history) {{
      localStorage.setItem(ATTEMPT_HISTORY_KEY, JSON.stringify(history.slice(0, MAX_ATTEMPT_HISTORY)));
    }}

    function recordAttempt(seconds) {{
      const history = loadAttemptHistory();
      history.unshift({{ seconds }});
      const nextHistory = history.slice(0, MAX_ATTEMPT_HISTORY);
      saveAttemptHistory(nextHistory);
      return nextHistory;
    }}

    function formatHistory(history) {{
      if (!history.length) {{
        return "No previous attempts yet.";
      }}

      return `Last ${{history.length}}: ${{history.map((attempt) => `${{attempt.seconds}}s`).join(", ")}}`;
    }}

    function handleSelect(button) {{
      button.classList.toggle("known");

      const romajiReveal = button.querySelector(".romaji-reveal");
      if (romajiReveal) {{
        romajiReveal.remove();
      }} else {{
        const revealEl = document.createElement("div");
        revealEl.className = "romaji-reveal";
        revealEl.innerHTML = matchingRomaji
          ? `<span class="romaji-text">${{button.dataset.kana}}</span><span class="romaji-helper">(${{button.dataset.pronunciation}})</span>`
          : `<span class="romaji-text">${{button.dataset.romaji}}</span><span class="romaji-helper">(${{button.dataset.pronunciation}})</span>`;
        button.appendChild(revealEl);
      }}

      const knownCount = kanaGrid.querySelectorAll('.card.known').length;

      if (knownCount === activeEntries.length && !roundCompleted) {{
        roundCompleted = true;
        const elapsedSeconds = Math.max(0, Math.round((Date.now() - attemptStartMs) / 1000));
        const history = recordAttempt(elapsedSeconds);
        updateStatus(`Finished in ${{elapsedSeconds}} seconds. ${{formatHistory(history)}}`);
        return;
      }}

      updateStatus(matchingRomaji
        ? `Romaji-to-kana mode: ${{knownCount}}/${{activeEntries.length}} cards marked as known.`
        : `Hiragana-to-romaji mode: ${{knownCount}}/${{activeEntries.length}} kana marked as known.`);
    }}

    function render() {{
      attemptStartMs = Date.now();
      roundCompleted = false;
      kanaGrid.innerHTML = "";

      const sourceEntries = showingRemainingSet ? getRemainingEntries() : getStarterEntries();
      activeEntries = shuffle(sourceEntries);

      if (!activeEntries.length) {{
        updateStatus("No kana found for this set. Check your data source.");
        return;
      }}

      setSetButtonLabel();
      setSetSubtitle();
      setModeButtonLabel();

      activeEntries.forEach((item) => {{
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "card";
        btn.dataset.romaji = item.romaji;
        btn.dataset.kana = item.kana;
        btn.dataset.pronunciation = item.pronunciation;
        btn.innerHTML = matchingRomaji
          ? `<div class="kana">${{item.romaji}}</div>`
          : `<div class="kana">${{item.kana}}</div>`;
        btn.addEventListener("click", () => handleSelect(btn));
        kanaGrid.appendChild(btn);
      }});

      updateGridColumns();

      updateStatus(matchingRomaji
        ? "Romaji-to-kana mode: click any romaji card to toggle known and reveal hiragana."
        : "Hiragana-to-romaji mode: click any kana card to toggle known and reveal romaji.");
    }}

    themeBtn.addEventListener("click", () => {{
      setDarkMode(!document.body.classList.contains("dark-mode"));
    }});

    setDarkMode(localStorage.getItem("hiraganaMatchTheme") === "dark");

    switchSetBtn.addEventListener("click", () => {{
      showingRemainingSet = !showingRemainingSet;
      render();
    }});

    modeBtn.addEventListener("click", () => {{
      setMatchingMode(!matchingRomaji);
      render();
    }});

    resetBtn.addEventListener("click", render);
    window.addEventListener("resize", updateGridColumns);
    window.addEventListener("orientationchange", updateGridColumns);

    if (typeof ResizeObserver !== "undefined") {{
      const resizeObserver = new ResizeObserver(updateGridColumns);
      resizeObserver.observe(kanaGrid);
    }}

    render();
  </script>
</body>
</html>
"""


def generate_html(output_file: Path | None = None) -> Path:
    if output_file is None:
        output_file = Path(__file__).resolve().parent.parent / "docs" / "hiragana_match.html"

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(build_html(HIRAGANA_ENTRIES), encoding="utf-8")
    return output_file


if __name__ == "__main__":
    path = generate_html()
    print(f"Created: {path}")
