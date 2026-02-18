import csv
import html
import re
from pathlib import Path
from urllib.parse import quote_plus, quote


CSV_PATH = Path("comparative_topic_matrix_with_subtopic.csv")
HTML_OUT = Path("comparative_topic_tree_hyperlinked.html")


CATEGORIES = [
    (
        "1) Sacred Time, Prayer, Festivals",
        [
            "Prayer/Shema/Tefillin",
            "Shabbat",
            "Eruvin/Boundary-Carrying Framework",
            "Pesach",
            "Yom Tov (general)",
            "Rosh Hashanah",
            "Yom Kippur",
            "Sukkot",
            "Public Fasts",
            "Purim/Megillah",
            "Chol HaMoed",
        ],
    ),
    (
        "2) Kashrut / Forbidden Foods / Bodily Sanctity",
        [
            "Permitted/Forbidden Species",
            "Ritual Slaughter",
            "Blood/Fat/Meat Prohibitions",
            "Firstborn (animal/human)",
            "Orlah",
        ],
    ),
    (
        "3) Family Law / Personal Status",
        [
            "Marriage/Kiddushin",
            "Vows",
            "Nazirite",
            "Sotah ordeal",
            "Divorce",
            "Levirate/Yibbum-Chalitzah",
            "Niddah",
        ],
    ),
    (
        "4) Civil, Commercial, Damages, Courts",
        [
            "Torts/Damages",
            "Commerce/Loans/Deposits",
            "Real Estate/Partnerships/Inheritance",
            "Courts/Testimony/Penalties",
        ],
    ),
    (
        "5) Temple, Sacrifices, Purity",
        [
            "Offerings (animal/meal)",
            "Temple Daily Service/Structure",
            "Bird Offerings/Nest Cases",
            "Purity/Impurity Systems",
        ],
    ),
    (
        "6) Agriculture / Land-Dependent Mitzvot",
        [
            "Peah/Leket/Shikhechah",
            "Terumah/Ma'aser",
            "Shemitah/Yovel",
            "Kilayim",
            "Challah",
            "Bikkurim",
        ],
    ),
]


BOOK_MAP = {
    "Ex": "Exodus",
    "Lev": "Leviticus",
    "Num": "Numbers",
    "Deut": "Deuteronomy",
    "Joel": "Joel",
    "Esther": "Esther",
}


