import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


CSV_PATH = Path("comparative_topic_matrix_with_subtopic.csv")
OUT_HTML = Path("high_level_relationship_chart.html")


PENTATEUCH_BOOKS = {
    "Gen": "Genesis",
    "Ex": "Exodus",
    "Lev": "Leviticus",
    "Num": "Numbers",
    "Deut": "Deuteronomy",
}

TRACTATE_TO_SEDER = {
    # Zeraim
    "Berakhot": "Zeraim",
    "Peah": "Zeraim",
    "Demai": "Zeraim",
    "Kilayim": "Zeraim",
    "Sheviit": "Zeraim",
    "Terumot": "Zeraim",
    "Maasrot": "Zeraim",
    "Maaser Sheni": "Zeraim",
    "Challah": "Zeraim",
    "Orlah": "Zeraim",
    "Bikkurim": "Zeraim",
    # Moed
    "Shabbat": "Moed",
    "Eruvin": "Moed",
    "Pesachim": "Moed",
    "Yoma": "Moed",
    "Sukkah": "Moed",
    "Beitzah": "Moed",
    "Rosh Hashanah": "Moed",
    "Taanit": "Moed",
    "Megillah": "Moed",
    "Moed Katan": "Moed",
    "Chagigah": "Moed",
    # Nashim
    "Yevamot": "Nashim",
    "Ketubot": "Nashim",
    "Nedarim": "Nashim",
    "Nazir": "Nashim",
    "Sotah": "Nashim",
    "Gittin": "Nashim",
    "Kiddushin": "Nashim",
    # Nezikin
    "Bava Kamma": "Nezikin",
    "Bava Metzia": "Nezikin",
    "Bava Batra": "Nezikin",
    "Sanhedrin": "Nezikin",
    "Makkot": "Nezikin",
    "Shevuot": "Nezikin",
    "Eduyot": "Nezikin",
    "Horayot": "Nezikin",
    # Kodashim
    "Chullin": "Kodashim",
    "Bekhorot": "Kodashim",
    "Zevachim": "Kodashim",
    "Menachot": "Kodashim",
    "Tamid": "Kodashim",
    "Middot": "Kodashim",
    "Kinnim": "Kodashim",
    # Tahorot
    "Niddah": "Tahorot",
    "Kelim": "Tahorot",
    "Oholot": "Tahorot",
    "Negaim": "Tahorot",
    "Parah": "Tahorot",
    "Tahorot": "Tahorot",
    "Mikvaot": "Tahorot",
}

SEFER_NORMALIZATION = {
    "Madda": "Madda",
    "Ahavah": "Ahavah",
    "Zemanim": "Zemanim",
    "Nashim": "Nashim",
    "Kedushah": "Kedushah",
    "Hafla'ah": "Haflaah",
    "Haflaah": "Haflaah",
    "Zeraim": "Zeraim",
    "Avodah": "Avodah",
    "Korbanot": "Korbanot",
    "Taharah": "Taharah",
    "Nezikin": "Nezikin",
    "Kinyan": "Kinyan",
    "Mishpatim": "Mishpatim",
    "Shoftim": "Shoftim",
    "Nachalah": "Kinyan",
}


def split_parts(value: str) -> list[str]:
    return [p.strip() for p in value.split(";") if p.strip()]


def pentateuch_nodes(bible_range: str) -> set[str]:
    books = set()
    for part in split_parts(bible_range):
        m = re.match(r"^([A-Za-z]+)\s", part)
        if not m:
            continue
        abbr = m.group(1)
        if abbr in PENTATEUCH_BOOKS:
            books.add(PENTATEUCH_BOOKS[abbr])
    return books


def mishnah_nodes(mishnah_range: str) -> set[str]:
    sedarim = set()
    for part in split_parts(mishnah_range):
        m = re.match(r"^([A-Za-z' ]+?)\s+\d", part)
        if not m:
            continue
        tractate = m.group(1).strip()
        seder = TRACTATE_TO_SEDER.get(tractate)
        if seder:
            sedarim.add(seder)
    return sedarim


