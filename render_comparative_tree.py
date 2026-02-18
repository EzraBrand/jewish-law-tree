import csv
from pathlib import Path
from textwrap import fill

import matplotlib.pyplot as plt


CSV_PATH = Path("comparative_topic_matrix_with_subtopic.csv")
PNG_OUT = Path("comparative_topic_tree_vertical.png")
SVG_OUT = Path("comparative_topic_tree_vertical.svg")


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


def load_rows(path: Path) -> dict[str, dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return {row["Subtopic"]: row for row in reader}


def box_text(label: str, value: str, width: int = 52) -> str:
    return f"{label}: {fill(value, width=width)}"


def main() -> None:
    rows = load_rows(CSV_PATH)

    for _, subtopics in CATEGORIES:
        for s in subtopics:
            if s not in rows:
                raise ValueError(f"Missing subtopic in CSV: {s}")

    subtopic_count = sum(len(s) for _, s in CATEGORIES)
    total_height = 10 + subtopic_count * 4.2

    fig, ax = plt.subplots(figsize=(26, max(28, total_height * 0.24)))
    ax.set_xlim(0, 26)
    ax.set_ylim(0, total_height)
    ax.axis("off")

    # x positions for each hierarchy level
    x_root = 2.4
    x_topic = 6.0
    x_sub = 10.8
    x_leaf = 17.2

    y = total_height - 4.0
    root_y = y

    ax.text(
        x_root,
        root_y,
        "Torah / Jewish Knowledge Corpus",
        ha="center",
        va="center",
        fontsize=14,
        fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.35", fc="#2f3d4a", ec="#1f2a33", lw=1.2, alpha=0.97),
        color="white",
    )

    topic_nodes = []
    y -= 5.0

    for topic, subtopics in CATEGORIES:
        topic_y = y
        topic_nodes.append((topic, topic_y, subtopics))

        # root -> topic connector
        ax.plot([x_root + 0.9, x_topic - 1.2], [root_y, topic_y], color="#5a6772", lw=1.0)

        ax.text(
            x_topic,
            topic_y,
            fill(topic, width=34),
            ha="center",
            va="center",
            fontsize=11,
            fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.28", fc="#e9eef3", ec="#9aa7b2", lw=1.0),
        )

        y -= 2.8
        for sub in subtopics:
            row = rows[sub]
            sub_y = y

            # topic -> subtopic connector
            ax.plot([x_topic + 1.5, x_sub - 1.1], [topic_y - 0.15, sub_y], color="#7b8792", lw=0.9)

            ax.text(
                x_sub,
                sub_y,
                fill(sub, width=28),
                ha="center",
                va="center",
                fontsize=9.5,
                bbox=dict(boxstyle="round,pad=0.22", fc="#ffffff", ec="#b3bdc6", lw=0.9),
            )

            leaf_items = [
                ("Bible", row["Bible range"]),
                ("Mishnah", row["Mishnah range"]),
                ("Mishneh Torah", row["Mishneh Torah unit"]),
                ("Shulchan Aruch", row["Shulchan Aruch simanim"]),
            ]

            leaf_offsets = [1.25, 0.4, -0.45, -1.3]
            for (label, value), off in zip(leaf_items, leaf_offsets):
                ly = sub_y + off
                ax.plot([x_sub + 1.7, x_leaf - 1.6], [sub_y, ly], color="#9aa7b2", lw=0.7)
                ax.text(
                    x_leaf,
                    ly,
                    box_text(label, value, width=54),
                    ha="left",
                    va="center",
                    fontsize=8.2,
                    bbox=dict(boxstyle="round,pad=0.20", fc="#fdfdfd", ec="#d1d7dd", lw=0.7),
                )

            y -= 4.0

        y -= 1.3

    fig.suptitle(
        "Comparative Hierarchical Topic Tree (Citation-Granular)\nBible, Mishnah, Mishneh Torah, Shulchan Aruch",
        fontsize=16,
        fontweight="bold",
        y=0.995,
    )

    plt.tight_layout(rect=[0.01, 0.01, 0.995, 0.985])
    fig.savefig(PNG_OUT, dpi=300)
    fig.savefig(SVG_OUT)
    plt.close(fig)

    print(f"Wrote: {PNG_OUT}")
    print(f"Wrote: {SVG_OUT}")


if __name__ == "__main__":
    main()
