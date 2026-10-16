# 解析专精特新“小巨人”省级公示 Word 附件。
#
# 当前已验证附件格式：
# - 北京市第六批新增企业公示名单：两列表格（序号、企业名称）
# - 北京市第三批复核通过企业公示名单：两列表格（序号、企业名称）
#
# 不同省份的附件可能是 .doc、.docx、.xls、.xlsx 或 PDF，本脚本只处理
# 与北京样本结构一致的 .docx 文件。其他格式应先单独增加解析函数。

source(here::here("analysis", "dependencies.R"))

raw_dir <- here("data", "raw", "little_giant",
                "2024_batch6_provincial", "beijing")
out_file <- here("data", "interim", "little_giant_batch6_beijing.csv")

extract_docx_rows <- function(path) {
  xml_files <- unzip(path, files = "word/document.xml", exdir = tempdir())
  doc <- xml2::read_xml(xml_files)

  rows <- xml2::xml_find_all(doc, ".//w:tr")
  cells <- lapply(rows, function(row) {
    trimws(xml2::xml_text(xml2::xml_find_all(row, ".//w:tc")))
  })

  valid <- vapply(cells, function(x) {
    length(x) >= 2L && grepl("^[0-9]+$", x[[1]]) && nzchar(x[[2]])
  }, logical(1L))

  tibble(
    sequence = as.integer(vapply(cells[valid], `[[`, character(1L), 1L)),
    company_name = vapply(cells[valid], `[[`, character(1L), 2L)
  )
}

parse_beijing_attachment <- function(file_name, batch, list_type) {
  extract_docx_rows(file.path(raw_dir, file_name)) |>
    mutate(
      province = "北京市",
      batch = .env$batch,
      list_type = .env$list_type,
      source_file = file_name,
      .before = 1L
    ) |>
    rename(sequence_in_source = sequence)
}

new_firms <- parse_beijing_attachment(
  "P020240903490003096824.docx",
  "第六批",
  "new"
)

review_firms <- parse_beijing_attachment(
  "P020240903490003421325.docx",
  "第三批复核",
  "review_passed"
)

beijing <- bind_rows(new_firms, review_firms)

dir.create(dirname(out_file), recursive = TRUE, showWarnings = FALSE)
write_csv(beijing, out_file, na = "")

if (anyDuplicated(beijing$company_name)) {
  warning("北京名单中存在重复企业名称，请检查附件。")
}

cat("已解析北京市第六批/第三批复核名单：", nrow(beijing), "行\n")
print(count(beijing, list_type, sort = TRUE))