SUBTOPIC_WIKI = {
    "Prayer/Shema/Tefillin": {"he": "תפילה וקריאת שמע", "en_url": "https://en.wikipedia.org/wiki/Jewish_prayer", "he_url": "https://he.wikipedia.org/wiki/תפילה"},
    "Shabbat": {"he": "שבת", "en_url": "https://en.wikipedia.org/wiki/Shabbat", "he_url": "https://he.wikipedia.org/wiki/שבת"},
    "Eruvin/Boundary-Carrying Framework": {"he": "עירוב", "en_url": "https://en.wikipedia.org/wiki/Eruv", "he_url": "https://he.wikipedia.org/wiki/עירוב"},
    "Pesach": {"he": "פסח", "en_url": "https://en.wikipedia.org/wiki/Passover", "he_url": "https://he.wikipedia.org/wiki/פסח"},
    "Yom Tov (general)": {"he": "יום טוב", "en_url": "https://en.wikipedia.org/wiki/Yom_tov", "he_url": "https://he.wikipedia.org/wiki/יום_טוב"},
    "Rosh Hashanah": {"he": "ראש השנה", "en_url": "https://en.wikipedia.org/wiki/Rosh_Hashanah", "he_url": "https://he.wikipedia.org/wiki/ראש_השנה"},
    "Yom Kippur": {"he": "יום הכיפורים", "en_url": "https://en.wikipedia.org/wiki/Yom_Kippur", "he_url": "https://he.wikipedia.org/wiki/יום_הכיפורים"},
    "Sukkot": {"he": "סוכות", "en_url": "https://en.wikipedia.org/wiki/Sukkot", "he_url": "https://he.wikipedia.org/wiki/סוכות"},
    "Public Fasts": {"he": "תענית", "en_url": "https://en.wikipedia.org/wiki/Fast_days_in_Judaism", "he_url": "https://he.wikipedia.org/wiki/תענית"},
    "Purim/Megillah": {"he": "פורים ומגילת אסתר", "en_url": "https://en.wikipedia.org/wiki/Purim", "he_url": "https://he.wikipedia.org/wiki/פורים"},
    "Chol HaMoed": {"he": "חול המועד", "en_url": "https://en.wikipedia.org/wiki/Chol_HaMoed", "he_url": "https://he.wikipedia.org/wiki/חול_המועד"},
    "Permitted/Forbidden Species": {"he": "כשרות", "en_url": "https://en.wikipedia.org/wiki/Kashrut", "he_url": "https://he.wikipedia.org/wiki/כשרות"},
    "Ritual Slaughter": {"he": "שחיטה", "en_url": "https://en.wikipedia.org/wiki/Shechita", "he_url": "https://he.wikipedia.org/wiki/שחיטה"},
    "Blood/Fat/Meat Prohibitions": {"he": "איסורי אכילה (דם וחֵלֶב)", "en_url": "https://en.wikipedia.org/wiki/Kashrut", "he_url": "https://he.wikipedia.org/wiki/כשרות"},
    "Firstborn (animal/human)": {"he": "בכור ופדיון הבן", "en_url": "https://en.wikipedia.org/wiki/Pidyon_haben", "he_url": "https://he.wikipedia.org/wiki/פדיון_הבן"},
    "Orlah": {"he": "עורלה", "en_url": "https://en.wikipedia.org/wiki/Orlah", "he_url": "https://he.wikipedia.org/wiki/עורלה"},
    "Marriage/Kiddushin": {"he": "קידושין ונישואין", "en_url": "https://en.wikipedia.org/wiki/Jewish_wedding", "he_url": "https://he.wikipedia.org/wiki/קידושין"},
    "Vows": {"he": "נדר (יהדות)", "en_url": "https://en.wikipedia.org/wiki/Neder", "he_url": "https://he.wikipedia.org/wiki/נדר_(יהדות)"},
    "Nazirite": {"he": "נזיר", "en_url": "https://en.wikipedia.org/wiki/Nazirite", "he_url": "https://he.wikipedia.org/wiki/נזיר_(יהדות)"},
    "Sotah ordeal": {"he": "סוטה", "en_url": "https://en.wikipedia.org/wiki/Sotah", "he_url": "https://he.wikipedia.org/wiki/סוטה"},
    "Divorce": {"he": "גירושין (גט)", "en_url": "https://en.wikipedia.org/wiki/Get_(divorce_document)", "he_url": "https://he.wikipedia.org/wiki/גט"},
    "Levirate/Yibbum-Chalitzah": {"he": "ייבום וחליצה", "en_url": "https://en.wikipedia.org/wiki/Yibbum", "he_url": "https://he.wikipedia.org/wiki/ייבום"},
    "Niddah": {"he": "נידה", "en_url": "https://en.wikipedia.org/wiki/Niddah", "he_url": "https://he.wikipedia.org/wiki/נידה"},
    "Torts/Damages": {"he": "נזיקין", "en_url": "https://en.wikipedia.org/wiki/Nezikin", "he_url": "https://he.wikipedia.org/wiki/נזיקין"},
    "Commerce/Loans/Deposits": {"he": "איסור ריבית (הלכה)", "en_url": "https://en.wikipedia.org/wiki/Loans_and_interest_in_Judaism", "he_url": "https://he.wikipedia.org/wiki/איסור_ריבית_(הלכה)"},
    "Real Estate/Partnerships/Inheritance": {"he": "ירושה (משפט עברי)", "en_url": "https://en.wikipedia.org/wiki/Inheritance#Jewish_laws", "he_url": "https://he.wikipedia.org/wiki/ירושה_(משפט_עברי)"},
    "Courts/Testimony/Penalties": {"he": "סנהדרין ודיני ראיות", "en_url": "https://en.wikipedia.org/wiki/Sanhedrin", "he_url": "https://he.wikipedia.org/wiki/סנהדרין"},
    "Offerings (animal/meal)": {"he": "קורבנות", "en_url": "https://en.wikipedia.org/wiki/Korban", "he_url": "https://he.wikipedia.org/wiki/קורבן"},
    "Temple Daily Service/Structure": {"he": "בית המקדש ועבודת המקדש", "en_url": "https://en.wikipedia.org/wiki/Temple_in_Jerusalem", "he_url": "https://he.wikipedia.org/wiki/בית_המקדש"},
    "Bird Offerings/Nest Cases": {"he": "קורבן עוף וקינים", "en_url": "https://en.wikipedia.org/wiki/Kinnim", "he_url": "https://he.wikipedia.org/wiki/קורבן_עוף"},
    "Purity/Impurity Systems": {"he": "טומאה וטהרה", "en_url": "https://en.wikipedia.org/wiki/Tumah_and_taharah", "he_url": "https://he.wikipedia.org/wiki/טומאה_וטהרה"},
    "Peah/Leket/Shikhechah": {"he": "פאת השדה", "en_url": "https://en.wikipedia.org/wiki/Pe%27ah", "he_url": "https://he.wikipedia.org/wiki/פאת_השדה"},
    "Terumah/Ma'aser": {"he": "תרומה ומעשר", "en_url": "https://en.wikipedia.org/wiki/Special:Search?search=Terumah+Maaser", "he_url": "https://he.wikipedia.org/wiki/תרומות_ומעשרות"},
    "Shemitah/Yovel": {"he": "שמיטה ויובל", "en_url": "https://en.wikipedia.org/wiki/Shmita", "he_url": "https://he.wikipedia.org/wiki/שמיטה"},
    "Kilayim": {"he": "כלאיים", "en_url": "https://en.wikipedia.org/wiki/Kil%27ayim", "he_url": "https://he.wikipedia.org/wiki/כלאיים"},
    "Challah": {"he": "הפרשת חלה", "en_url": "https://en.wikipedia.org/wiki/Challah", "he_url": "https://he.wikipedia.org/wiki/הפרשת_חלה"},
    "Bikkurim": {"he": "ביכורים", "en_url": "https://en.wikipedia.org/wiki/Bikkurim", "he_url": "https://he.wikipedia.org/wiki/ביכורים"},
}


