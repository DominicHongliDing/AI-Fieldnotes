"""Check source attribution, dates, duplicates and local Markdown links offline."""
import json
import re
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT/'data/catalog.json').read_text(encoding='utf-8'))
errors = []

def check(condition, message):
    if not condition:
        errors.append(message)

def valid_date(value, label):
    try:
        check(date.fromisoformat(value) <= date.today(), label + ': future date')
    except (TypeError, ValueError):
        errors.append(label + ': invalid date')

def url(value, label):
    parts = urlsplit(value)
    check(parts.scheme == 'https' and bool(parts.netloc) and not parts.username, label + ': invalid public URL')

for collection in ('resources','creators','reading'):
    ids, links = set(), set()
    for item in data[collection]:
        label = collection + '/' + item.get('id','MISSING')
        check(bool(item.get('id')) and item['id'] not in ids, label + ': duplicate or absent id')
        ids.add(item.get('id'))
        check(item.get('status') in ('active','retired'), label + ': status')
        valid_date(item.get('checked_at'), label)
        check(bool(item.get('why')), label + ': reason missing')
        if collection == 'creators':
            url(item['homepage'], label)
            for value in item['links'].values():
                url(value, label)
            continue
        url(item['url'], label)
        url(item['source_url'], label)
        check(item['url'].rstrip('/') not in links, label + ': duplicate URL')
        links.add(item['url'].rstrip('/'))
        if collection == 'reading':
            if item.get('published_at'):
                valid_date(item['published_at'], label)
            else:
                check(bool(item.get('date_note')), label + ': unknown date without note')
            check(bool(item.get('basis')), label + ': recommendation basis missing')
            if item.get('section') == 'news':
                check(bool(item.get('published_at')), label + ': news requires publication date')
        if collection == 'resources' and item.get('hands_on'):
            check(bool(item.get('test_record')), label + ': hands-on claim requires record')

for path in ROOT.rglob('*.md'):
    if '.git' in path.parts:
        continue
    for target in re.findall(r'\]\(([^)]+)\)',path.read_text(encoding='utf-8')):
        if urlsplit(target).scheme or target.startswith('#'):
            continue
        target = unquote(target.split('#')[0].split('?')[0])
        check((path.parent/target).resolve().exists(), f'{path.relative_to(ROOT)}: missing local link {target}')

if errors:
    raise SystemExit('\n'.join(errors))
print('PASS: catalog attribution, dates, IDs, duplicate URLs and internal links')