def mt_nodes(mt_unit: str) -> set[str]:
    sefarim = set()
    for part in split_parts(mt_unit):
        m = re.search(r"Sefer\s+([A-Za-z' ]+)", part)
        if not m:
            continue
        raw = m.group(1).strip()
        raw = raw.split(":")[0].strip()
        raw = raw.split("(")[0].strip()
        normalized = SEFER_NORMALIZATION.get(raw)
        if normalized:
            sefarim.add(normalized)
    return sefarim


def sa_nodes(sa_simanim: str) -> set[str]:
    if sa_simanim.startswith("("):
        return {"No Practical Parallel"}
    nodes = set()
    for part in split_parts(sa_simanim):
        p = part.strip()
        if p.startswith("Orach Chayim"):
            nodes.add("Orach Chayim")
        elif p.startswith("Yoreh De'ah"):
            nodes.add("Yoreh Deah")
        elif p.startswith("Even HaEzer"):
            nodes.add("Even HaEzer")
        elif p.startswith("Choshen Mishpat"):
            nodes.add("Choshen Mishpat")
    return nodes or {"No Practical Parallel"}


def add_weighted_links(counter: Counter, left: set[str], right: set[str]) -> None:
    if not left or not right:
        return
    w = 1.0 / (len(left) * len(right))
    for a in left:
        for b in right:
            counter[(a, b)] += w


def citation_snippet(row: dict[str, str], layer_pair: int) -> str:
    if layer_pair == 1:
        return f"Bible: {row['Bible range']} | Mishnah: {row['Mishnah range']}"
    if layer_pair == 2:
        return f"Mishnah: {row['Mishnah range']} | Mishneh Torah: {row['Mishneh Torah unit']}"
    return f"Mishneh Torah: {row['Mishneh Torah unit']} | Shulchan Aruch: {row['Shulchan Aruch simanim']}"


def append_evidence(
    evidence: dict[tuple[int, str, str], list[str]],
    layer_pair: int,
    left: set[str],
    right: set[str],
    row: dict[str, str],
) -> None:
    if not left or not right:
        return
    snippet = citation_snippet(row, layer_pair)
    line = f"- {row['Subtopic']}: {snippet}"
    for a in left:
        for b in right:
            key = (layer_pair, a, b)
            bucket = evidence[key]
            # Keep tooltip readable while still citation-aware.
            if len(bucket) < 4 and line not in bucket:
                bucket.append(line)


