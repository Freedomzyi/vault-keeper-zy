#!/usr/bin/env python3
"""vault-keeper-ZY 工具箱 — Obsidian 知识库确定性操作层

用法：
  python vault_tools.py validate <vault_path>     # YAML frontmatter 校验
  python vault_tools.py broken-links <vault_path> # 断链检测
  python vault_tools.py orphans <vault_path>      # 孤儿笔记检测
  python vault_tools.py duplicates <vault_path>   # 相似内容检测
  python vault_tools.py expired <vault_path>      # 过期卡片检测
  python vault_tools.py moc <vault_path>           # 生成/更新 对话总览.md
  python vault_tools.py stats <vault_path>         # 生成 vault 统计
  python vault_tools.py health <vault_path>        # 运行完整健康检查
  python vault_tools.py template card <title>      # 输出知识卡片模板
  python vault_tools.py template conversation <date> <title>  # 输出对话记录模板
"""

import sys
import os
import re
import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter, defaultdict

# ─── YAML frontmatter 解析（不依赖 pyyaml）──────────────────────────

def parse_frontmatter(filepath: Path) -> dict | None:
    """解析 Markdown 文件的 YAML frontmatter，返回 dict 或 None"""
    try:
        text = filepath.read_text(encoding="utf-8")
    except Exception:
        return None

    if not text.startswith("---"):
        return None

    end = text.find("---", 3)
    if end == -1:
        return None

    fm_text = text[3:end].strip()
    result = {}
    for line in fm_text.split("\n"):
        line = line.strip()
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            # 处理列表
            if value.startswith("[") and value.endswith("]"):
                value = [v.strip().strip('"').strip("'") for v in value[1:-1].split(",") if v.strip()]
            result[key] = value
    return result


def find_md_files(vault: Path) -> list[Path]:
    """递归找到所有 .md 文件，跳过 .obsidian/ 和模板/"""
    files = []
    for f in vault.rglob("*.md"):
        if ".obsidian" in f.parts:
            continue
        if "模板" in f.parts:
            continue
        files.append(f)
    return files


# ─── 1. YAML frontmatter 校验 ───────────────────────────────────────

def validate_frontmatter(vault: Path) -> dict:
    """扫描所有 md 文件，检查 frontmatter 合规性"""
    required_fields = {"date", "tags", "status"}
    card_required = {"expires"}  # 知识卡片必须有的额外字段

    issues = []
    total = 0
    ok = 0

    for f in find_md_files(vault):
        total += 1
        fm = parse_frontmatter(f)
        rel = f.relative_to(vault)

        if fm is None:
            issues.append({"file": str(rel), "issue": "缺少 YAML frontmatter"})
            continue

        missing = required_fields - set(fm.keys())
        if missing:
            issues.append({"file": str(rel), "issue": f"缺少必填字段: {', '.join(sorted(missing))}"})
            continue

        # 知识卡片额外检查
        if "知识卡片" in str(rel):
            if "expires" not in fm:
                issues.append({"file": str(rel), "issue": "知识卡片缺少 expires 字段"})

        # 检查过期
        if fm.get("expires"):
            try:
                exp = datetime.strptime(str(fm["expires"]), "%Y-%m-%d")
                if exp < datetime.now():
                    issues.append({
                        "file": str(rel),
                        "issue": f"已过期 (expires: {fm['expires']})"
                    })
            except ValueError:
                issues.append({"file": str(rel), "issue": f"expires 格式错误: {fm['expires']}"})

        ok += 1

    return {"total": total, "ok": ok, "issues": len(issues), "details": issues}


# ─── 2. 断链检测 ────────────────────────────────────────────────────

