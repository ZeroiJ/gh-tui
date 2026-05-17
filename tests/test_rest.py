from gh_tui.api.rest import parse_repo, parse_search_results


def test_parse_repo():
  data = {
    "full_name": "octocat/Hello-World",
    "description": "My first repo",
    "stargazers_count": 100,
    "forks_count": 20,
    "subscribers_count": 5,
    "language": "Python",
    "license": {"spdx_id": "MIT"},
    "html_url": "https://github.com/octocat/Hello-World",
    "default_branch": "main",
    "updated_at": "2024-01-01T00:00:00Z",
    "open_issues_count": 3,
    "private": False,
  }
  repo = parse_repo(data)
  assert repo.full_name == "octocat/Hello-World"
  assert repo.stars == 100
  assert repo.license_name == "MIT"


def test_parse_search():
  data = {
    "items": [
      {
        "full_name": "facebook/react",
        "description": "React",
        "stargazers_count": 200000,
        "language": "JavaScript",
        "html_url": "https://github.com/facebook/react",
      }
    ]
  }
  results = parse_search_results(data)
  assert len(results) == 1
  assert results[0].full_name == "facebook/react"
