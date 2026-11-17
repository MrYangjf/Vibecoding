﻿# -*- coding: utf-8 -*-
"""simplify_apply_docs.py —— 文档注释补全/压缩器（§二②）。

口径（2026-10-26 业主裁定，standards/CodeSimplification §一①/§二②/顶层裁定第 3 条）：
  · public/protected：新增或改动必写 ///（存量不追溯 ⇒ 本脚本不新增 public 的 ///，只修已写好的）
  · private：**允许且建议写** /// 做总结（不强制）⇒ ⛔ **不得删除既有 private ///**
  · 无论公私，**写了就要写对**：summary 一行 ≤20 字 + param/returns 完整
本脚本只改注释文本（不动代码）：补 <param>、补 <returns>、压缩超 20 汉字的 summary（余文移入 <remarks>）。
插入行**继承 doc 块首行的前导空白**（禁区坑 #4）；逐文件快照可回滚。
用法：python simplify_apply_docs.py --all [--dry-run] [--files a.cs ...]
"""
import os, re, sys, shutil, argparse, time

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import csharp_review as CR
import simplify_guard as G
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CODE = os.path.join(ROOT, "AdaWeldSystem")
SNAP = os.path.join(ROOT, "_simplify_snapshot")
SKIP = {"bin", "obj", "3rdDepend", ".vs"}
CJK = re.compile(r"[\u4e00-\u9fff]")
PDESC = {
    "message": "消息内容", "msg": "消息内容", "str": "文本内容", "text": "文本内容",
    "level": "日志级别", "index": "索引", "i": "索引", "count": "数量", "n": "数量",
    "path": "路径", "filepath": "文件路径", "name": "名称", "value": "值",
    "timeout": "超时时长(毫秒)", "data": "数据", "result": "结果", "flag": "标志位",
    "enable": "是否启用", "sender": "发送方", "e": "事件参数", "config": "配置对象",
    "axis": "轴对象", "target": "目标位置(mm)", "delta": "增量值", "obj": "对象",
    "bytes": "字节数据", "row": "行数据", "col": "列名", "len": "长度",
    "offset": "偏移量", "key": "键名", "tablename": "表名", "sql": "SQL 语句",
    "success": "是否成功", "force": "是否强制执行", "item": "数据项",
    "list": "数据集合", "size": "元素个数", "num": "数量", "total": "合计值",
    "targetmm": "目标位置 毫米", "tolmm": "到位容差 毫米", "timeoutseconds": "超时秒数",
    "nochangeseconds": "位置无变化早停秒数", "requirestablespeed": "是否要求速度稳定",
    "cancelrequested": "取消请求回调", "evidence": "失败证据收集开关",
    "cfg": "配置对象", "document": "XML 文档对象", "buf": "字节缓冲区",
    "section": "配置段名", "filelabel": "文件标签", "source": "数据来源",
    "keys": "键名集合", "def": "默认值", "min": "下限", "max": "上限",
    "fullpath": "完整路径", "relativepath": "相对路径", "axisname": "轴名",
    "nodeid": "站点号", "reason": "原因说明", "running": "是否正在执行",
    "withbus": "是否叠加总线健康检查", "mode": "工作模式",
    "node": "配置节点", "parent": "父节点", "temp": "临时值", "scale": "比例系数",
    "start": "起始值", "end": "结束值", "width": "宽度", "height": "高度",
    "tag": "日志标签", "title": "标题", "content": "内容", "file": "文件",
    "url": "地址", "ip": "IP 地址", "port": "端口号", "cmd": "指令",
    "code": "结果码", "err": "错误信息", "rowindex": "零基行号",
    "columnindex": "零基列号", "columnname": "列名", "sheetname": "工作表名",
    "filename": "文件名", "actionname": "动作名", "stepindex": "步骤序号",
    "stepname": "步骤名", "axiskey": "轴标识", "timeoutms": "超时毫秒数",
    "headers": "表头集合", "rowvalues": "行数据", "expected": "期望值",
    "actual": "实际值", "exception": "异常对象", "ex": "异常对象",
    "lines": "文本行集合", "parameters": "参数集合", "records": "记录集合",
}


def pdesc(n):
    k = n.lower()
    return PDESC.get(k, k + " 参数")


def rdesc(rt):
    t = (rt or "").strip().lower()
    if t in ("bool", "system.boolean"):
        return "是否成功"
    if t in ("int", "long", "short", "uint", "ulong", "ushort", "byte", "int32", "int64"):
        return "结果码"
    if t in ("double", "float", "decimal"):
        return "计算结果"
    if t in ("string", "system.string"):
        return "结果文本"
    if t.startswith("task"):
        return "异步任务"
    if t.startswith("list") or t.startswith("array") or t.startswith("ienumerable"):
        return "结果集合"
    if t in ("void", ""):
        return None
    return "返回值"


def doc_block(lines, sl):
    i = sl - 1
    if i <= 0 or not lines[i - 1].strip().startswith("///"):
        return None
    j = i - 1
    while j > 0 and lines[j - 1].strip().startswith("///"):
        j -= 1
    return (j, i)