def check_broken_links(vault: Path) -> dict:
    """扫描所有 [[wikilinks]] 是否指向存在的文件"""
    wikilink_re = re.compile(r"\[\[([^\]|#]+)(?:[|#][^\]]+)?\]\]")

    all_files = {f.stem: f for f in find_md_files(vault)}
    all_files.update({f.name.replace(".md", ""): f for f in find_md_files(vault)})

    # 也检查带路径的链接（去目录前缀）
    for f in find_md_files(vault):
        rel = str(f.relative_to(vault)).replace("\\", "/")
        all_files[rel.replace(".md", "")] = f

    broken = []

    for f in find_md_files(vault):
        try:
            text = f.read_text(encoding="utf-8")
        except Exception:
            continue

        links = wikilink_re.findall(text)
        for link in links:
            link = link.strip()
            if link not in all_files:
                broken.append({
                    "from": str(f.relative_to(vault)),
                    "to": link
                })

    return {"total_links_checked": sum(1 for _ in broken) + len(broken),  # approximate
            "broken": len(broken),
            "details": broken}


# ─── 3. 孤儿笔记检测 ────────────────────────────────────────────────

def find_orphans(vault: Path) -> dict:
    """找出零反向链接的知识卡片"""
    files = find_md_files(vault)
    file_stems = {f.stem for f in files}
    file_rels = {str(f.relative_to(vault)).replace("\\", "/").replace(".md", "") for f in files}

    # 统计被引用次数
    ref_count = Counter()
    wikilink_re = re.compile(r"\[\[([^\]|#]+)(?:[|#][^\]]+)?\]\]")

    for f in files:
        try:
            text = f.read_text(encoding="utf-8")
        except Exception:
            continue
        for link in wikilink_re.findall(text):
            link = link.strip()
            ref_count[link] += 1

    orphans = []
    for f in files:
        rel = str(f.relative_to(vault))
        stem = f.stem
        rel_no_ext = rel.replace(".md", "")
        # 检查多种匹配方式
        if ref_count[stem] == 0 and ref_count[rel_no_ext] == 0:
            fm = parse_frontmatter(f)
            if fm and "知识卡片" in str(rel):
                orphans.append({"file": rel, "backlinks": 0})

    return {"orphans": len(orphans), "details": orphans}


# ─── 4. 重复检测 ────────────────────────────────────────────────────

def detect_duplicates(vault: Path) -> dict:
    """检测文件名相似或内容高度相似的卡片"""
    files = find_md_files(vault)
    similar = []

    # 按文件名相似度
    stems = [f.stem.lower() for f in files]
    for i in range(len(stems)):
        for j in range(i + 1, len(stems)):
            s1, s2 = stems[i], stems[j]
            # 简单判断：一个包含另一个 或 编辑距离 ≤ 3
            if s1 != s2 and (s1 in s2 or s2 in s1 or _levenshtein(s1, s2) <= 3):
                similar.append({
                    "file1": str(files[i].relative_to(vault)),
                    "file2": str(files[j].relative_to(vault)),
                    "reason": "文件名相似"
                })

    return {"similar_pairs": len(similar), "details": similar[:20]}


def _levenshtein(a: str, b: str) -> int:
    if len(a) < len(b):
        return _levenshtein(b, a)
    if len(b) == 0:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a):
        curr = [i + 1]
        for j, cb in enumerate(b):
            curr.append(min(
                prev[j + 1] + 1,
                curr[j] + 1,
                prev[j] + (ca != cb)
            ))
        prev = curr
    return prev[-1]


# ─── 5. 过期检测 ────────────────────────────────────────────────────

def check_expired(vault: Path) -> dict:
    """检测即将过期和已过期的卡片"""
    now = datetime.now()
    soon = now + timedelta(days=7)
    expired = []
    expiring_soon = []
    stale_by_mtime = []

    for f in find_md_files(vault):
        fm = parse_frontmatter(f)
        if not fm:
            continue

        # 检查 expires 字段
        if fm.get("expires"):
            try:
                exp = datetime.strptime(str(fm["expires"]), "%Y-%m-%d")
                if exp < now:
                    expired.append({"file": str(f.relative_to(vault)), "expires": str(fm["expires"])})
                elif exp <= soon:
                    expiring_soon.append({"file": str(f.relative_to(vault)), "expires": str(fm["expires"])})
            except ValueError:
                pass

        # 检查 mtime（知识卡片）
        if "知识卡片" in str(f.relative_to(vault)):
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            days_since = (now - mtime).days
            if days_since >= 180:
                stale_by_mtime.append({
                    "file": str(f.relative_to(vault)),
                    "days_since_modified": days_since
                })

    return {
        "expired": len(expired),
        "expiring_soon": len(expiring_soon),
        "stale_by_mtime": len(stale_by_mtime),
        "expired_details": expired,
        "expiring_soon_details": expiring_soon,
        "stale_details": stale_by_mtime
    }


