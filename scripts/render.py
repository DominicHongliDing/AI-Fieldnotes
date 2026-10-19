"""Render the browsing directories from the maintained catalog."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def cell(text):
    return str(text).replace('|', '\\|').replace('\n', ' ')

def render():
    data = json.loads((ROOT / 'data/catalog.json').read_text(encoding='utf-8'))
    resources = ['# 网站与工具', '', '[返回首页](../README.md) · [作者目录](creators.md) · [文章与视频](reading.md)', '',
                 '按用途寻找入口。以下推荐依据官网或项目文档整理；没有标注实际试用的条目，不代表已完成体验评测。收费、地区与账号条件请以官网为准。', '']
    categories = dict.fromkeys(r['category'] for r in data['resources'] if r['status'] == 'active')
    for category in categories:
        resources += [f'## {category}', '', '| 资源 | 适合谁、有什么用 | 从哪里开始 |', '|---|---|---|']
        for r in data['resources']:
            if r['category'] != category or r['status'] != 'active':
                continue
            resources.append(f"| [{cell(r['name'])}]({r['url']}) · {cell(r['language'])} | {cell(r['audience'])}。{cell(r['why'])} | {cell(r['first_step'])} |")
        resources += ['', '<details>', '<summary>本组来源与核对日期</summary>', '']
        for r in data['resources']:
            if r['category'] == category and r['status'] == 'active':
                resources.append(f"- {r['name']}：[核对来源]({r['source_url']}) · {r['checked_at']} · {'有实际试用记录' if r['hands_on'] else '介绍核对，未完成试用评测'}")
        resources += ['', '</details>', '']
    authors = ['# 值得关注的作者与频道', '', '[返回首页](../README.md) · [具体文章与视频](reading.md)', '',
               '先按感兴趣的主题选两三位，持续看一段时间，再决定是否增加。频道收录代表值得了解其内容，不代表赞同作者的所有观点。', '',
               'X 入口通过作者官网交叉确认；部分动态页面限制访问，本次未核验其最近发帖情况。', '']
    for c in data['creators']:
        if c['status'] != 'active':
            continue
        authors += [f"## {c['name']}", '', f"**{c['focus']}** · {c['language']}", '', c['why'], '',
                    ' · '.join(f'[{label}]({url})' for label, url in c['links'].items()), '',
                    f"账号来源：[作者主页]({c['homepage']}) · 核对：{c['checked_at']}", '']
    reading = ['# 留下来慢慢看的文章与视频', '', '[返回首页](../README.md) · [更新记录](../editions/README.md)', '',
               '这里包含近期文章、方法资料和旧课程。原始发布日期与核对日期分别记录，收录日期不代表新发布。视频条目注明查看了什么；尚未完整观看的条目只作为观看导引。', '']
    for kind in ('视频', '文章'):
        reading += [f'## {kind}', '']
        for item in data['reading']:
            if item['kind'] != kind or item['status'] != 'active':
                continue
            reading += [f"### [{item['title']}]({item['url']})", '',
                        f"{item['author']} · {item['language']} · {item['published_at'] or item['date_note']}", '',
                        item['why'], '', f"适合：{item['audience']}。{item['caution']}", '',
                        f"推荐依据：{item['basis']}（[来源]({item['source_url']})）。收录 / 核对：{item['checked_at']}。", '']
    for name, lines in [('resources',resources),('creators',authors),('reading',reading)]:
        (ROOT / f'guides/{name}.md').write_text('\n'.join(lines).strip()+'\n',encoding='utf-8',newline='\n')
    print(f"Rendered {len(data['resources'])} resources, {len(data['creators'])} creators, {len(data['reading'])} reading items")

if __name__ == '__main__':
    render()
