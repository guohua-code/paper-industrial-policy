# 产业经济政策论文

实证研究项目仓库。目标是保证从原始数据到论文表格、图形的全流程可复现。

## 研究问题

待补充（一句话说明研究的政策背景、识别对象和核心因果问题）。

## 目录结构

| 目录 | 用途 |
| --- | --- |
| `data/raw/` | 原始数据，只读，不手工修改，不入库 |
| `data/interim/` | 清洗过程中的中间数据 |
| `data/processed/` | 供回归分析直接使用的最终数据 |
| `analysis/01_clean/` | 原始数据清洗脚本 |
| `analysis/02_build/` | 变量构造、样本合并脚本 |
| `analysis/03_analysis/` | 描述统计、回归、稳健性检验脚本 |
| `results/figures/`、`results/tables/` | 脚本生成的图形与表格，不手工编辑 |
| `manuscripts/` | 论文草稿 |
| `references/` | 参考文献库（BibTeX） |
| `notes/` | 研究笔记与决策日志 |

## 数据

数据文件不纳入 Git。数据来源、获取方式、版本与校验值记录在
[data/README.md](data/README.md)，按说明下载后放入对应目录即可复原。

## 复现流程

1. 配置环境（见下）。
2. 按 `data/README.md` 获取原始数据，放入 `data/raw/`。
3. 按编号顺序运行 `analysis/` 下的脚本：

```bash
bash analysis/run_all.sh
```

生成的表格和图形输出到 `results/`，论文中只引用这些产出文件。

## 计算环境

待补充：使用的软件及版本（如 Stata 18 / R 4.4 / Python 3.12），
以及依赖锁定文件（`requirements.txt`、`renv.lock` 或 Stata 包清单）。

## 写作与引用

参考文献统一维护在 `references/refs.bib`。草稿目前用 Markdown，
后续如转向 LaTeX/Quarto，编译方式在此说明。