def load_rows() -> dict[str, dict[str, str]]:
    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return {row["Subtopic"]: row for row in reader}


def build_subtopic_wiki_links() -> dict[str, dict[str, str]]:
    links: dict[str, dict[str, str]] = {}
    for subtopic, meta in SUBTOPIC_WIKI.items():
        links[subtopic] = {
            "he_term": meta["he"],
            "en_url": meta["en_url"],
            "he_url": meta["he_url"],
        }
    return links


def split_parts(value: str) -> list[str]:
    return [p.strip() for p in value.split(";") if p.strip()]


def strip_parenthetical(text: str) -> str:
    return re.sub(r"\s*\([^)]*\)\s*$", "", text).strip()


def sefaria_ref_url(path: str) -> str:
    return f"https://www.sefaria.org/{quote(path, safe='._,-')}"


def sefaria_search_url(query: str) -> str:
    return f"https://www.sefaria.org/search?q={quote_plus(query)}&tab=text"


def sefaria_il_ref_url(path: str) -> str:
    return f"https://www.sefaria.org.il/{quote(path, safe='._,-')}"


def normalize_mt_key(text: str) -> str:
    s = text.lower()
    s = s.replace("'", "").replace("’", "")
    s = s.replace("-", " ").replace("/", " ")
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


# Maps common transliterated Hilkhot names to Sefaria's English Mishneh Torah title slugs.
MT_TITLE_MAP = {
    "kriat shema": "Reading_the_Shema",
    "tefillah u virkat kohanim": "Prayer_and_the_Priestly_Blessing",
    "tefillin umezuzah vesefer torah": "Tefillin_Mezuzah_and_the_Torah_Scroll",
    "tzitzit": "Fringes",
    "berakhot": "Blessings",
    "shabbat": "Sabbath",
    "eruvin": "Eruvin",
    "chametz u matzah": "Leavened_and_Unleavened_Bread",
    "korban pesach": "Paschal_Offering",
    "yom tov": "Rest_on_a_Holiday",
    "shofar sukkah velulav": "Shofar_Sukkah_and_Lulav",
    "shevitat asor": "Rest_on_the_Tenth_of_Tishrei",
    "taaniyot": "Fasts",
    "megillah vechanukah": "Scroll_of_Esther_and_Hanukkah",
    "maakhalot asurot": "Forbidden_Foods",
    "shechitah": "Ritual_Slaughter",
    "issurei biah": "Forbidden_Intercourse",
    "bekhorot": "Firstlings",
    "maaser sheni veneta revai": "Second_Tithe_and_Fourth_Year_Fruit",
    "matanot aniyim": "Gifts_to_the_Poor",
    "terumot": "Heave_Offerings",
    "maaser": "Tithes",
    "shemitah veyovel": "Sabbatical_and_Jubilee_Years",
    "kilayim": "Diverse_Kinds",
    "bikkurim": "First_Fruits_and_other_Gifts_to_Priests_outside_the_Sanctuary",
    "ishut": "Marriage",
    "sotah": "Sotah",
    "gerushin": "Divorce",
    "yibbum vachalitzah": "Levirate_Marriage_and_Halitza",
    "nedarim": "Vows",
    "shevuot": "Oaths",
    "nezirut": "Nazirite_Vows",
    "nizkei mamon": "Damages_to_Property",
    "genevah": "Theft",
    "gezelah vaavedah": "Robbery_and_Lost_Property",
    "temidin umusafin": "Daily_Offerings_and_Additional_Offerings",
    "beit habechirah": "The_Chosen_House",
}


