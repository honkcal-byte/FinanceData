import os
import logging
from typing import List, Optional

import requests
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from openai import OpenAI
from Dboperation import ArticleDB
import openrouter


# ----------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------
CONFIG = {
    "WP_URL": "https://chinamarketsnow.com/wp-json/wp/v2/posts",
    "WP_USER": "writedatauser",
    "WP_PASSWORD": "sVec PTjy FsGY Tk7E uwMs 5ISh",
    "DEFAULT_CATEGORY_ID": 2,
    "REQUEST_TIMEOUT": 20,
}

OPENROUTER = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
)

logging.basicConfig(
    filename="crawler.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

db=  ArticleDB("207.148.127.78","haawjkxnuy","QbeufDdc59","haawjkxnuy")


# ----------------------------------------------------------------------
# FETCH ARTICLE HTML
# ----------------------------------------------------------------------
def fetch_article_html(url: str) -> str:
    logging.info(f"Fetching URL: {url}")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            )
        )

        page.goto(url, timeout=60000)
        page.wait_for_load_state("networkidle")

        # 再多等 2 秒，防止 JS 没渲染完
        page.wait_for_timeout(2000)

        html = page.content()
        browser.close()
        return html


# ----------------------------------------------------------------------
# PARSE
# ----------------------------------------------------------------------
def parse_article(html: str) -> Optional[tuple]:
    soup = BeautifulSoup(html, "html.parser")

    # Title
    title_tag = soup.find("title")
    title = title_tag.text.strip() if title_tag else None

    # Summary
    summary_tag = soup.find("pre", class_="detail-brief")
    summary = summary_tag.text.strip() if summary_tag else ""

    # Content
    content_div = soup.find("div", class_="detail-content")
    if not content_div:
        logging.error("Article content_div missing.")
        return None, None

    paragraphs = [
        p.get_text(strip=True)
        for p in content_div.find_all("p")
        if p.get_text(strip=True)
    ]

    content = "\n".join(paragraphs)

    if not title or not content:
        return None, None

    return title, content


# ----------------------------------------------------------------------
# REWRITE USING OPENROUTER
# ----------------------------------------------------------------------
def rewrite_to_english(title: str, content: str) -> str:
    prompt = f"""
Rewrite the following Chinese financial news into fluent, professional English 
suitable for global investors. Keep key facts, numbers, and context intact.
Return output in clean HTML paragraphs (<p>...</p>).

=== Original Title ===
{title}

=== Original Content ===
{content}
"""

    try:
        resp = OPENROUTER.chat.completions.create(
            model="tngtech/deepseek-r1t2-chimera:free",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=3500,
        )

        result = resp.choices[0].message.content

        logging.info(f"Rewrite success, tokens={resp.usage.total_tokens}")
        return result

    except Exception as e:
        logging.error(f"Rewrite failed: {e}")
        return f"<p>Translation failed: {e}</p>"


# ----------------------------------------------------------------------
# PUBLISH TO WORDPRESS
# ----------------------------------------------------------------------
def publish_to_wordpress(title: str, html_content: str):
    data = {
        "title": title,
        "content": html_content,
        "status": "publish",
        "categories": [CONFIG["DEFAULT_CATEGORY_ID"]],
    }

    try:
        resp = requests.post(
            CONFIG["WP_URL"],
            auth=HTTPBasicAuth(CONFIG["WP_USER"], CONFIG["WP_PASSWORD"]),
            json=data,
            timeout=CONFIG["REQUEST_TIMEOUT"],
        )
        if resp.status_code >= 300:
            logging.error(f"WP publish failed: {resp.status_code}, {resp.text}")
            print("WordPress error:", resp.text)
            return None

        print("Published:", resp.json())
        return resp.json()

    except Exception as e:
        logging.error(f"Publish exception: {e}")
        print("Exception:", e)
        return None


# ----------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------
if __name__ == "__main__":
    targeturl = "https://www.cls.cn/detail/2226742"

    html = fetch_article_html(targeturl)
    title, content = parse_article(html)

    if title:
        print("Parse OK:", title)
        en_content = rewrite_to_english(title, content)

        new_id = db.add_article(
            source="Reuters",
            url=targeturl,
            title="title",
            content="content"
        )
        print("Inserted to db successfully:", new_id)

        publish_to_wordpress(title, en_content)
    else:
        print("Parse failed")
        logging.error("Parse returned empty title/content")