def split_summary(plain, limit=20):
    """按自然断点切分 summary：括号或括号外冒号优先，超限再硬切。"""
    depth, cjk, cands = 0, 0, []
    for i, ch in enumerate(plain):
        if ch in "（(":
            if depth == 0 and 4 <= cjk <= limit:
                cands.append(i)
            depth += 1
        elif ch in "）)":
            depth = max(0, depth - 1)
        elif ch in "：:" and depth == 0 and 4 <= cjk <= limit:
            cands.append(i)
        if CJK.match(ch):
            cjk += 1
        if cjk > limit:
            break
    if cjk <= limit:
        return plain, ""
    if cands:
        i = cands[-1]
        rest = plain[i:].strip().lstrip("（(：:，,；;、 ")
        if plain[i] in "（(":
            rest = rest.rstrip("。").rstrip("）)")
        return plain[:i].strip(), rest
    acc = ""
    for ch in plain:
        if len(CJK.findall(acc + ch)) > limit:
            break
        acc += ch
    return acc.strip(), plain[len(acc):].strip()


def fix_block(text, params, rt):
    stat = {"trim": 0, "param": 0, "returns": 0}
    sm = re.search(r"<summary>(.*?)</summary>", text, re.S)
    if not sm:
        return text, stat
    inner = sm.group(1)
    # 多行 summary 也要能压：先剥掉行内 /// 标记与空白，得到纯文本
    plain = re.sub(r"\s*///\s*", " ", inner).strip()
    acc, rest = split_summary(plain)
    if rest:
        text = text.replace(sm.group(0), "<summary>" + acc + "</summary>")
        if "<remarks>" in text:
            text = re.sub(r"<remarks>(.*?)</remarks>",
                          lambda m: "<remarks>" + m.group(1) + " " + rest + "</remarks>",
                          text, count=1, flags=re.S)
        else:
            text = text.replace("</summary>", "</summary>\n/// <remarks>" + rest + "</remarks>", 1)
        stat["trim"] += 1
    found = set(re.findall(r'<param\s+name="([^"]+)"', text))
    missing = [p for p in params if p not in found]
    if missing:
        ins = "\n".join('/// <param name="%s">%s。</param>' % (p, pdesc(p)) for p in missing)
        text = (text.replace("</summary>", "</summary>\n" + ins, 1) if "</summary>" in text
                else ins + "\n" + text)
        stat["param"] += len(missing)
    if "<returns" not in text and rdesc(rt) is not None:
        text = text.rstrip() + "\n/// <returns>%s。</returns>" % rdesc(rt)
        stat["returns"] += 1
    return text, stat


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--files", nargs="*", default=[])
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.files:
        files = [os.path.abspath(p) for p in a.files]
    else:
        files = []
        for dp, dn, fns in os.walk(CODE):
            dn[:] = [d for d in dn if d not in SKIP]
            for fn in sorted(fns):
                if fn.endswith(".cs") and not fn.endswith(".Designer.cs"):
                    files.append(os.path.join(dp, fn))
        files.sort()
    os.makedirs(SNAP, exist_ok=True)
    t0 = time.time()
    tot = {"trim": 0, "param": 0, "returns": 0}
    nfix = 0
    for f in files:
        raw = open(f, "rb").read()
        bom = raw[:3] == b"\xef\xbb\xbf"
        text_all = raw.decode("utf-8-sig")
        lines = text_all.split("\n")
        edits = []
        for cls in CR.parse_file(text_all):
            for mth in cls.get("methods", []):
                sl = getattr(mth, "start_line", None)
                if not sl:
                    continue
                db = doc_block(lines, sl)
                if not db:
                    continue
                ds, de = db
                text = "\n".join(lines[ds:de])
                pm = getattr(mth, "params", None) or []
                if not isinstance(pm, str):
                    pm = ", ".join(str(x) for x in pm)
                newtext, stat = fix_block(text, CR._parse_param_names(pm),
                                          getattr(mth, "return_type", "") or "")
                if newtext != text:
                    ind = re.match(r"^(\s*)", lines[ds]).group(1)
                    payload = [ind + l.lstrip() if l.strip().startswith("///") else l
                               for l in newtext.split("\n")]
                    edits.append((ds, de, payload))
                    for k in tot:
                        tot[k] += stat[k]
        if not edits:
            continue
        edits.sort(key=lambda e: e[0], reverse=True)
        crlf = raw.count(b"\r\n") > 0 and (raw.count(b"\n") - raw.count(b"\r\n")) == 0
        out = list(lines)
        for a1, b1, payload in edits:
            if crlf:
                payload = [p if p.endswith("\r") else p + "\r" for p in payload]
            out[a1:b1] = payload
        if a.dry_run:
            print("DRY   %-56s edits=%d" % (os.path.relpath(f, CODE), len(edits)))
            continue
        cand = "\n".join(out)
        cand_raw = cand.encode("utf-8")
        if bom:
            cand_raw = b"\xef\xbb\xbf" + cand_raw
        broken = G.check_text(cand, cand_raw, text_all, raw)
        if broken:
            print("SKIP  %-56s %s" % (os.path.relpath(f, CODE), "; ".join(broken[:2])))
            continue
        rel = os.path.relpath(f, CODE)
        snap = os.path.join(SNAP, rel.replace("\\", "__"))
        shutil.copy2(f, snap)
        open(f, "wb").write(cand_raw)
        gfs = G.check(f, SNAP)
        if gfs:
            shutil.copy2(snap, f)
            print("ROLLBACK %-50s %s" % (rel, "; ".join(gfs[:2])))
            continue
        nfix += 1
        print("OK    %-58s edits=%d" % (rel, len(edits)), flush=True)
    print("docs: files=%d trim=%d param=%d returns=%d elapsed=%.1fs"
          % (nfix, tot["trim"], tot["param"], tot["returns"], time.time() - t0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
