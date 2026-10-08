"""Snapshot public GitHub profile metrics and language bytes from original repos."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import os
import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from svg_common import ROOT


def api(path):
    headers = {'User-Agent': 'Varshith-profile-stats', 'Accept': 'application/vnd.github+json',
               'X-GitHub-Api-Version': '2022-11-28'}
    if os.environ.get('GITHUB_TOKEN'):
        headers['Authorization'] = 'Bearer ' + os.environ['GITHUB_TOKEN']
    for attempt in range(3):
        try:
            with urlopen(Request('https://api.github.com' + path, headers=headers), timeout=30) as response:
                return json.load(response)
        except (HTTPError, URLError, TimeoutError):
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)


def summarize_languages(language_maps):
    totals = {}
    for mapping in language_maps:
        for name, count in mapping.items():
            if not isinstance(count, int) or count < 0:
                raise ValueError('Unexpected GitHub language byte count')
            totals[name] = totals.get(name, 0) + count
    return dict(sorted(totals.items(), key=lambda item: (-item[1], item[0])))


def main():
    username = json.loads((ROOT/'data/profile.json').read_text(encoding='utf-8'))['username']
    profile = api(f'/users/{username}')
    repos = []
    page = 1
    while True:
        batch = api(f'/users/{username}/repos?type=owner&per_page=100&page={page}')
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    originals = [r for r in repos if not r['fork'] and not r['archived'] and not r['private']]
    with ThreadPoolExecutor(max_workers=3) as pool:
        languages = summarize_languages(pool.map(lambda r: api('/repos/'+r['full_name']+'/languages'), originals))
    data = {'username': username, 'as_of': datetime.now(timezone.utc).date().isoformat(),
            'public_repos': profile['public_repos'], 'followers': profile['followers'],
            'stars': sum(r['stargazers_count'] for r in originals),
            'original_repos_analyzed': len(originals), 'languages': languages,
            'language_scope': 'Bytes of code in public, non-fork, non-archived repositories',
            'source': f'https://api.github.com/users/{username}'}
    temporary = ROOT/'data/github-stats.json.tmp'
    temporary.write_text(json.dumps(data, indent=2)+'\n', encoding='utf-8')
    temporary.replace(ROOT/'data/github-stats.json')
    print(f'Fetched public stats for {username}; analyzed {len(originals)} original repositories')


if __name__ == '__main__':
    main()
