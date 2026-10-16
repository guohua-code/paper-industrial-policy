# 将专精特新“小巨人”省级名单与沪深 A 股上市公司基础表做名称匹配。
#
# 当前仅做基准口径：上市公司本身直接入选。
# 子公司入选、曾用名匹配和模糊匹配需要另建审计表，不能在本脚本中静默合并。

source(here::here("analysis", "dependencies.R"))

little_giant_file <- here("data", "interim",
                          "little_giant_batch6_beijing.csv")
listed_file <- here("data", "interim",
                    "listed_companies_szse_sse.csv")
out_file <- here("data", "interim",
                 "little_giant_batch6_beijing_matched_listed.csv")

little_giant <- read_csv(little_giant_file, show_col_types = FALSE)
listed <- read_csv(listed_file, show_col_types = FALSE)

clean_company_name <- function(x) {
  x |>
    str_squish() |>
    str_remove_all("\\s+") |>
    str_replace_all("[（]", "(") |>
    str_replace_all("[）]", ")")
}

little_giant <- little_giant |>
  mutate(company_name_clean = clean_company_name(company_name))

listed <- listed |>
  mutate(company_name_clean = clean_company_name(company_full_name))

matched <- little_giant |>
  inner_join(listed, by = "company_name_clean",
             suffix = c("_policy", "_listed"))

write_csv(matched, out_file, na = "")

cat("匹配上市公司数：", nrow(matched), "\n")
print(count(matched, list_type, sort = TRUE))

stopifnot(
  sum(matched$list_type == "new") == 8,
  sum(matched$list_type == "review_passed") == 11
)
