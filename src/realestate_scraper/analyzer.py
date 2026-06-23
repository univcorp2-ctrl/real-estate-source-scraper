from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from realestate_scraper.extract import clean_text
from realestate_scraper.models import Source
from realestate_scraper.plugins import get_plugin

DEFAULT_USER_AGENT = "RealEstateResearchBot/0.1 (+https://github.com/)"


@dataclass
class HtmlStructureSummary:
    title: str = ""
    h1: list[str] = field(default_factory=list)
    h2: list[str] = field(default_factory=list)
    forms: list[dict[str, str]] = field(default_factory=list)
    json_ld_count: int = 0
    link_count: int = 0
    same_host_link_count: int = 0
    likely_detail_links: list[str] = field(default_factory=list)
    detected_labels: list[str] = field(default_factory=list)


@dataclass
class RobotsSummary:
    robots_url: str
    fetch_status: str
    disallow_count: int = 0
    allow_count: int = 0
    crawl_delay: str = ""
    important_rules: list[str] = field(default_factory=list)


@dataclass
class SiteAnalysis:
    source_id: str
    source_name: str
    base_url: str
    review_status: str
    plugin_id: str
    implementation_status: str
    robots: RobotsSummary
    structure: HtmlStructureSummary | None
    notes: str


def summarize_html_structure(html: str, base_url: str, detail_patterns: list[str]) -> HtmlStructureSummary:
    soup = BeautifulSoup(html, "html.parser")
    title = clean_text(soup.title.string) if soup.title and soup.title.string else ""
    h1 = [clean_text(node.get_text(" ", strip=True)) for node in soup.find_all("h1")[:5]]
    h2 = [clean_text(node.get_text(" ", strip=True)) for node in soup.find_all("h2")[:8]]
    forms: list[dict[str, str]] = []
    for form in soup.find_all("form")[:10]:
        forms.append(
            {
                "method": str(form.get("method", "get")).upper(),
                "action": urljoin(base_url, str(form.get("action", ""))),
                "input_count": str(len(form.find_all(["input", "select", "textarea"]))),
            }
        )
    same_host = 0
    links: list[str] = []
    base_host = urlparse(base_url).netloc
    compiled = [re.compile(pattern) for pattern in detail_patterns]
    for anchor in soup.find_all("a", href=True):
        url = urljoin(base_url, str(anchor.get("href")))
        if urlparse(url).netloc == base_host:
            same_host += 1
        if compiled and any(pattern.search(url) for pattern in compiled) and url not in links:
            links.append(url)
    labels = detect_common_labels(soup)
    return HtmlStructureSummary(
        title=title,
        h1=[value for value in h1 if value],
        h2=[value for value in h2 if value],
        forms=forms,
        json_ld_count=len(soup.select("script[type='application/ld+json']")),
        link_count=len(soup.find_all("a", href=True)),
        same_host_link_count=same_host,
        likely_detail_links=links[:20],
        detected_labels=labels[:30],
    )


def detect_common_labels(soup: BeautifulSoup) -> list[str]:
    labels: list[str] = []
    keywords = ["価格", "賃料", "利回り", "所在地", "交通", "面積", "築", "Price", "Rent", "Address", "Area"]
    for node in soup.find_all(["dt", "th", "label", "span", "div"]):
        text = clean_text(node.get_text(" ", strip=True))
        if 1 <= len(text) <= 28 and any(keyword in text for keyword in keywords):
            if text not in labels:
                labels.append(text)
    return labels


def summarize_robots_text(robots_url: str, text: str, status_code: int) -> RobotsSummary:
    if status_code == 404:
        return RobotsSummary(robots_url=robots_url, fetch_status="missing_404")
    if status_code >= 400:
        return RobotsSummary(robots_url=robots_url, fetch_status=f"http_{status_code}")
    lines = [line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith("#")]
    disallows = [line for line in lines if line.lower().startswith("disallow:")]
    allows = [line for line in lines if line.lower().startswith("allow:")]
    crawl_delay = ""
    for line in lines:
        if line.lower().startswith("crawl-delay:"):
            crawl_delay = line.split(":", 1)[1].strip()
            break
    important: list[str] = []
    for line in lines:
        lower = line.lower()
        if any(token in lower for token in ["disallow", "crawl-delay", "sitemap", "api", "search", "sort", "login"]):
            important.append(line)
        if len(important) >= 20:
            break
    return RobotsSummary(
        robots_url=robots_url,
        fetch_status="ok",
        disallow_count=len(disallows),
        allow_count=len(allows),
        crawl_delay=crawl_delay,
        important_rules=important,
    )


