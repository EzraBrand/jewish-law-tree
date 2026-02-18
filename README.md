# Jewish Law Tree

This project maps major areas of Jewish law across four core texts:
- Bible (Tanakh/Torah law passages)
- Mishnah
- Mishneh Torah (Rambam)
- Shulchan Aruch

The goal is simple: help readers see how the same legal topics appear in different layers of the Jewish legal tradition, and support study of the history of halacha.

## What You Can Browse
- `index.html` (live page): a vertical topic tree with full citation detail.
- `high_level_relationship_chart.html`: a high-level line chart showing flow across Pentateuch, Mishnah, Mishneh Torah, and Shulchan Aruch.
- Each citation is linked to Sefaria.
- Each subtopic header is linked to a relevant Wikipedia page in English and Hebrew.
- Hebrew labels are shown cleanly (without parenthetical metadata in the visible text).

Live site:
- `https://ezrabrand.github.io/jewish-law-tree/`

## Data Files
- `comparative_topic_matrix.csv`: base comparison table (4 columns).
- `comparative_topic_matrix_with_subtopic.csv`: same data, plus a `Subtopic` column.

## Technical Appendix
- `render_comparative_tree_html.py` builds the main HTML page from CSV data.
- `render_comparative_tree.py` builds static image versions (`.png`, `.svg`).
- `index.html` is the GitHub Pages entrypoint.
- GitHub Actions deploys updates from `main` to the live Pages site.

To regenerate locally:

```bash
python render_comparative_tree.py
python render_comparative_tree_html.py
```

Image, based on this data: 

![BRAND - Hierarchical Topic Tree of Jewish Law - v1 - 18-Feb-2026](https://github.com/user-attachments/assets/9b0bbfb8-5a45-4c25-9621-41f350e754f5)

Also uploaded here, as a PDF: [Comparative Hierarchical Topic Tree of Jewish Law: Bible, Mishnah, Mishneh Torah, Shulchan Aruch](https://www.academia.edu/164739079/Comparative_Hierarchical_Topic_Tree_of_Jewish_Law_Bible_Mishnah_Mishneh_Torah_Shulchan_Aruch)

