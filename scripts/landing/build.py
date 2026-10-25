#!/usr/bin/env python3
"""Build the Humboldt landing page in two forms from template.html:
   artifact.html  - Claude-hosted page (the host adds the document skeleton)
   index.html     - full standalone document for madbullahi.github.io/humboldt/
Usage: python3 -I build.py <template.html> <icons dir> <artifact out> <github out>
"""
import html, json, re, sys

FAQ = [
    ("What is the aim of the project?",
     "To find out how well a treatment step built on <i>Daphnia</i> removes bacterial and viral pathogens from reclaimed water, alongside the chemicals it already removes, while keeping that step low in cost and carbon."),
    ("Who funds it, and where is it based?",
     "The Alexander von Humboldt Foundation funds it through a Research Fellowship for Postdocs hosted at Goethe University Frankfurt. Muhammad is currently on a research visit at the University of Birmingham."),
    ("Why use <i>Daphnia</i>?",
     "<i>Daphnia</i> are small freshwater crustaceans that feed by filtering the water around them. They are among the best studied animals in ecotoxicology, so their responses to pollutants are well understood."),
    ("Has the approach worked outside the lab?",
     "Yes, for chemicals. A four week mesocosm trial in real wastewater removed pharmaceuticals, and the technology has since moved to commercial demonstration through Daphne Water Solutions."),
    ("Does it remove pathogens yet?",
     "That is the question this project answers. Results will be shared through publications and on the <a href=\"https://madbullahi.github.io/#humboldt\" target=\"_top\">project log</a> as they come in."),
    ("Who should get in touch?",
     "Water utilities and treatment plant operators, microbiologists and virologists, funders, and researchers working on water reuse or antimicrobial resistance."),
    ("What could a collaboration look like?",
     "Joint funding applications, an exchange of samples or data, a pilot trial at a treatment site, or shared analysis of pathogen and resistance data."),
    ("Where can I follow progress?",
     "On the project log and the publication list at <a href=\"https://madbullahi.github.io/\" target=\"_top\">madbullahi.github.io</a>."),
]

TITLE = "Daphnia water treatment for pathogen removal"
DESC = ("A Humboldt Fellowship project testing how far a low carbon treatment step built on Daphnia "
        "removes bacterial and viral pathogens and chemicals from reclaimed water.")
FONT = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700&display=swap">\n')
ICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='8' fill='%230A0A0A'/%3E"
        "%3Ctext x='16' y='21' font-family='Arial,sans-serif' font-weight='700' font-size='13' fill='white' text-anchor='middle'%3EMA%3C/text%3E%3C/svg%3E")


def main(tpl_path, icons, art_out, gh_out):
    tpl = open(tpl_path, encoding="utf-8").read()

    def icon(m):
        svg = open(f"{icons}/{m.group(1)}.svg", encoding="utf-8").read().strip()
        return svg.replace("<svg ", '<svg class="ico" aria-hidden="true" focusable="false" ', 1)
    tpl = re.sub(r"\{\{icon:([a-z-]+)\}\}", icon, tpl)

    caret = icon(re.match(r"(.*)", "caret-down"))
    faq_html = "\n        ".join(
        f'<details class="reveal"><summary><span>{q}</span>{caret}</summary><div class="a"><p>{a}</p></div></details>' for q, a in FAQ)
    tpl = tpl.replace("{{faq}}", faq_html)
    assert "{{" not in tpl, "unfilled placeholder"

    plain = lambda s: html.unescape(re.sub(r"<[^>]+>", "", s))
    ld = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": plain(q), "acceptedAnswer": {"@type": "Answer", "text": plain(a)}} for q, a in FAQ]},
        ensure_ascii=False).replace("<", "\\u003c")

    # Claude-hosted version: the host wraps it in a document skeleton.
    art = (f"<title>Humboldt Daphnia Project</title>\n<meta name=\"claude:viewport-fit-sides\" content=\"cover\">\n"
           f"<meta name=\"description\" content=\"{DESC}\">\n{FONT}{tpl}\n")
    open(art_out, "w", encoding="utf-8").write(art)

    url = "https://madbullahi.github.io/humboldt/"
    gh = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{TITLE} | Muhammad Abdullahi</title>
<meta name="description" content="{DESC}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{TITLE}">
<meta property="og:description" content="{DESC}">
<meta property="og:image" content="{url}og.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{TITLE}">
<meta name="twitter:description" content="{DESC}">
<meta name="twitter:image" content="{url}og.png">
<link rel="icon" href="{ICON}">
{FONT}<style>:root {{ padding-top: env(safe-area-inset-top, 0px); padding-bottom: env(safe-area-inset-bottom, 0px); }}</style>
<script type="application/ld+json">{ld}</script>
</head>
<body>
{tpl}
</body>
</html>
"""
    open(gh_out, "w", encoding="utf-8").write(gh)
    print("built", art_out, gh_out)


if __name__ == "__main__":
    main(*sys.argv[1:5])