def build_graph(rows: list[dict[str, str]]) -> tuple[list[dict], list[dict]]:
    links_l1_l2 = Counter()
    links_l2_l3 = Counter()
    links_l3_l4 = Counter()
    evidence = defaultdict(list)

    node_values = defaultdict(float)

    for row in rows:
        l1 = pentateuch_nodes(row["Bible range"])
        l2 = mishnah_nodes(row["Mishnah range"])
        l3 = mt_nodes(row["Mishneh Torah unit"])
        l4 = sa_nodes(row["Shulchan Aruch simanim"])

        add_weighted_links(links_l1_l2, l1, l2)
        add_weighted_links(links_l2_l3, l2, l3)
        add_weighted_links(links_l3_l4, l3, l4)
        append_evidence(evidence, 1, l1, l2, row)
        append_evidence(evidence, 2, l2, l3, row)
        append_evidence(evidence, 3, l3, l4, row)

    for (a, b), v in links_l1_l2.items():
        node_values[a] += v
        node_values[b] += v
    for (a, b), v in links_l2_l3.items():
        node_values[a] += v
        node_values[b] += v
    for (a, b), v in links_l3_l4.items():
        node_values[a] += v
        node_values[b] += v

    # Per your requested display order (halakhic flow emphasis): Exodus first.
    layer1 = ["Exodus", "Leviticus", "Numbers", "Deuteronomy", "Genesis"]
    layer2 = ["Zeraim", "Moed", "Nashim", "Nezikin", "Kodashim", "Tahorot"]
    layer3 = [
        "Madda",
        "Ahavah",
        "Zemanim",
        "Nashim",
        "Kedushah",
        "Haflaah",
        "Zeraim",
        "Avodah",
        "Korbanot",
        "Taharah",
        "Nezikin",
        "Kinyan",
        "Mishpatim",
        "Shoftim",
    ]
    layer4 = [
        "Orach Chayim",
        "Yoreh Deah",
        "Even HaEzer",
        "Choshen Mishpat",
        "No Practical Parallel",
    ]

    nodes = []
    for label in layer1:
        nodes.append({"id": f"L1:{label}", "name": label, "layer": 1, "value": node_values.get(label, 0)})
    for label in layer2:
        nodes.append({"id": f"L2:{label}", "name": label, "layer": 2, "value": node_values.get(label, 0)})
    for label in layer3:
        nodes.append({"id": f"L3:{label}", "name": label, "layer": 3, "value": node_values.get(label, 0)})
    for label in layer4:
        nodes.append({"id": f"L4:{label}", "name": label, "layer": 4, "value": node_values.get(label, 0)})

    node_id = {n["id"]: i for i, n in enumerate(nodes)}

    links = []
    for (a, b), v in links_l1_l2.items():
        tip = f"{a} -> {b}\\nWeight: {v:.2f}\\n\\nContributing entries (sample):\\n" + "\\n".join(
            evidence.get((1, a, b), [])
        )
        links.append(
            {
                "source": node_id[f"L1:{a}"],
                "target": node_id[f"L2:{b}"],
                "value": round(v, 4),
                "layer": 1,
                "tooltip": tip,
            }
        )
    for (a, b), v in links_l2_l3.items():
        tip = f"{a} -> {b}\\nWeight: {v:.2f}\\n\\nContributing entries (sample):\\n" + "\\n".join(
            evidence.get((2, a, b), [])
        )
        links.append(
            {
                "source": node_id[f"L2:{a}"],
                "target": node_id[f"L3:{b}"],
                "value": round(v, 4),
                "layer": 2,
                "tooltip": tip,
            }
        )
    for (a, b), v in links_l3_l4.items():
        tip = f"{a} -> {b}\\nWeight: {v:.2f}\\n\\nContributing entries (sample):\\n" + "\\n".join(
            evidence.get((3, a, b), [])
        )
        links.append(
            {
                "source": node_id[f"L3:{a}"],
                "target": node_id[f"L4:{b}"],
                "value": round(v, 4),
                "layer": 3,
                "tooltip": tip,
            }
        )

    return nodes, links


