from typing import Any

import httpx

from app.crawlers import crawl_site


async def task(payload: Any):
    settings = {s.label: s.default for s in payload.settings}
    root_url = settings.get("root_url", "").strip()
    if not root_url:
        report = "Root URL is required"
    else:
        try:
            crawl_depth = int(settings.get("crawl_depth", 2))
        except ValueError:
            crawl_depth = 2
        required_meta_tags_str = settings.get(
            "required_meta_tags", "title,meta description"
        )

        required_meta_tags = [
            tag.strip()
            for tag in required_meta_tags_str.split(",")
            if tag.strip()
        ]
        result = await crawl_site(root_url, crawl_depth, required_meta_tags)
        report_lines = []
        if result["broken_links"]:
            report_lines.append(
                f"Broken links: {', '.join(result['broken_links'])}"
            )
        if result["meta_issues"]:
            report_lines.append("Meta issues:")
            for url, errors in result["meta_issues"].items():
                report_lines.append(f" - {url}: {', '.join(errors)}")

        if not report_lines:
            report_lines.append("No issues found")
        report = "\n".join(report_lines)

    telex_format = {
        "message": report,
        "username": "Link Inspector",
        "event_name": "Site Crawl Report",
        "status": (
            "error"
            if "Broken Links:" in report or "Meta Tag Issues:" in report
            else "success"
        ),
    }

    headers = {"Content-Type": "application/json"}

    async with httpx.AsyncClient() as client:
        await client.post(
            payload.return_url, json=telex_format, headers=headers
        )
