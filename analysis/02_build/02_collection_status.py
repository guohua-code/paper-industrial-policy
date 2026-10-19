#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第六批小巨人省级采集状态清单 + 校验器（只读，不联网，不改数据）。"""
from pathlib import Path
import csv, collections

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw/little_giant/2024_batch6_provincial"
INTERIM = ROOT / "data/interim/little_giant_batch6"

# 31个省级行政区（省/自治区/直辖市），深圳等单列市计入广东不单列
REGIONS = ["北京市","天津市","河北省","山西省","内蒙古自治区","辽宁省","吉林省","黑龙江省",
"上海市","江苏省","浙江省","安徽省","福建省","江西省","山东省","河南省","湖北省","湖南省",
"广东省","广西壮族自治区","海南省","重庆市","四川省","贵州省","云南省","西藏自治区",
"陕西省","甘肃省","青海省","宁夏回族自治区","新疆维吾尔自治区"]
PINYIN = {"北京市":"beijing","天津市":"tianjin","河北省":"hebei","山西省":"shanxi","内蒙古自治区":"neimenggu",
"辽宁省":"liaoning","吉林省":"jilin","黑龙江省":"heilongjiang","上海市":"shanghai","江苏省":"jiangsu",
"浙江省":"zhejiang","安徽省":"anhui","福建省":"fujian","江西省":"jiangxi","山东省":"shandong",
"河南省":"henan","湖北省":"hubei","湖南省":"hunan","广东省":"guangdong","广西壮族自治区":"guangxi",
"海南省":"hainan","重庆市":"chongqing","四川省":"sichuan","贵州省":"guizhou","云南省":"yunnan",
"西藏自治区":"xizang","陕西省":"shaanxi","甘肃省":"gansu","青海省":"qinghai",
"宁夏回族自治区":"ningxia","新疆维吾尔自治区":"xinjiang"}

def csv_count(path, list_type):
    if not path.exists(): return None
    with path.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    return sum(1 for r in rows if r.get("list_type") == list_type)

def prov_new_count(py):
    """标准名优先；广东有非标准 partial 文件（省内263，不含深圳），单独识别。"""
    std = csv_count(INTERIM / f"{py}_new.csv", "new")
    if std is not None:
        return std, "标准"
    partial = INTERIM / f"{py}_partial.csv"
    if partial.exists():
        n = csv_count(partial, "new")
        if n is not None:
            return n, "部分(partial)"
    return None, ""

rows = []
for prov in REGIONS:
    py = PINYIN[prov]
    rawdir = RAW / py
    new_n, src_tag = prov_new_count(py)
    rev_n = csv_count(INTERIM / f"{py}_review.csv", "review_passed")
    has_raw = rawdir.exists() and any(rawdir.iterdir())
    has_source = (rawdir / "SOURCE.md").exists()
    note = ""
    if prov == "广东省":
        sz_new = csv_count(INTERIM / "shenzhen_new.csv", "new") or 0
        sz_rev = csv_count(INTERIM / "shenzhen_review.csv", "review_passed") or 0
        base = new_n if new_n is not None else 0
        note = f"省内{base}({src_tag}) + 深圳单列{sz_new}；复核深圳{sz_rev}"
        # 广东new合计 = 省内partial + 深圳单列
        new_total = base + sz_new
    else:
        new_total = new_n
    status = "已解析" if new_n is not None else "缺失"
    rows.append((prov, status, new_n, new_total, rev_n, has_source, note))

print("="*84)
print("第六批省级采集作战地图  (只读本地；new合计含计划单列市深圳)")
print("="*84)
print(f"{'省份':<9}{'状态':<6}{'省内新增':>7}{'含单列合计':>9}{'复核':>6}  {'SRC':<4} 备注")
print("-"*84)
tot_new=tot_rev=0; missing=[]; done=[]
for prov,st,nn,nt,rv,src,note in rows:
    nn_s = str(nn) if nn is not None else "-"
    nt_s = str(nt) if (nt or 0)>0 else "-"
    rv_s = str(rv) if rv is not None else "-"
    print(f"{prov:<9}{st:<6}{nn_s:>7}{nt_s:>9}{rv_s:>6}  {'有' if src else '无':<4} {note}")
    if nt: tot_new+=nt; done.append(prov)
    if prov!="广东省" and nn is None: missing.append(prov)
    if rv: tot_rev+=rv
print("-"*84)
print(f"已解析(含深圳): {len(done)} 省   真正缺新增名单: {len(missing)} 省")
print(f"缺失清单: {'、'.join(missing)}")
print(f"全国新增CSV合计(广东含深圳): {tot_new}   复核合计: {tot_rev}")
print(f"公开口径第六批新增 3012，对省级CSV缺口: {3012 - tot_new}")
