# Batch GitHub Repo Verification via API

## When to Use

When you need to verify a list of GitHub repositories exists, are active, and get their stats (stars, description, language, forks). Common cases: verifying repos from a video description, article, or "awesome" list.

## Technique

Use `web_extract` pointed at the GitHub API endpoint to avoid SSL/connection issues with raw GitHub.com:

```
https://api.github.com/repos/{owner}/{repo}
```

Batch up to 5 URLs per `web_extract` call (independent = parallel):

```python
web_extract(urls=[
    "https://api.github.com/repos/freeCodeCamp/freeCodeCamp",
    "https://api.github.com/repos/codecrafters-io/build-your-own-x",
    "https://api.github.com/repos/ossu/computer-science",
    "https://api.github.com/repos/EbookFoundation/free-programming-books",
], char_limit=2500)
```

## Reading Results

The API response is JSON (truncated by web_extract at ~2,500 chars). Key fields to extract:

| Field | Meaning |
|-------|---------|
| `full_name` | owner/repo (check this matches expected — repos can transfer owners) |
| `stargazers_count` | Stars count |
| `forks_count` | Forks count |
| `description` | Short description |
| `language` | Primary language |
| `html_url` | Full GitHub URL (always the canonical one) |
| `fork` | Is this a fork of another repo? |
| `archived` | Is the repo archived (read-only)? |
| `disabled` | Is it disabled? |

To extract star counts from cached JSON, search for `stargazers_count` in the response — the number follows directly.

## Pitfalls

- **Transferred repos**: The URL `api.github.com/repos/kamranahmedse/developer-roadmap` may return `nilbuild/developer-roadmap` if the repo was transferred. The API auto-redirects. The stats are for the current repo.
- **Rate limiting**: Unauthenticated API has 60 requests/hour. 5 URLs per web_extract call = 12 calls/hour budget. 5 web_extract calls (25 repos) = fine.
- **Truncation**: For large responses, check the footer for the full-text saved path and use `read_file` to get the omitted middle.