def render_html(nodes: list[dict], links: list[dict]) -> str:
    graph = {"nodes": nodes, "links": links}
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>High-Level Relationship Chart | Pentateuch, Mishnah, Mishneh Torah, Shulchan Aruch</title>
  <style>
    :root {{
      --bg: #f3f6fb;
      --ink: #1f2937;
      --muted: #6b7280;
      --card: #ffffff;
      --line: #d5deea;
      --l1: #4b8f3a;
      --l2: #f08a24;
      --l3: #2d78b8;
      --l4: #8b5fbf;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Segoe UI", "Noto Sans", Arial, sans-serif;
      color: var(--ink);
      background: linear-gradient(180deg, #f8fbff 0%, var(--bg) 100%);
    }}
    .wrap {{
      max-width: 1800px;
      margin: 0 auto;
      padding: 16px 16px 24px;
    }}
    h1 {{
      margin: 0 0 6px;
      font-size: 1.4rem;
      font-weight: 700;
    }}
    .subtitle {{
      margin: 0 0 12px;
      color: var(--muted);
      font-size: 0.96rem;
    }}
    .legend {{
      display: grid;
      grid-template-columns: repeat(4, minmax(180px, 1fr));
      gap: 8px;
      margin-bottom: 10px;
    }}
    .legend-item {{
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 6px 8px;
      font-size: 0.9rem;
    }}
    .dot {{
      display: inline-block;
      width: 10px;
      height: 10px;
      border-radius: 50%;
      margin-right: 6px;
      vertical-align: middle;
    }}
    #chart {{
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 10px;
      overflow: auto;
    }}
    svg {{
      display: block;
      min-width: 1500px;
    }}
    .node rect {{
      stroke: #fff;
      stroke-width: 1px;
    }}
    .node text {{
      font-size: 12px;
      fill: #1f2937;
      pointer-events: none;
    }}
    .link {{
      fill: none;
      stroke-opacity: 0.25;
      mix-blend-mode: multiply;
    }}
    .link:hover {{
      stroke-opacity: 0.65;
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <p style="margin:0 0 8px;"><a href="./index.html">Back to main citation tree</a></p>
    <h1>High-Level Relationship Chart</h1>
    <p class="subtitle">Based on current mappings: Pentateuch → Mishnah → Mishneh Torah → Shulchan Aruch (high-level, aggregated).</p>
    <div class="legend">
      <div class="legend-item"><span class="dot" style="background: var(--l1);"></span>Pentateuch (Books)</div>
      <div class="legend-item"><span class="dot" style="background: var(--l2);"></span>Mishnah (Sedarim)</div>
      <div class="legend-item"><span class="dot" style="background: var(--l3);"></span>Mishneh Torah (Sefarim)</div>
      <div class="legend-item"><span class="dot" style="background: var(--l4);"></span>Shulchan Aruch (4 Sections)</div>
    </div>
    <div id="chart"></div>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/d3-sankey@0.12.3/dist/d3-sankey.min.js"></script>
  <script>
    const graph = {json.dumps(graph, ensure_ascii=False)};

    const width = 1700;
    const height = 980;

    const colorByLayer = new Map([
      [1, getComputedStyle(document.documentElement).getPropertyValue('--l1').trim()],
      [2, getComputedStyle(document.documentElement).getPropertyValue('--l2').trim()],
      [3, getComputedStyle(document.documentElement).getPropertyValue('--l3').trim()],
      [4, getComputedStyle(document.documentElement).getPropertyValue('--l4').trim()],
    ]);

    const nodeColor = d => colorByLayer.get(d.layer) || "#888";
    const linkColor = d => colorByLayer.get(d.layer) || "#999";

    const svg = d3.select("#chart")
      .append("svg")
      .attr("viewBox", [0, 0, width, height])
      .attr("width", "100%")
      .attr("height", height);

    const sankey = d3.sankey()
      .nodeWidth(12)
      .nodePadding(8)
      .extent([[18, 40], [width - 18, height - 30]])
      .nodeAlign(d3.sankeyJustify)
      // Preserve the explicit node order provided by the Python layer lists.
      .nodeSort(null);

    const g = sankey({{
      nodes: graph.nodes.map(d => Object.assign({{}}, d)),
      links: graph.links.map(d => Object.assign({{}}, d))
    }});

    svg.append("g")
      .selectAll("path")
      .data(g.links)
      .join("path")
      .attr("class", "link")
      .attr("d", d3.sankeyLinkHorizontal())
      .attr("stroke", d => linkColor(d))
      .attr("stroke-width", d => Math.max(1, d.width))
      .append("title")
      .text(d => d.tooltip || `${{d.source.name}} -> ${{d.target.name}}\\nWeight: ${{d.value.toFixed(2)}}`);

    const node = svg.append("g")
      .selectAll("g")
      .data(g.nodes)
      .join("g")
      .attr("class", "node");

    node.append("rect")
      .attr("x", d => d.x0)
      .attr("y", d => d.y0)
      .attr("height", d => Math.max(2, d.y1 - d.y0))
      .attr("width", d => d.x1 - d.x0)
      .attr("fill", d => nodeColor(d))
      .append("title")
      .text(d => `${{d.name}}\\nTotal flow: ${{(d.value || 0).toFixed(2)}}`);

    node.append("text")
      .attr("x", d => d.x0 < width / 2 ? d.x1 + 6 : d.x0 - 6)
      .attr("y", d => (d.y1 + d.y0) / 2)
      .attr("dy", "0.35em")
      .attr("text-anchor", d => d.x0 < width / 2 ? "start" : "end")
      .text(d => d.name);
  </script>
</body>
</html>
"""


def main() -> None:
    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    nodes, links = build_graph(rows)
    html_text = render_html(nodes, links)
    OUT_HTML.write_text(html_text, encoding="utf-8")
    print(f"Wrote: {OUT_HTML}")
    print(f"Nodes: {len(nodes)}, Links: {len(links)}")


if __name__ == "__main__":
    main()