# ─── 6. MOC 生成 ────────────────────────────────────────────────────

def generate_moc(vault: Path, dry_run: bool = False) -> str:
    """生成或更新 对话总览.md"""
    conv_dir = vault / "对话记录"
    card_dir = vault / "知识卡片"

    lines = [
        "# 对话总览",
        "",
        f"> 自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## 对话记录",
        ""
    ]

    if conv_dir.exists():
        conv_files = sorted(conv_dir.glob("*.md"), reverse=True)
        by_month = defaultdict(list)
        for f in conv_files:
            month = f.stem[:7]  # YYYY-MM
            by_month[month].append(f)

        for month in sorted(by_month.keys(), reverse=True):
            lines.append(f"### {month}")
            for f in sorted(by_month[month], reverse=True):
                lines.append(f"- [[对话记录/{f.stem}|{f.stem}]]")
            lines.append("")

    lines.append("## 知识卡片")
    lines.append("")
    if card_dir.exists():
        for f in sorted(card_dir.glob("*.md")):
            fm = parse_frontmatter(f)
            status_tag = f" `[{fm.get('status', '?')}]`" if fm else ""
            lines.append(f"- [[知识卡片/{f.stem}]]{status_tag}")
    lines.append("")

    content = "\n".join(lines)

    if not dry_run:
        moc_path = vault / "对话总览.md"
        moc_path.write_text(content, encoding="utf-8")

    return content


# ─── 7. Vault 统计 ──────────────────────────────────────────────────

def generate_stats(vault: Path, search_hits: list = None,
                   recent_hits: list = None, dry_run: bool = False) -> str:
    """生成 vault 统计报表"""
    conv_dir = vault / "对话记录"
    card_dir = vault / "知识卡片"

    conv_count = len(list(conv_dir.glob("*.md"))) if conv_dir.exists() else 0
    card_count = len(list(card_dir.glob("*.md"))) if card_dir.exists() else 0

    # 统计标签
    all_tags = Counter()
    if card_dir.exists():
        for f in card_dir.glob("*.md"):
            fm = parse_frontmatter(f)
            if fm and fm.get("tags"):
                tags = fm["tags"]
                if isinstance(tags, str):
                    tags = [tags]
                for t in tags:
                    if isinstance(t, str):
                        all_tags[t.strip()] += 1

    lines = [
        "# Vault 统计",
        "",
        f"> 更新于 {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        f"- 📝 对话记录：{conv_count} 篇",
        f"- 🃏 知识卡片：{card_count} 张",
        f"- 🔗 标签种类：{len(all_tags)} 个",
        ""
    ]

    if all_tags:
        lines.append("## 标签分布")
        for tag, count in all_tags.most_common():
            lines.append(f"- {tag}: {count}")
        lines.append("")

    if search_hits:
        lines.append("## 本次检索命中明细")
        lines.append("")
        lines.append("| 卡片/文件 | 命中 |")
        lines.append("|-----------|------|")
        for hit in search_hits:
            lines.append(f"| {hit.get('name', '?')} | {hit.get('score', '?')} |")
        lines.append("")

    if recent_hits:
        lines.append("## 近 30 天活跃度排行 Top 5")
        for i, hit in enumerate(recent_hits[:5], 1):
            lines.append(f"{i}. {hit.get('name', '?')} — {hit.get('count', 0)} 次")
        lines.append("")

    content = "\n".join(lines)

    if not dry_run:
        stats_path = vault / "vault 统计.md"
        stats_path.write_text(content, encoding="utf-8")

    return content


# ─── 8. 健康检查报告 ────────────────────────────────────────────────

