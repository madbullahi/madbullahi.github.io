#!/usr/bin/env python3
"""Build the Humboldt landing page in two forms from template.html:
   artifact.html  - Claude-hosted page (the host adds the document skeleton)
   index.html     - full standalone document for madbullahi.github.io/humboldt/
Usage: python3 -I build.py <template.html> <icons dir> <artifact out> <github out> [<saved live site page>]
The optional last argument is the main website's page (https://claude.ai/artifact/4TKo2VvsTrtr93AnAwqn49,
saved with the Artifact tool); its site-data JSON fills the "Latest from the project" section.
"""
import datetime, html, json, re, sys

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
LOG_URL = "https://madbullahi.github.io/#humboldt"


def fmt_date(d):
    m = re.match(r"^(\d{4})-(\d{2})(?:-(\d{2}))?$", d or "")
    if not m:
        return html.escape(d or "")
    return (f"{int(m.group(3))} " if m.group(3) else "") + f"{MONTHS[int(m.group(2)) - 1]} {m.group(1)}"


def species(s):
    return re.sub(r"\b(Daphnia magna|Daphnia)\b", r"<i>\1</i>", html.escape(s))


def latest_html(site_path, icon):
    if not site_path:
        entries = []
    else:
        live = open(site_path, encoding="utf-8").read()
        m = re.search(r'<script type="application/json" id="site-data">\s*(.*?)\s*</script>', live, re.S)
        if not m:
            sys.exit("build: no site-data JSON in the live page")
        entries = json.loads(m.group(1)).get("log", [])
    entries = sorted(entries, key=lambda e: str(e.get("date", "")), reverse=True)[:3]
    if not entries:
        return ('<div class="updates-empty reveal"><h3>First results are on their way</h3>'
                f'<p>Experiments, protocols and results will appear here as they are posted to the project log.</p>'
                f'<a class="btn btn-ghost btn-sm" href="{LOG_URL}" target="_top">Open the project log</a></div>')
    items = []
    for e in entries:
        text = str(e.get("text", "")).strip().split("\n\n")[0]
        if len(text) > 240:
            text = text[:240].rsplit(" ", 1)[0] + "…"
        link = e.get("link") if re.match(r"^https?://", str(e.get("link", ""))) else ""
        more = (f'<a class="more" href="{html.escape(link)}" target="_blank" rel="noopener">{html.escape(e.get("linkLabel") or "Read more")} {icon("arrow-up-right")}</a>'
                if link else f'<a class="more" href="{LOG_URL}" target="_top">Read on the project log {icon("arrow-up-right")}</a>')
        items.append(f'<li class="reveal"><span class="head">{html.escape(str(e.get("type", "Update")))} · {fmt_date(e.get("date"))}</span>'
                     f'<h3>{species(str(e.get("title", "")))}</h3>' + (f'<p>{species(text)}</p>' if text else "") + more + '</li>')
    cls = "updates one" if len(items) == 1 else "updates"
    return f'<ul class="{cls}">' + "".join(items) + "</ul>"

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


def main(tpl_path, icons, art_out, gh_out, site_path=None):
    tpl = open(tpl_path, encoding="utf-8").read()

    def svg(name):
        s = open(f"{icons}/{name}.svg", encoding="utf-8").read().strip()
        return s.replace("<svg ", '<svg class="ico" aria-hidden="true" focusable="false" ', 1)
    tpl = re.sub(r"\{\{icon:([a-z-]+)\}\}", lambda m: svg(m.group(1)), tpl)
    tpl = tpl.replace("{{latest}}", latest_html(site_path, svg))
    t = datetime.date.today()
    tpl = tpl.replace("{{refreshed}}", f"{t.day} {MONTHS[t.month - 1]} {t.year}")

    caret = svg("caret-down")
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
    if len(sys.argv) not in (5, 6):
        sys.exit(__doc__)
    main(*sys.argv[1:6])
