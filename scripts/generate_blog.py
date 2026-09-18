import os
import re
import json
import requests
from datetime import datetime, timezone
from pathlib import Path


GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
OLLAMA_API_KEY = os.environ.get("OLLAMA_API_KEY")

GITHUB_USERNAME = "shorifsimec"

POSTS_DIR = Path("_posts")
POSTS_DIR.mkdir(parents=True, exist_ok=True)


def github_get(url):
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    return response.json()


def get_repositories():
    url = (
        f"https://api.github.com/users/{GITHUB_USERNAME}/repos"
        "?per_page=100&sort=updated"
    )

    repos = github_get(url)

    return [
        repo
        for repo in repos
        if not repo.get("fork", False)
        and repo.get("name") != "shorifsimec.github.io"
    ]


def get_repo_readme(repo_name):
    url = (
        f"https://api.github.com/repos/"
        f"{GITHUB_USERNAME}/{repo_name}/readme"
    )

    try:
        data = github_get(url)

        import base64

        content = base64.b64decode(
            data["content"]
        ).decode("utf-8", errors="ignore")

        return content[:10000]

    except Exception:
        return ""


def build_repository_context(repos):
    context = []

    for repo in repos[:10]:
        readme = get_repo_readme(repo["name"])

        context.append(
            {
                "name": repo["name"],
                "description": repo.get("description"),
                "language": repo.get("language"),
                "html_url": repo.get("html_url"),
                "stars": repo.get("stargazers_count", 0),
                "updated_at": repo.get("updated_at"),
                "readme": readme,
            }
        )

    return context


def generate_with_ollama(context):
    if not OLLAMA_API_KEY:
        raise RuntimeError(
            "OLLAMA_API_KEY secret is not configured."
        )

    prompt = f"""
You are a technical blog writer.

Analyze the following GitHub repositories and create ONE useful
technical blog article.

Repositories:

{json.dumps(context, indent=2)}

Requirements:

- Write a practical developer-focused article.
- Do not invent project features.
- Only use information available in the repository data.
- Use Markdown.
- Include a clear title.
- Include an introduction.
- Explain the project or technology.
- Include useful technical details.
- Include code examples only when justified.
- Finish with a conclusion.
- Do not mention that an AI generated the article.

Return ONLY the article in Markdown.
"""

    response = requests.post(
        "https://ollama.com/api/chat",
        headers={
            "Authorization": f"Bearer {OLLAMA_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "gpt-oss:20b",
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "stream": False,
        },
        timeout=300,
    )

    response.raise_for_status()

    data = response.json()

    return data["message"]["content"]


def slugify(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"\s+", "-", text)
    return text.strip("-")


def extract_title(markdown):
    match = re.search(
        r"^#\s+(.+)$",
        markdown,
        re.MULTILINE,
    )

    if match:
        return match.group(1).strip()

    return "Daily GitHub Project Update"


def save_post(markdown):
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    title = extract_title(markdown)
    slug = slugify(title)

    if not slug:
        slug = "daily-github-project"

    filename = POSTS_DIR / f"{today}-{slug}.md"

    # Prevent duplicate posts
    if filename.exists():
        print(f"Post already exists: {filename}")
        return

    front_matter = f"""---
layout: post
title: "{title.replace('"', '\\"')}"
date: {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %z")}
categories: [github, programming]
tags: [github, programming, software-development]
---

"""

    # Remove duplicate H1 because title exists in front matter
    markdown = re.sub(
        r"^#\s+.+$\n?",
        "",
        markdown,
        count=1,
        flags=re.MULTILINE,
    )

    filename.write_text(
        front_matter + markdown.strip() + "\n",
        encoding="utf-8",
    )

    print(f"Created: {filename}")


def main():
    print("Fetching GitHub repositories...")

    repos = get_repositories()

    print(f"Found {len(repos)} repositories.")

    context = build_repository_context(repos)

    print("Generating article with Ollama...")

    article = generate_with_ollama(context)

    if not article.strip():
        raise RuntimeError("AI returned an empty article.")

    save_post(article)


if __name__ == "__main__":
    main()