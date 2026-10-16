#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
解析第六批专精特新“小巨人”省级公示 PDF（表格列：序号 / 省(区、市) / 企业名称）。

用法:
  uv run --python 3.12 --with pdfplumber python analysis/01_clean/03_parse_provincial_batch6.py \
      --province 江苏省 --batch 第六批 --list-type new \
      --pdf data/raw/little_giant/2024_batch6_provincial/jiangsu/jiangsu_batch6_new_711.pdf \
      --out data/interim/little_giant_batch6/jiangsu_new.csv

输出列: province,batch,list_type,sequence_in_source,company_name,source_file
依赖: pdfplumber
"""
import argparse, csv, os, re, sys

try:
    import pdfplumber
except ImportError:
    sys.exit("缺少 pdfplumber，请用: uv run --python 3.12 --with pdfplumber python ...")


def extract_rows(pdf_path: str):
    """从 PDF 所有表格中提取 (序号, 省份, 企业名称)。

    兼容两种省级附件格式：
      A. 三列：序号 / 省(区、市) / 企业名称（如江苏）
      B. 两列：省(区、市) / 企业名称，无序号（如浙江）
    """
    out = []
    auto_seq = 0
    with pdfplumber.open(pdf_path) as pdf:
        for pageno, page in enumerate(pdf.pages, start=1):
            for table in page.extract_tables():
                for raw in table:
                    cells = [(c or "").replace("\n", "").replace(" ", "").strip()
                             for c in raw]
                    cells = [c for c in cells if c != ""]
                    if not cells:
                        continue
                    # 跳过表头
                    joined = "".join(cells)
                    if "企业名称" in joined or "序号" in joined and len(cells) <= 3:
                        if "企业名称" in joined:
                            continue
                    if len(cells) >= 3 and re.fullmatch(r"\d+", cells[0]):
                        seq, prov, name = int(cells[0]), cells[1], cells[2]
                    elif len(cells) >= 2:
                        # 两列：省份 + 企业名称
                        prov, name = cells[0], cells[1]
                        if not prov.endswith(("省", "市", "自治区")) or not name:
                            continue
                        auto_seq += 1
                        seq = auto_seq
                    else:
                        continue
                    if not name:
                        continue
                    out.append((seq, prov, name, pageno))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--province", required=True)
    ap.add_argument("--batch", default="第六批")
    ap.add_argument("--list-type", default="new",
                    help="new=新增, review_passed=复核通过, rename=更名")
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    rows = extract_rows(args.pdf)
    # 校验：全部属于目标省份（更名名单同样含省份列）
    bad_prov = [r for r in rows if args.province not in r[1]]
    if bad_prov:
        print(f"[警告] {len(bad_prov)} 行省份不是 {args.province}，例如 {bad_prov[:3]}")

    seen, dedup = set(), []
    for seq, prov, name, pageno in rows:
        if name in seen:
            continue
        seen.add(name)
        dedup.append((seq, prov, name))
    dedup.sort(key=lambda r: r[0])

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    source_file = os.path.basename(args.pdf)
    with open(args.out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["province", "batch", "list_type", "sequence_in_source",
                    "company_name", "source_file"])
        for seq, prov, name in dedup:
            w.writerow([args.province, args.batch, args.list_type, seq,
                        name, source_file])

    print(f"{args.province} [{args.list_type}]: 解析 {len(rows)} 行，去重后 {len(dedup)} 家 "
          f"-> {args.out}")


if __name__ == "__main__":
    main()
