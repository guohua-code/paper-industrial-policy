# 第六批专精特新“小巨人”省级名单采集规范（子代理必读）

## 背景
为论文采集工信部 **第六批**（2024 年 8–9 月公示，全国新增约 3012 家）专精特新“小巨人”企业的**省级公示名单**。计划单列市（深圳、宁波、青岛、大连、厦门）部分省份单独推荐，需注意口径。

## 目标
为分配给你的每个省份，找到**官方或可信转载的完整名单附件**（PDF / Excel / docx 均可），下载并标准化。

## 采集步骤（已在本机验证可行）
1. 用必应搜索（终端直连可用）：
   ```
   curl -sL -m 25 "https://cn.bing.com/search?q=<URL编码的查询词>" \
     -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/120 Safari/537.36"
   ```
   查询词示例：`山东省 第六批 专精特新小巨人 名单 公示 附件 pdf`
   从返回 HTML 中提取 `.b_algo h2 a` 的链接。多翻几页/换关键词（加“工信厅”“完整名单”“xlsx”等）。
2. 优先来源：省工信厅/经信厅官网附件 > 政府/事业单位平台镜像 > 行业协会转载 > 媒体全文。名单附件常为 `.pdf/.xls/.xlsx/.docx`。
3. 下载：
   ```
   curl -sL -m 120 "<附件URL>" -H "User-Agent: Mozilla/5.0 ..." -H "Referer: <来源页>" -o <文件>
   ```
   用 `file <文件>` 确认是真实 PDF/Office 文档（不是 HTML 404 页）。官方附件有时已下架(404)，就换镜像。
4. 解析校验：
   - PDF：`uv run --python 3.12 --with pdfplumber python ...`，逐页 `extract_tables()`。
   - xlsx：`uv run --python 3.12 --with openpyxl`；docx：`--with python-docx`。
   - 名单表格通常是【序号/省(区、市)/企业名称】三列，或【省/企业名称】两列。
   - **必须核对家数**：序号连续、去重后家数与公开报道一致；检查是否遗漏计划单列市（用企业名中的城市名统计，如深圳/青岛/宁波/大连/厦门）。

## 输出（务必严格遵守）
对每个省份 pinyin（如 shandong）：
- 原始文件存到：
  `data/raw/little_giant/2024_batch6_provincial/<pinyin>/`（可多个附件 + 一个 `SOURCE.md` 记录来源URL、标题、采集日期、家数校验结论、口径说明）
- 标准化 CSV 存到：
  `data/interim/little_giant_batch6/<pinyin>_new.csv`（第六批**新增**）
  如有复核通过名单另存 `<pinyin>_review.csv`。
- CSV 必须是 **UTF-8-SIG**，表头固定为：
  `province,batch,list_type,sequence_in_source,company_name,source_file`
  - province：中文省名（如“山东省”）；深圳等单列市也填所属省（“广东省”），但在 SOURCE.md 注明
  - batch：`第六批`
  - list_type：`new` 或 `review_passed`
  - sequence_in_source：原表序号（两列无序号则按顺序编号）
  - company_name：企业全称，去掉换行/多余空格，保留全角括号原样
  - source_file：原始文件名
- 只采集，**不要运行 git，不要运行匹配脚本，不要改其他文件**。

## 返回给调度者
每个省份报告：省名 | 新增家数 | 复核家数 | 是否含单列市 | CSV路径 | 来源URL | 可信度(官方/镜像/媒体) | 遗留问题。
拿不到完整名单的省也要明确说明卡在哪，不要编造企业名。
