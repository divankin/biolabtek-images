import os, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

rows = [l.rstrip('\n').split('\t') for l in open('urls.tsv') if l.strip()]
failed = []

def get(row):
    mid, pos, url = row
    path = f'photos/{mid}/{pos}.jpg'
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            open(path, 'wb').write(data)
            return
        except Exception as e:
            err = e
            time.sleep(3 * (attempt + 1))
    failed.append(f'{mid}\t{pos}\t{url}\t{err}')

with ThreadPoolExecutor(8) as ex:
    list(ex.map(get, rows))

if failed:
    open('failed.txt', 'w').write('\n'.join(failed) + '\n')
print(f'{len(rows)} urls, {len(failed)} failed')
