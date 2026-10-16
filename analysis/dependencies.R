# 项目依赖清单
#
# 约定：分析脚本只 library() 本文件中列出的包。
# 需要新增依赖时，先写在这里，安装后运行 renv::snapshot() 更新锁文件。
# 不要在分析脚本里直接 install.packages()。

# 路径与项目结构
library(here)

# 数据读取与处理
library(tidyverse)   # dplyr, tidyr, readr, ggplot2, purrr, stringr 等
library(haven)       # 读取 Stata(.dta)、SPSS(.sav)、SAS 文件
library(readxl)      # 读取 Excel
library(data.table)  # 大数据集快速读写与合并
library(xml2)        # 解析 Word/网页等 XML 结构
library(httr)        # HTTP API 与网页下载

# 计量分析
library(fixest)      # 多期/高维固定效应、聚类稳健标准误
library(lmtest)      # 系数联合检验等
library(sandwich)    # 稳健 / 聚类标准误

# 结果输出
library(modelsummary) # 回归表、描述统计导出（LaTeX/Word/CSV）