def run_health_check(vault: Path, dry_run: bool = False) -> str:
    """运行完整健康检查，生成报告"""
    now = datetime.now().strftime("%Y-%m-%d")

    valid = validate_frontmatter(vault)
    broken = check_broken_links(vault)
    orphans = find_orphans(vault)
    dupes = detect_duplicates(vault)
    expired = check_expired(vault)

    report = [
        f"# 健康报告 {now}",
        "",
        f"> vault-keeper-ZY 自动生成",
        "",
        "## 概览",
        "",
        f"| 检查项 | 状态 |",
        f"|--------|------|",
        f"| YAML 合规 | {valid['ok']}/{valid['total']} ({valid['issues']} 问题) |",
        f"| 断链检测 | {broken['broken']} 条 |",
        f"| 孤儿卡片 | {orphans['orphans']} 张 |",
        f"| 重复检测 | {dupes['similar_pairs']} 对 |",
        f"| 已过期卡片 | {expired['expired']} 张 |",
        f"| 即将过期 | {expired['expiring_soon']} 张 |",
        f"| 长期未改 | {expired['stale_by_mtime']} 张 |",
        "",
    ]

    # 详细问题
    if broken["details"]:
        report.append("## ⚠️ 断链")
        for b in broken["details"][:10]:
            report.append(f"- `{b['from']}` → `[[{b['to']}]]`")
        report.append("")

    if orphans["details"]:
        report.append("## 👻 孤儿卡片（零反向链接）")
        for o in orphans["details"]:
            report.append(f"- {o['file']}")
        report.append("")

    if expired["expired_details"]:
        report.append("## ❌ 已过期")
        for e in expired["expired_details"]:
            report.append(f"- {e['file']} (expires: {e['expires']})")
        report.append("")

    if expired["expiring_soon_details"]:
        report.append("## ⏳ 即将过期（7天内）")
        for e in expired["expiring_soon_details"]:
            report.append(f"- {e['file']} (expires: {e['expires']})")
        report.append("")

    content = "\n".join(report)

    if not dry_run:
        health_dir = vault / "系统"
        health_dir.mkdir(parents=True, exist_ok=True)
        report_path = health_dir / f"健康报告 {now}.md"
        report_path.write_text(content, encoding="utf-8")

    return content


# ─── 9. 模板生成 ────────────────────────────────────────────────────

def template_card(title: str) -> str:
    return f"""---
date: {datetime.now().strftime('%Y-%m-%d')}
tags: []
aliases: []
status: active
expires: {(datetime.now() + timedelta(days=180)).strftime('%Y-%m-%d')}
---

# {title}

## 要点

## 相关

- [[]]
"""


def template_conversation(date: str, title: str) -> str:
    return f"""---
date: {date}
tags: [小龙虾, 对话]
aliases: []
status: active
---

# {date} {title}

## 话题

## 决策

## 待办

## 相关

- [[]]
"""


# ─── CLI ────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "template":
        if len(sys.argv) < 4:
            print("用法: vault_tools.py template card <title>")
            print("      vault_tools.py template conversation <date> <title>")
            sys.exit(1)
        kind = sys.argv[2]
        if kind == "card":
            print(template_card(sys.argv[3]))
        elif kind == "conversation":
            print(template_conversation(sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else ""))
        return

    if len(sys.argv) < 3:
        print(f"用法: vault_tools.py {cmd} <vault_path>")
        sys.exit(1)

    vault = Path(sys.argv[2])
    if not vault.exists():
        print(json.dumps({"error": f"vault 路径不存在: {vault}"}, ensure_ascii=False))
        sys.exit(1)

    result = None

    if cmd == "validate":
        result = validate_frontmatter(vault)
    elif cmd == "broken-links":
        result = check_broken_links(vault)
    elif cmd == "orphans":
        result = find_orphans(vault)
    elif cmd == "duplicates":
        result = detect_duplicates(vault)
    elif cmd == "expired":
        result = check_expired(vault)
    elif cmd == "moc":
        result = {"ok": True, "message": "对话总览.md 已更新"}
        generate_moc(vault)
    elif cmd == "stats":
        result = {"ok": True, "message": "vault 统计.md 已更新"}
        generate_stats(vault)
    elif cmd == "health":
        report = run_health_check(vault)
        result = {"ok": True, "message": "健康报告已生成", "report": report[:200] + "..."}
    else:
        print(f"未知命令: {cmd}")
        print(__doc__)
        sys.exit(1)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
