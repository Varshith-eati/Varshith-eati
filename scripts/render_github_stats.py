"""Render GitHub metrics and language composition using local JSON snapshots."""
import json
from svg_common import ROOT, begin, chrome, text, save, FG, MUTED, GREEN

COLORS = ['#58a6ff','#f1e05a','#a371f7','#f78166','#39d353','#db61a2','#8b949e']
LANGUAGE_COLORS = {'JavaScript':'#f1e05a','HTML':'#e34c26','CSS':'#a371f7',
                   'Python':'#58a6ff','TypeScript':'#3178c6','Batchfile':'#89e051','Other':'#8b949e'}


def render(profile, calendar):
    stats = calendar['stats']
    parts = begin(860, 248, 'GitHub stats', 'Public GitHub metrics and contribution streaks within the displayed 53-week calendar.')
    chrome(parts, 'GitHub stats', 860)
    parts.append(text(834,25,'Updated '+profile['as_of']+' UTC',11,MUTED,'text-anchor="end"'))
    for i, (value, label) in enumerate([(f"{stats['total']:,}", 'Contributions in 53 weeks'),
                                      (stats['current_streak'], 'Current streak / days'),
                                      (stats['longest_streak'], 'Longest streak / days')]):
        x=145+i*285
        parts.append(text(x,98,value,32,GREEN,'text-anchor="middle" font-weight="600"'))
        parts.append(text(x,126,label,13,FG,'text-anchor="middle"'))
        if i<2:
            parts.append(f'<path d="M{286+i*285} 63V143" stroke="#30363d"/>')
    parts.append('<path d="M24 155H836" stroke="#21262d"/>')
    for i,(value,label) in enumerate([(profile['public_repos'],'Public repositories'),(profile['stars'],'Stars on original repos'),(profile['followers'],'Followers')]):
        x=145+i*285
        parts.append(text(x,187,value,21,FG,'text-anchor="middle" font-weight="600"'))
        parts.append(text(x,208,label,12,MUTED,'text-anchor="middle"'))
    parts.append(text(24,235,'Contribution period: '+calendar['start']+' to '+calendar['as_of'],10,MUTED))
    save(ROOT/'github-stats.svg',parts)

    languages = list(profile['languages'].items())
    shown = languages[:6]
    if len(languages)>6:
        shown.append(('Other',sum(v for _,v in languages[6:])))
    total = sum(v for _,v in shown)
    parts = begin(860,248,'Most used languages',profile['language_scope'])
    chrome(parts,'Most used languages',860)
    parts.append(text(24,69,'Across '+str(profile['original_repos_analyzed'])+' public original repositories',13,FG))
    x=24
    for i,(name,value) in enumerate(shown):
        width=812*value/total if total else 0
        color=LANGUAGE_COLORS.get(name,COLORS[i])
        parts.append(f'<rect x="{x:.3f}" y="85" width="{width:.3f}" height="12" fill="{color}"/>')
        x+=width
        lx=24+(i%3)*278
        ly=127+(i//3)*30
        parts.append(f'<circle cx="{lx+5}" cy="{ly-4}" r="5" fill="{color}"/>')
        percent=value/total*100 if total else 0
        share='<0.1%' if 0<percent<0.1 else f'{percent:.1f}%'
        parts.append(text(lx+18,ly,f'{name}  {share}',13,FG))
    if not total:
        parts.append(text(24,125,'No public language data yet.',13,MUTED))
    parts.append(text(24,226,'Language share by bytes of code / public repos / excludes forks and archived repositories',10,MUTED))
    save(ROOT/'top-languages.svg',parts)


if __name__ == '__main__':
    render(json.loads((ROOT/'data/github-stats.json').read_text(encoding='utf-8')),
           json.loads((ROOT/'data/contributions.json').read_text(encoding='utf-8')))
