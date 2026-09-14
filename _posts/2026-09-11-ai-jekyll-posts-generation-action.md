---
layout: post
title: "ai-jekyll-posts-generation-action"
date: 2026-09-11 09:58:44 +0000
categories: projects
excerpt: "Automating My Portfolio: Turning Repositories into Blog Posts Maintaining a technical blog can be a..."
---

# Automating My Portfolio: Turning Repositories into Blog Posts

Maintaining a technical blog can be a daunting task. Often, the hardest part isn't the coding itself, but the effort required to document projects, write summaries, and keep a portfolio up to date. I wanted a way to bridge the gap between my active development on GitHub and my public-facing blog without spending hours manually writing updates.

To solve this, I created the **Automated Repo Article Generator**.

## What is the Automated Repo Article Generator?

The Automated Repo Article Generator is a GitHub Action designed to turn my public code repositories into high-quality blog content automatically. It scans my public repositories, analyzes the `README.md` files, and uses the power of AI to synthesize that technical documentation into a comprehensive blog article. These articles are then published directly to my Jekyll-based blog as dated markdown files in the `_posts` directory.

## How It Works

I have designed the system to be entirely "set and forget." The workflow follows a precise logic to ensure the blog remains current without creating redundant content:

1. **Repository Scanning:** The action fetches all my public, non-archived repositories.
2. **Change Detection:** It compares the last commit date of each repository against the date of any existing blog post for that project.
3. **AI Generation:** If a repository has new activity, the action sends the `README.md` content to Ollama Cloud (specifically utilizing the `gemma4:31b-cloud` model) to generate a professional article.
4. **Automated Publishing:** The generated content is formatted with Jekyll frontmatter and saved as a `_posts/YYYY-MM-DD-repo-name.md` file.
5. **Portfolio Maintenance:** To keep the blog clean, the action automatically removes posts for repositories that have been deleted.
6. **Deployment:** All new posts and deletions are committed and pushed back to the repository automatically.

## Key Features

### Smart Update Logic
I didn't want my blog to be flooded with duplicate posts. The generator includes intelligent filtering:
* **Commit-Based Updates:** It only processes repositories that have had a commit newer than the existing post.
* **Automatic Cleanup:** It synchronizes the blog with my current GitHub state by deleting posts for removed repos.
* **Validation:** It silently skips any repositories that lack a `README.md`, ensuring only documented projects are featured.

### Seamless Jekyll Integration
The output is perfectly formatted for Jekyll, including:
* **Frontmatter:** Automatic generation of layout, title, date, and categories.
* **Excerpts:** It automatically generates a 100-character excerpt for the blog's landing page.

## Potential Use Cases

This tool is ideal for several different scenarios:

* **Developer Portfolios:** If you have dozens of small projects and want a blog that automatically highlights your latest work.
* **Open Source Maintainers:** To automatically announce updates or provide high-level summaries of project changes to a non-technical audience.
* **Learning Journals:** For those who use GitHub to track their learning progress and want a mirrored blog reflecting their growth.

## Getting Started

For those looking to implement this in their own Jekyll blog, the setup is straightforward:

1. **API Key:** Obtain an API key from [Ollama Cloud](https://ollama.com) and add it to your GitHub Secrets as `OLLAMA_API_KEY`.
2. **Permissions:** Enable "Read and write permissions" in your repository's Action settings.
3. **Workflow Configuration:** Add a `.github/workflows/generate-posts.yml` file using the following configuration:

```yaml
name: Daily Repo Article Generator

on:
  schedule:
    - cron: "0 8 * * *" # Runs daily at 8 AM UTC
  workflow_dispatch:

permissions:
  contents: write

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Generate blog posts
        uses: nishadnyc/ai-jekyll-posts-generation-action@v1
        with:
          ollama-api-key: ${{ secrets.OLLAMA_API_KEY }}
```

By automating the documentation process, I can focus on writing code while my blog handles the storytelling.