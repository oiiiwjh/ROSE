#!/usr/bin/env python3
"""Generate library/README.md index from all meta.md files."""

import os
import re
import sys
from datetime import datetime
from pathlib import Path


def parse_frontmatter(text):
    """Parse YAML frontmatter from meta.md content."""
    m = re.match(r'^---\s*\n(.*?)\n---', text, re.DOTALL)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        # Handle simple key: value
        kv = re.match(r'^(\w+):\s*(.+)$', line)
        if kv:
            key, val = kv.group(1), kv.group(2).strip()
            # Parse list values like [a, b, c]
            if val.startswith('[') and val.endswith(']'):
                items = val[1:-1]
                fm[key] = [s.strip().strip('"').strip("'") for s in items.split(',') if s.strip()]
            # Parse quoted strings
            elif (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                fm[key] = val[1:-1]
            else:
                fm[key] = val
    return fm


def extract_summary(text):
    """Extract full summary from 概要总结 section."""
    m = re.search(r'## 概要总结\s*\n\n?(.+?)(?:\n\n|\n##|\Z)', text, re.DOTALL)
    if not m:
        return ''
    return m.group(1).strip()


def parse_reading_list(library_dir):
    """Parse reading_list.md and return a set of directory names in the list."""
    rl_path = os.path.join(library_dir, 'reading_list.md')
    dirs_in_list = set()
    if not os.path.isfile(rl_path):
        return dirs_in_list
    with open(rl_path, 'r', encoding='utf-8') as f:
        for line in f:
            # Match markdown links like [Title](papers/2401-12345-nerf/) or (tmp/xxx/)
            for m in re.finditer(r'\]\((?:papers|blogs|tmp)/([^/)]+)/?\)', line):
                dirs_in_list.add(m.group(1))
    return dirs_in_list


def scan_papers(library_dir, subdir):
    """Scan a subdirectory for paper meta.md files."""
    papers = []
    target = os.path.join(library_dir, subdir)
    if not os.path.isdir(target):
        return papers
    for entry in sorted(os.listdir(target)):
        meta_path = os.path.join(target, entry, 'meta.md')
        if os.path.isfile(meta_path):
            with open(meta_path, 'r', encoding='utf-8') as f:
                content = f.read()
            fm = parse_frontmatter(content)
            if fm:
                fm['_dir'] = entry
                fm['_subdir'] = subdir
                # Check if analysis.md and qa.md exist
                fm['_has_analysis'] = os.path.isfile(
                    os.path.join(target, entry, 'analysis.md')
                )
                fm['_has_qa'] = os.path.isfile(
                    os.path.join(target, entry, 'qa.md')
                )
                # Extract summary from body
                fm['_summary'] = extract_summary(content)
                # Collection date: from frontmatter or file mtime
                if 'collected_date' not in fm:
                    mtime = os.path.getmtime(meta_path)
                    fm['collected_date'] = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
                papers.append(fm)
    # Sort by date descending
    papers.sort(key=lambda p: p.get('date', ''), reverse=True)
    return papers


def reading_status(paper, reading_list_dirs):
    """Determine reading status: 已精读 / 计划阅读 / 已分析 / 待阅读."""
    if paper.get('_has_qa'):
        return '✅ 已精读'
    if paper.get('_dir') in reading_list_dirs:
        return '📖 计划阅读'
    if paper.get('_has_analysis'):
        return '📝 已分析'
    return '⬚ 待阅读'


def generate_readme(library_dir):
    """Generate the README.md content."""
    collected = scan_papers(library_dir, 'papers')
    blogged = scan_papers(library_dir, 'blogs')
    temporary = scan_papers(library_dir, 'tmp')
    reading_list_dirs = parse_reading_list(library_dir)

    n_analyzed = sum(1 for p in collected + blogged + temporary if p.get('status') == 'analyzed' or p.get('_has_analysis'))
    n_meta_only = len(collected) + len(blogged) + len(temporary) - n_analyzed

    now = datetime.now().strftime('%Y-%m-%d %H:%M')

    lines = []
    lines.append('# Library Index')
    lines.append('')
    lines.append(f'> 自动生成，请勿手动编辑 | 最后更新: {now}')
    lines.append('')

    # Statistics
    lines.append('## 统计')
    lines.append('')
    lines.append('| 指标 | 数量 |')
    lines.append('|------|------|')
    lines.append(f'| 正式收藏(论文) | {len(collected)} |')
    lines.append(f'| 正式收藏(Blog) | {len(blogged)} |')
    lines.append(f'| 临时/待整理 | {len(temporary)} |')
    lines.append(f'| 已深度分析 | {n_analyzed} |')
    lines.append(f'| 仅元数据 | {n_meta_only} |')
    lines.append('')

    # Collected papers
    lines.append('## 正式收藏 (library/papers/)')
    lines.append('')
    if collected:
        lines.append('| 论文 | 发表日期 | 收集日期 | 来源 | 评分 | 阅读状态 | 概述 |')
        lines.append('|------|----------|----------|------|------|----------|------|')
        for p in collected:
            title = p.get('title', p['_dir'])
            link = f'[{title}](papers/{p["_dir"]}/)'
            date = p.get('date', '')
            collected_date = p.get('collected_date', '')
            source = p.get('source', '')
            rating = p.get('rating', '')
            if rating:
                rating = f'{"⭐" * int(rating)}'
            status = reading_status(p, reading_list_dirs)
            summary = p.get('_summary', '')
            lines.append(f'| {link} | {date} | {collected_date} | {source} | {rating} | {status} | {summary} |')
    else:
        lines.append('*暂无*')
    lines.append('')

    # Blog collection
    lines.append('## 收藏博客 (library/blogs/)')
    lines.append('')
    if blogged:
        lines.append('| 标题 | 日期 | 收集日期 | 来源站点 | 评分 | 阅读状态 | 概述 |')
        lines.append('|------|------|----------|----------|------|----------|------|')
        for p in blogged:
            title = p.get('title', p['_dir'])
            link = f'[{title}](blogs/{p["_dir"]}/)'
            date = p.get('date', '')
            collected_date = p.get('collected_date', '')
            source_site = p.get('source_site', '')
            rating = p.get('rating', '')
            if rating:
                rating = f'{"⭐" * int(rating)}'
            status = reading_status(p, reading_list_dirs)
            summary = p.get('_summary', '')
            lines.append(f'| {link} | {date} | {collected_date} | {source_site} | {rating} | {status} | {summary} |')
    else:
        lines.append('*暂无*')
    lines.append('')

    # Temporary papers
    lines.append('## 临时论文 (library/tmp/)')
    lines.append('')
    if temporary:
        lines.append('| 论文 | 发表日期 | 收集日期 | 来源 | 状态 | 概述 |')
        lines.append('|------|----------|----------|------|------|------|')
        for p in temporary:
            title = p.get('title', p['_dir'])
            link = f'[{title}](tmp/{p["_dir"]}/)'
            date = p.get('date', '')
            collected_date = p.get('collected_date', '')
            source = p.get('source', '')
            status = p.get('status', 'meta_only')
            if p.get('_has_analysis'):
                status = 'analyzed'
            summary = p.get('_summary', '')
            lines.append(f'| {link} | {date} | {collected_date} | {source} | {status} | {summary} |')
    else:
        lines.append('*暂无*')
    lines.append('')

    return '\n'.join(lines)


def main():
    # Determine library directory
    if len(sys.argv) > 1:
        library_dir = sys.argv[1]
    else:
        # Default: library/ relative to repo root
        script_dir = Path(__file__).resolve().parent
        library_dir = str(script_dir.parent.parent.parent / 'library')

    readme_path = os.path.join(library_dir, 'README.md')
    content = generate_readme(library_dir)

    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f'Generated {readme_path}')


if __name__ == '__main__':
    main()
