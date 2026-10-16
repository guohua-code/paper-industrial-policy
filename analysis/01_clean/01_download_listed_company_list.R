# 下载并整理沪深 A 股上市公司基础清单（公开交易所数据）。
#
# 数据用途：
# - 为专精特新“小巨人”官方名单匹配证券代码；
# - 提供公司全称、简称、上市日期、注册地区和行业等基础字段；
# - 不替代 CSMAR/Wind/CNRDS 等商业数据库，正式实证前仍需补充统一社会信用代码、
#   曾用名、退市状态和财务变量。

source(here::here("analysis", "dependencies.R"))

raw_sz <- here("data", "raw", "listed_companies", "szse_a_share_2026-10-16.xlsx")
raw_sse_main <- here("data", "raw", "listed_companies", "sse_main_a_2026-10-16.json")
raw_sse_star <- here("data", "raw", "listed_companies", "sse_star_2026-10-16.json")
out_file <- here("data", "interim", "listed_companies_szse_sse.csv")

dir.create(dirname(raw_sz), recursive = TRUE, showWarnings = FALSE)
dir.create(dirname(out_file), recursive = TRUE, showWarnings = FALSE)

## 1. 深交所 A 股列表 -------------------------------------------------

szse_url <- paste0(
  "https://www.szse.cn/api/report/ShowReport?",
  "SHOWTYPE=xlsx&CATALOGID=1110&TABKEY=tab1"
)

download.file(szse_url, raw_sz, mode = "wb", quiet = TRUE)

sz <- read_excel(raw_sz, sheet = "A股列表") |>
  transmute(
    exchange = "SZSE",
    market_board = `板块`,
    stock_code = `A股代码`,
    stock_name = str_squish(`A股简称`),
    company_full_name = str_squish(`公司全称`),
    company_name_en = `英文名称`,
    list_date = as.character(`A股上市日期`),
    delist_date = NA_character_,
    registered_address = str_squish(`注册地址`),
    province = str_squish(`省    份`),
    city = str_squish(`城     市`),
    industry_name = str_squish(`所属行业`),
    csrc_industry_code = NA_character_,
    company_status = "listed",
    source = "SZSE ShowReport A股列表",
    source_file = basename(raw_sz)
  )

## 2. 上交所主板与科创板列表 -----------------------------------------

sse_query_url <- "https://query.sse.com.cn/sseQuery/commonQuery.do"

download_sse_json <- function(stock_type, path) {
  params <- list(
    STOCK_TYPE = stock_type,
    REG_PROVINCE = "",
    CSRC_CODE = "",
    STOCK_CODE = "",
    sqlId = "COMMON_SSE_CP_GPJCTPZ_GPLB_GP_L",
    COMPANY_STATUS = "2,4,5,7,8",
    type = "inParams",
    isPagination = "true",
    `pageHelp.cacheSize` = 1,
    `pageHelp.beginPage` = 1,
    `pageHelp.pageSize` = 10000,
    `pageHelp.pageNo` = 1
  )

  response <- GET(
    sse_query_url,
    query = params,
    add_headers(
      `User-Agent` = "Mozilla/5.0",
      Referer = "https://www.sse.com.cn/assortment/stock/list/share/"
    )
  )

  stop_for_status(response)
  writeBin(content(response, as = "raw"), path)
  jsonlite::fromJSON(content(response, as = "text", encoding = "UTF-8"))
}

parse_sse <- function(json, board_name, raw_file) {
  as_tibble(json$pageHelp$data) |>
    transmute(
      exchange = "SSE",
      market_board = board_name,
      stock_code = A_STOCK_CODE,
      stock_name = str_squish(SEC_NAME_CN),
      company_full_name = str_squish(FULL_NAME),
      company_name_en = FULL_NAME_IN_ENGLISH,
      list_date = LIST_DATE,
      delist_date = if_else(DELIST_DATE == "-", NA_character_, DELIST_DATE),
      registered_address = NA_character_,
      province = str_squish(AREA_NAME_DESC),
      city = NA_character_,
      industry_name = str_squish(CSRC_CODE_DESC),
      csrc_industry_code = CSRC_CODE,
      company_status = as.character(PRODUCT_STATUS %||% "listed"),
      source = "SSE commonQuery COMMON_SSE_CP_GPJCTPZ_GPLB_GP_L",
      source_file = basename(raw_file)
    )
}

sse_main_json <- download_sse_json("1", raw_sse_main)
sse_star_json <- download_sse_json("8", raw_sse_star)

sse_main <- parse_sse(sse_main_json, "主板", raw_sse_main)
sse_star <- parse_sse(sse_star_json, "科创板", raw_sse_star)

## 3. 合并与基础校验 -------------------------------------------------

listed <- bind_rows(sz, sse_main, sse_star) |>
  mutate(
    stock_code = str_pad(stock_code, width = 6, side = "left", pad = "0"),
    list_date = format(parse_date_time(list_date, orders = c("%Y-%m-%d", "%Y%m%d")), "%Y-%m-%d"),
    delist_date = if_else(
      grepl("^\\d{8}$", delist_date),
      format(parse_date_time(delist_date, orders = "%Y%m%d"), "%Y-%m-%d"),
      delist_date
    ),
    exchange_code = paste0(exchange, "_", stock_code)
  ) |>
  relocate(exchange_code, .before = exchange)

if (anyDuplicated(listed$stock_code)) {
  warning("存在重复 6 位证券代码，请检查沪深代码或北交所缺失。")
}

write_csv(listed, out_file, na = "")

cat("已生成上市公司基础表：", nrow(listed), "行\n")
print(count(listed, exchange, market_board, sort = TRUE))

stopifnot(
  nrow(sz) > 2500,
  nrow(sse_main) > 1500,
  nrow(sse_star) > 500,
  nrow(listed) > 4500
)