def bible_part_url(part: str) -> str:
    core = strip_parenthetical(part)
    m = re.match(r"^([A-Za-z]+)\s+(.+)$", core)
    if not m:
        return sefaria_search_url(core)
    abbr, ref = m.group(1), m.group(2).strip()
    book = BOOK_MAP.get(abbr)
    if not book:
        return sefaria_search_url(core)

    if re.fullmatch(r"\d+:\d+-\d+:\d+", ref):
        c1, v1, c2, v2 = re.match(r"(\d+):(\d+)-(\d+):(\d+)", ref).groups()
        return sefaria_ref_url(f"{book}.{c1}.{v1}-{c2}.{v2}")
    if re.fullmatch(r"\d+:\d+-\d+", ref):
        c, v1, v2 = re.match(r"(\d+):(\d+)-(\d+)", ref).groups()
        return sefaria_ref_url(f"{book}.{c}.{v1}-{c}.{v2}")
    if re.fullmatch(r"\d+-\d+", ref):
        c1, c2 = re.match(r"(\d+)-(\d+)", ref).groups()
        return sefaria_ref_url(f"{book}.{c1}-{c2}")
    if re.fullmatch(r"\d+:\d+", ref):
        c, v = re.match(r"(\d+):(\d+)", ref).groups()
        return sefaria_ref_url(f"{book}.{c}.{v}")
    if re.fullmatch(r"\d+", ref):
        return sefaria_ref_url(f"{book}.{ref}")

    return sefaria_search_url(core)


def mishnah_part_url(part: str) -> str:
    core = strip_parenthetical(part)
    m = re.match(r"^([A-Za-z' ]+?)\s+(\d+(?:-\d+)?)$", core)
    if not m:
        return sefaria_search_url(f"Mishnah {core}")
    tractate = m.group(1).strip().replace(" ", "_")
    chapter_rng = m.group(2)
    return sefaria_ref_url(f"Mishnah_{tractate}.{chapter_rng}")


def mt_part_url(part: str) -> str:
    core = strip_parenthetical(part)
    if "selected hilkhot" in core.lower() or "relevant hilkhot" in core.lower():
        return sefaria_search_url(f"Mishneh Torah {core}")

    # Handle values like "Sefer Ahavah: Hilkhot Kri'at Shema" by extracting the Hilkhot title.
    if ":" in core:
        core = core.split(":", 1)[1].strip()
    core = re.sub(r"^Hilkhot\s+", "", core, flags=re.IGNORECASE).strip()

    key = normalize_mt_key(core)
    slug = MT_TITLE_MAP.get(key)
    if slug:
        return sefaria_il_ref_url(f"Mishneh_Torah,_{slug}.1.1")

    # Best-effort direct link formula for unmapped entries.
    if key and not key.startswith("sefer "):
        generic_slug = "_".join(w.capitalize() for w in key.split())
        return sefaria_il_ref_url(f"Mishneh_Torah,_{generic_slug}.1.1")

    return sefaria_search_url(f"Mishneh Torah {core}")


def sa_part_url(part: str) -> str:
    core = strip_parenthetical(part)
    m = re.match(
        r"^(Orach Chayim|Yoreh De'ah|Even HaEzer|Choshen Mishpat)\s+(\d+)(?:-(\d+))?$",
        core,
    )
    if not m:
        return sefaria_search_url(f"Shulchan Aruch {core}")

    section = m.group(1).replace(" ", "_")
    start = m.group(2)
    end = m.group(3)
    ref = f"{start}-{end}" if end else start
    return sefaria_ref_url(f"Shulchan_Arukh,_{section}.{ref}")


