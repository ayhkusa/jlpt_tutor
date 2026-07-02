import os

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

G = nx.DiGraph()
for source, target, meaning in relationships:
    G.add_edge(source, target, label=meaning)

color_map = {
    "ア": "#ff6b6b",
    "イ": "#4dabf7",
    "ウ": "#51cf66",
    "エ": "#ffd43b",
    "オ": "#b197fc",
}

node_colors = []
for node in G.nodes():
    if node in color_map:
        node_colors.append(color_map[node])
    elif node.startswith("ア"):
        node_colors.append("#ffb3b3")
    elif node.startswith("イ"):
        node_colors.append("#b3d9ff")
    elif node.startswith("ウ"):
        node_colors.append("#bff0c2")
    elif node.startswith("エ"):
        node_colors.append("#fff0a6")
    elif node.startswith("オ"):
        node_colors.append("#d9c2ff")
    else:
        node_colors.append("lightgray")

pos = {}
vowels = ["ア", "イ", "ウ", "エ", "オ"]
for i, v in enumerate(vowels):
    pos[v] = (0, 4 - i * 2)

radius = 3
for v in vowels:
    words = [target for source, target, _ in relationships if source == v]
    for i, word in enumerate(words):
        x = radius * ((i % 2) + 1) * (1 if i < 5 else -1)
        y = (i - 5) * 0.6 + (4 - vowels.index(v) * 2)
        pos[word] = (x, y)

fig, ax = plt.subplots(figsize=(18, 12))
nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=1800, ax=ax)
nx.draw_networkx_labels(G, pos, font_size=12, font_family=JP_FONT, ax=ax)
nx.draw_networkx_edges(G, pos, arrowstyle="-|>", arrowsize=18, width=1.5, edge_color="gray", ax=ax)
edge_labels = nx.get_edge_attributes(G, "label")
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8, font_family=JP_FONT, rotate=False, ax=ax)
ax.set_title("Katakana Vocabulary Network", fontsize=16, fontfamily=JP_FONT)
ax.axis("off")
fig.tight_layout()
fig.savefig("katakana_vocab_network.png", dpi=200, bbox_inches="tight", facecolor="white")
plt.show()
