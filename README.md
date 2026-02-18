![BRAND - Hierarchical Topic Tree of Jewish Law - v1 - 18-Feb-2026](https://github.com/user-attachments/assets/ead385e3-a607-4a33-9182-23e78deee7d8)# Jewish Law Tree

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

## Notes
- Mishneh Torah links in HTML use direct Sefaria URL format when mapped (example style: `Mishneh_Torah,_Foundations_of_the_Torah.1.1`), with fallback behavior for ambiguous entries.
- Some Shulchan Aruch / Mishneh Torah entries are intentionally marked as partial or non-practical parallels where relevant.






![BRAND - Hierarchical Topic Tree of Jewish Law - v1 - 18-Feb-2026](https://github.com/user-attachments/assets/9b0bbfb8-5a45-4c25-9621-41f350e754f5)