def linked_parts(value: str, source_type: str) -> str:
    if value.startswith("(") and "no dedicated practical section" in value:
        return f"<span class='plain'>{html.escape(value)}</span>"

    parts = split_parts(value)
    rendered = []
    for p in parts:
        if source_type == "bible":
            url = bible_part_url(p)
        elif source_type == "mishnah":
            url = mishnah_part_url(p)
        elif source_type == "mt":
            url = mt_part_url(p)
        else:
            url = sa_part_url(p)
        rendered.append(
            f"<a href='{html.escape(url)}' target='_blank' rel='noopener noreferrer'>{html.escape(p)}</a>"
        )
    return "<span class='sep'>; </span>".join(rendered)


def subtopic_heading_html(subtopic: str, wiki_links: dict[str, dict[str, str]]) -> str:
    info = wiki_links.get(subtopic)
    if not info:
        return html.escape(subtopic)
    he_display = re.sub(r"\s*\([^)]*\)\s*$", "", info["he_term"]).strip()
    return (
        f"<a href='{html.escape(info['en_url'])}' target='_blank' rel='noopener noreferrer'>"
        f"{html.escape(subtopic)}</a> "
        f"(<a href='{html.escape(info['he_url'])}' target='_blank' rel='noopener noreferrer' "
        f"lang='he' dir='rtl'>{html.escape(he_display)}</a>)"
    )


