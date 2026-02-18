# Jewish Law Tree

Citation-granular comparative mapping across:
- Bible
- Mishnah
- Mishneh Torah
- Shulchan Aruch

The project provides a strict CSV matrix and generated visualizations (static image + full HTML hierarchy with Sefaria links).

## Files
- `comparative_topic_matrix.csv`
  - Strict 4-column matrix:
    - `Bible range`
    - `Mishnah range`
    - `Mishneh Torah unit`
    - `Shulchan Aruch simanim`
- `comparative_topic_matrix_with_subtopic.csv`
  - Same matrix with added `Subtopic` column for sorting/filtering.
- `render_comparative_tree.py`
  - Generates vertical static outputs:
    - `comparative_topic_tree_vertical.png`
    - `comparative_topic_tree_vertical.svg`
- `render_comparative_tree_html.py`
  - Generates:
    - `comparative_topic_tree_hyperlinked.html`
  - HTML is full-detail, vertical hierarchy, and hyperlinks citations to Sefaria.

## Generate Outputs
Run from repo root:

```bash
python render_comparative_tree.py
python render_comparative_tree_html.py
```

## GitHub Pages
- Site URL: `https://ezrabrand.github.io/jewish-law-tree/`
- Main page: `index.html` (same content as `comparative_topic_tree_hyperlinked.html`)

## Notes
- Mishneh Torah links in HTML use direct Sefaria URL format when mapped (example style: `Mishneh_Torah,_Foundations_of_the_Torah.1.1`), with fallback behavior for ambiguous entries.
- Some Shulchan Aruch / Mishneh Torah entries are intentionally marked as partial or non-practical parallels where relevant.

Image, based on this data: 

![BRAND - Hierarchical Topic Tree of Jewish Law - v1 - 18-Feb-2026](https://github.com/user-attachments/assets/9b0bbfb8-5a45-4c25-9621-41f350e754f5)

Also uploaded here, as a PDF: [Comparative Hierarchical Topic Tree of Jewish Law: Bible, Mishnah, Mishneh Torah, Shulchan Aruch](https://www.academia.edu/164739079/Comparative_Hierarchical_Topic_Tree_of_Jewish_Law_Bible_Mishnah_Mishneh_Torah_Shulchan_Aruch)

