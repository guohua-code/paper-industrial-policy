## 分析脚本

按编号顺序运行，下游脚本只读取上游的产出，不反向依赖：

- `01_clean/`：把 `data/raw/` 清洗为 `data/interim/`。
- `02_build/`：变量构造、样本合并，产出 `data/processed/`。
- `03_analysis/`：描述统计、基准回归、异质性、稳健性，
  产出写入 `results/tables/` 和 `results/figures/`。

命名规则：两位数字开头，例如 `01_clean/01_drop_missing.do`。
整体重跑使用 `bash analysis/run_all.sh`，脚本会按编号顺序执行各目录下的 `.R` 文件。

约定：

- 脚本路径全部相对仓库根目录，不依赖个人机器上的绝对路径；
  在脚本开头用 `here::here()` 定位路径，不要写 `setwd("C:/...")`。
- 所有随机化步骤固定随机种子。
- 输出文件由脚本生成，不手工改动 `results/` 里的内容。
- 不要在脚本里 `install.packages()`，依赖统一通过 `dependencies.R` 和 renv 管理。