def build_html(rows: dict[str, dict[str, str]], wiki_links: dict[str, dict[str, str]]) -> str:
    topic_html = []
    topic_index = 0
    for topic, subtopics in CATEGORIES:
        topic_index += 1
        blocks = []
        for subtopic in subtopics:
            row = rows[subtopic]
            blocks.append(
                f"""
                <article class="subtopic">
                  <h3>{subtopic_heading_html(subtopic, wiki_links)}</h3>
                  <div class="citations">
                    <div class="col">
                      <div class="label">Bible</div>
                      <div class="content">{linked_parts(row["Bible range"], "bible")}</div>
                    </div>
                    <div class="col">
                      <div class="label">Mishnah</div>
                      <div class="content">{linked_parts(row["Mishnah range"], "mishnah")}</div>
                    </div>
                    <div class="col">
                      <div class="label">Mishneh Torah</div>
                      <div class="content">{linked_parts(row["Mishneh Torah unit"], "mt")}</div>
                    </div>
                    <div class="col">
                      <div class="label">Shulchan Aruch</div>
                      <div class="content">{linked_parts(row["Shulchan Aruch simanim"], "sa")}</div>
                    </div>
                  </div>
                </article>
                """
            )
        topic_html.append(
            f"""
            <section class="topic" id="topic-{topic_index}">
              <h2>{html.escape(topic)}</h2>
              <div class="topic-branch">
                {''.join(blocks)}
              </div>
            </section>
            """
        )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Comparative Hierarchical Topic Tree (Citation-Granular)</title>
  <style>
    :root {{
      --bg: #f5f6f8;
      --card: #ffffff;
      --ink: #1d2430;
      --muted: #5a6576;
      --line: #c9d1db;
      --accent: #2f3d4a;
      --shadow: 0 8px 24px rgba(18, 24, 33, 0.08);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Segoe UI", "Noto Sans", Arial, sans-serif;
      background: linear-gradient(180deg, #f8fafc 0%, var(--bg) 100%);
      color: var(--ink);
      line-height: 1.45;
    }}
    .wrap {{
      max-width: 1400px;
      margin: 0 auto;
      padding: 24px 18px 48px;
    }}
    header {{
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 18px 20px;
      box-shadow: var(--shadow);
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: clamp(1.25rem, 2.8vw, 2rem);
      line-height: 1.25;
    }}
    .meta {{
      color: var(--muted);
      font-size: 0.95rem;
      margin: 0;
    }}
    .root {{
      margin: 20px auto 8px;
      width: fit-content;
      padding: 10px 18px;
      background: var(--accent);
      color: #fff;
      border-radius: 10px;
      font-weight: 700;
      box-shadow: var(--shadow);
    }}
    .tree {{
      margin-top: 16px;
      border-left: 3px solid var(--line);
      padding-left: 20px;
      position: relative;
    }}
    .topic {{
      position: relative;
      margin: 18px 0 28px;
      padding-left: 12px;
    }}
    .topic::before {{
      content: "";
      position: absolute;
      left: -23px;
      top: 22px;
      width: 18px;
      border-top: 2px solid var(--line);
    }}
    .topic h2 {{
      margin: 0 0 12px;
      display: inline-block;
      background: #eaf0f7;
      border: 1px solid #b9c8d8;
      border-radius: 10px;
      padding: 8px 12px;
      font-size: 1.05rem;
    }}
    .topic-branch {{
      border-left: 2px dashed #d7dee7;
      margin-left: 8px;
      padding-left: 14px;
    }}
    .subtopic {{
      position: relative;
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 12px;
      box-shadow: var(--shadow);
      padding: 14px;
      margin: 12px 0;
    }}
    .subtopic::before {{
      content: "";
      position: absolute;
      left: -16px;
      top: 22px;
      width: 14px;
      border-top: 2px solid #d5dde6;
    }}
    .subtopic h3 {{
      margin: 0 0 10px;
      font-size: 1rem;
      color: #213042;
    }}
    .citations {{
      display: grid;
      grid-template-columns: repeat(4, minmax(180px, 1fr));
      gap: 10px;
    }}
    .col {{
      border: 1px solid #d9e0e9;
      border-radius: 10px;
      padding: 10px;
      background: #fcfdff;
      min-height: 100%;
    }}
    .label {{
      font-weight: 700;
      margin-bottom: 6px;
      color: #2b3e54;
      font-size: 0.92rem;
      letter-spacing: 0.01em;
    }}
    .content {{
      font-size: 0.9rem;
      color: #233042;
      word-break: break-word;
    }}
    a {{
      color: #124f96;
      text-decoration-thickness: 1px;
      text-underline-offset: 2px;
    }}
    a:hover {{
      color: #0d3562;
      text-decoration-thickness: 2px;
    }}
    .sep {{
      color: #6f7c8d;
    }}
    .plain {{
      color: #5f6c7d;
      font-style: italic;
    }}
    .subtopic h3 a {{
      color: #123d72;
    }}
    .subtopic h3 a[lang="he"] {{
      color: #2e4b20;
      font-weight: 600;
    }}
    .foot {{
      margin-top: 18px;
      color: #536276;
      font-size: 0.88rem;
      background: #fff;
      border: 1px solid var(--line);
      border-radius: 10px;
      padding: 10px 12px;
    }}
    @media (max-width: 1200px) {{
      .citations {{ grid-template-columns: repeat(2, minmax(200px, 1fr)); }}
    }}
    @media (max-width: 760px) {{
      .citations {{ grid-template-columns: 1fr; }}
      .tree {{ padding-left: 12px; }}
      .topic::before {{ left: -15px; width: 10px; }}
      .subtopic::before {{ left: -12px; width: 8px; }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <header>
      <h1>Comparative Hierarchical Topic Tree (Citation-Granular): Bible, Mishnah, Mishneh Torah, Shulchan Aruch</h1>
      <p class="meta">Vertical hierarchy with full citation detail. Each citation token links to Sefaria (direct ref when parseable, otherwise Sefaria search query fallback).</p>
    </header>
    <div class="root">Torah / Jewish Knowledge Corpus</div>
    <main class="tree">
      {''.join(topic_html)}
    </main>
    <div class="foot">
      Generated from <code>comparative_topic_matrix_with_subtopic.csv</code>. Notes like “selected” or “no full practical code parallel” are preserved verbatim.
    </div>
  </div>
</body>
</html>
"""


def main() -> None:
    rows = load_rows()
    wiki_links = build_subtopic_wiki_links()
    for _, subtopics in CATEGORIES:
        for subtopic in subtopics:
            if subtopic not in rows:
                raise ValueError(f"Missing subtopic in CSV: {subtopic}")
            if subtopic not in wiki_links:
                raise ValueError(f"Missing wiki metadata for subtopic: {subtopic}")

    html_doc = build_html(rows, wiki_links)
    HTML_OUT.write_text(html_doc, encoding="utf-8")
    print(f"Wrote: {HTML_OUT}")


if __name__ == "__main__":
    main()
