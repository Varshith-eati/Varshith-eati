# Maintaining this profile

The README embeds four self-contained SVGs. Animations play once, then keep the
finished frame. There is no JavaScript, remote stylesheet, font download, stats
widget, or external image-rendering service. Reduced-motion preferences show the
finished frame immediately.

## Change the info card

Edit `data/profile.json`, then run `python scripts/make_info_card.py` and commit
the JSON and SVG. The workflow also regenerates the card after profile changes.
The initial facts came from the previous profile README; the student role does
not assume that a particular academic year remains current.

## Change the skills card

Edit `data/skills.json` and run `python scripts/make_skills_svg.py`, then commit
the JSON and `skills.svg`. Each logo is embedded as vector artwork, so the card
does not depend on a hosted icon service. The original SVG logos, source URLs,
and MIT licenses are in `assets/skills/`. Most logos come from
[Skill Icons](https://github.com/tandpfun/skill-icons); the Oracle logo comes from
[Devicon](https://github.com/devicons/devicon). Brand marks belong to their owners.

## Change the portrait

Use Python 3.12 and install `scripts/requirements-portrait.txt`. Then run:

```sh
python -m pip install -r scripts/requirements-portrait.txt
python scripts/prep_photo.py /path/to/your-photo.jpg
python scripts/make_ascii_svg.py
```

This photo already had a plain white background. The preparation script masks
that white, applies local contrast enhancement (CLAHE implemented in NumPy), and restores white so it
maps to spaces. For a new photo with a busy background, remove that background
first. The original and preprocessed photos are ignored by Git; only the ASCII
SVG is published. The density ramp is ` .` followed by backtick and `:-=+*cs#%@`.
Set `STATIC=1` when running a renderer to omit its animation for a still preview.

## Refresh the contribution calendar

No extra Python packages or personal access token are needed:

```sh
python -m unittest discover -s tests -v
python scripts/fetch_contributions.py
python scripts/render_heatmap_svg.py
```

Data comes from `https://github.com/users/Varshith-eati/contributions`, the public
HTML fragment behind the profile's calendar. Tooltips supply exact counts;
`data-level` supplies GitHub's five intensity levels. This reports whatever is
publicly visible there, including anonymized private counts if you have enabled
them on your profile. It never accesses private contribution details.

The grid has 53 Sunday-first columns and seven rows. Future days are outlined,
not counted as zero-contribution days. The displayed interval may be slightly
longer than 365 days; totals and streaks explicitly refer to that interval.
Today's zero leaves yesterday's streak active until the day has finished. Monthly
totals and best day are also stored in `data/contributions.json`.

The parser requires every expected date and count, rejects duplicates and
unrecognized intensity levels, retries transient requests, and writes atomically.
Bad or incomplete HTML fails the workflow without replacing the last good art.
If GitHub changes its markup, update the parser and its tests. Use `--html` and
`--as-of YYYY-MM-DD` to check a saved HTML fragment offline.

## Daily workflow

`.github/workflows/update-profile-art.yml` runs at **06:17 UTC / 11:47 IST** daily,
on relevant changes to `main`, and from **Actions > Update profile art > Run
workflow**. GitHub can delay scheduled runs. Scheduled workflows in public repos
can also be disabled after 60 days without repository activity; re-enable the
workflow in Actions if necessary. See [GitHub's schedule documentation](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule).

It uses only the automatic `GITHUB_TOKEN` supplied to checkout to commit changed
generated files. No custom secret is needed. The public data request has no
authorization header. The workflow tests the parser, has a five-minute limit,
serializes runs, and commits only the JSON, heatmap, and info card. It never
force-pushes; a concurrent edit can safely cause a push failure and be retried.

## Design reference

Inspired by Avi Vashishta's supplied guide, *How I Built an Animated GitHub Profile
README (ASCII Portrait + Neofetch Card + Live Contribution Graph)* (July 2026).
The implementation is written for this profile: a typing monochrome portrait,
staggered neofetch card, diagonal calendar reveal, and table-based README layout.
