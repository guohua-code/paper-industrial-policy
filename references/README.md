## 参考文献

文献库统一维护在 `refs.bib`，正文只引用其中的 BibTeX key。
建议配合 Zotero（Better BibTeX）或直接手工维护，避免多条重复记录。

## 推荐工作流

1. 用 Zotero + Zotero Connector 收集网页和数据库文献。
2. 安装 Better BibTeX，为每篇文献生成稳定的 citation key。
3. 将用于本论文的文献集合导出或自动同步为 `refs.bib`。
4. 在 `lit_matrix.csv` 中为精读文献填写一行，`bib_key` 必须与 `refs.bib` 一致。
5. 综述正文沉淀到 `../manuscripts/literature_review.md`。

## 文献矩阵字段说明

- `relation_to_my_study`：说明该文献与本文的关系，如理论依据、
  假设依据、方法参考、结论对照或边界条件。
- `usable_section`：预计用于引言、理论与假设、研究方法、讨论等哪个部分。
- `relevance_rating`：1-5 分，5 分为必须精读和引用。
- `reading_status`：建议使用 `待读`、`粗读`、`精读`、`已引用`、`排除`。

正式写作前删除 `lit_matrix.csv` 中的示例行；不要引用示例文献。