def analyze_source(source: Source, timeout: float = 20.0, fetch_html: bool = True) -> SiteAnalysis:
    user_agent = os.getenv("REAL_ESTATE_SCRAPER_USER_AGENT", DEFAULT_USER_AGENT)
    plugin = get_plugin(source.id)
    parsed = urlparse(source.base_url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    robots = RobotsSummary(robots_url=robots_url, fetch_status="not_checked")
    structure: HtmlStructureSummary | None = None
    headers = {"User-Agent": user_agent, "Accept-Language": "ja,en;q=0.8"}
    with httpx.Client(timeout=timeout, follow_redirects=True, headers=headers) as client:
        try:
            response = client.get(robots_url)
            robots = summarize_robots_text(robots_url, response.text, response.status_code)
        except httpx.HTTPError as exc:
            robots = RobotsSummary(robots_url=robots_url, fetch_status=f"error:{exc.__class__.__name__}")
        if fetch_html and source.seed_urls:
            try:
                html_response = client.get(source.seed_urls[0])
                if html_response.status_code < 400 and "html" in html_response.headers.get("content-type", ""):
                    structure = summarize_html_structure(
                        html_response.text,
                        source.seed_urls[0],
                        list(plugin.detail_url_patterns or tuple(source.item_url_patterns)),
                    )
            except httpx.HTTPError:
                structure = None
    status = "plugin_ready" if plugin.plugin_id != "generic" else "generic_ready"
    if source.review_status in {"research_only", "blocked"}:
        status = "not_scraped_research_only"
    if source.scrape_strategy in {"api_or_data_download", "metadata_only"}:
        status = "api_or_metadata_connector"
    return SiteAnalysis(
        source_id=source.id,
        source_name=source.name,
        base_url=source.base_url,
        review_status=source.review_status,
        plugin_id=plugin.plugin_id,
        implementation_status=status,
        robots=robots,
        structure=structure,
        notes=plugin.notes or source.notes,
    )


def write_site_analysis(analyses: list[SiteAnalysis], output_dir: str | Path) -> dict[str, str]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "site_analysis.json"
    md_path = output_dir / "site_analysis.md"
    json_path.write_text(json.dumps([asdict(item) for item in analyses], ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_site_analysis_markdown(analyses), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def render_site_analysis_markdown(analyses: list[SiteAnalysis]) -> str:
    lines = [
        "# Generated Site Analysis",
        "",
        "Generated by `python -m realestate_scraper analyze-sites`. It records robots.txt summaries, seed-page structure, plugin coverage, and implementation status.",
        "",
        "| source | plugin | status | robots | disallow | crawl-delay | forms | likely detail links |",
        "|---|---|---|---|---:|---|---:|---:|",
    ]
    for item in analyses:
        forms = len(item.structure.forms) if item.structure else 0
        links = len(item.structure.likely_detail_links) if item.structure else 0
        lines.append(
            f"| {item.source_id} | {item.plugin_id} | {item.implementation_status} | {item.robots.fetch_status} | {item.robots.disallow_count} | {item.robots.crawl_delay or '-'} | {forms} | {links} |"
        )
    lines.append("")
    for item in analyses:
        lines.extend(
            [
                f"## {item.source_name} (`{item.source_id}`)",
                "",
                f"- Base URL: {item.base_url}",
                f"- Plugin: `{item.plugin_id}`",
                f"- Review status: `{item.review_status}`",
                f"- Implementation status: `{item.implementation_status}`",
                f"- robots.txt: `{item.robots.fetch_status}` at {item.robots.robots_url}",
                f"- Disallow count: {item.robots.disallow_count}",
                f"- Crawl-delay: {item.robots.crawl_delay or '-'}",
                f"- Notes: {item.notes}",
                "",
            ]
        )
        if item.robots.important_rules:
            lines.append("Important robots rules observed:")
            lines.append("")
            for rule in item.robots.important_rules[:10]:
                lines.append(f"- `{rule}`")
            lines.append("")
        if item.structure:
            lines.extend(
                [
                    f"- Title: {item.structure.title or '-'}",
                    f"- H1: {', '.join(item.structure.h1) if item.structure.h1 else '-'}",
                    f"- Forms: {len(item.structure.forms)}",
                    f"- JSON-LD blocks: {item.structure.json_ld_count}",
                    f"- Links: {item.structure.link_count} total / {item.structure.same_host_link_count} same-host",
                    f"- Detected labels: {', '.join(item.structure.detected_labels[:12]) if item.structure.detected_labels else '-'}",
                    "",
                ]
            )
            if item.structure.likely_detail_links:
                lines.append("Likely detail-link samples:")
                lines.append("")
                for link in item.structure.likely_detail_links[:8]:
                    lines.append(f"- {link}")
                lines.append("")
    return "\n".join(lines)
