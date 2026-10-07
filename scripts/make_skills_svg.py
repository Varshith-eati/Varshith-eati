"""Render local technology logos and names as a self-contained terminal card."""
import json
import re
from xml.etree import ElementTree as ET
from svg_common import ROOT, MUTED, FG, begin, chrome, text, save

ET.register_namespace('', 'http://www.w3.org/2000/svg')


def render():
    groups = json.loads((ROOT / 'data/skills.json').read_text(encoding='utf-8'))
    height = 64 + len(groups)*100
    parts = begin(860, height, 'Skills and technologies - Eati Varshith',
                  'Technologies from my profile, each with its logo and name. '
                  + '; '.join(g['category']+': '+', '.join(i['name'] for i in g['items']) for g in groups))
    chrome(parts, '~/skills / technology inventory', 860)
    for row, group in enumerate(groups):
        y = 63 + row*100
        category = group['category'].split(' & ')
        for index, line in enumerate(category):
            if index:
                line = '& ' + line
            parts.append(text(22, y+30+index*16, line, 11, MUTED))
        for column, item in enumerate(group['items']):
            x = 148 + column*98
            logo = ET.parse(ROOT / 'assets/skills' / item['icon']).getroot()
            svg = ET.tostring(logo, encoding='unicode')
            # Keep gradient and clipping IDs unique across all embedded logos.
            for old_id in re.findall(r'\bid="([^"]+)"', svg):
                new_id = f'logo-{row}-{column}-{old_id}'
                svg = svg.replace(f'id="{old_id}"', f'id="{new_id}"')
                svg = svg.replace(f'url(#{old_id})', f'url(#{new_id})')
                svg = svg.replace(f'="#'+old_id+'"', f'="#'+new_id+'"')
            logo = ET.fromstring(svg)
            logo.set('x', str(x+18))
            logo.set('y', str(y+2))
            logo.set('width', '44')
            logo.set('height', '44')
            parts.append(ET.tostring(logo, encoding='unicode'))
            parts.append(text(x+40, y+67, item['name'], 11, FG, 'text-anchor="middle"'))
        if row < len(groups)-1:
            parts.append(f'<path d="M22 {y+85}H838" stroke="#21262d"/>')
    save(ROOT / 'skills.svg', parts)


if __name__ == '__main__':
    render()
