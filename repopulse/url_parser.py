from urllib.parse import urlparse


def parse_github_url(url: str) -> tuple[str, str, str | None]:
    """Parse a GitHub repository URL into (owner, repo, ref).

    Supported forms:
    - https://github.com/owner/repo
    - https://github.com/owner/repo.git
    - https://github.com/owner/repo/tree/<ref>  (ref may contain /)
    - https://github.com/owner/repo/releases/tag/<tag>

    ref is None for plain repository URLs.
    """
    parsed = urlparse(url.strip())

    if parsed.scheme not in {"http", "https"} or parsed.netloc.lower() != "github.com":
        raise ValueError("Only github.com URLs are supported.")

    parts = [part for part in parsed.path.strip("/").split("/") if part]
    if len(parts) < 2:
        raise ValueError("Invalid GitHub repository URL.")

    owner = parts[0]
    repo = parts[1].removesuffix(".git")
    ref: str | None = None

    if len(parts) >= 4 and parts[2] == "tree":
        # /tree/<ref> — remaining path segments form the ref (may include /)
        ref = "/".join(parts[3:])
    elif len(parts) >= 5 and parts[2] == "releases" and parts[3] == "tag":
        # /releases/tag/<tag> — tag name may include /
        ref = "/".join(parts[4:])
    elif len(parts) == 4 and parts[2] == "releases" and parts[3] == "tag":
        raise ValueError("Invalid GitHub release tag URL: missing tag name.")
    elif len(parts) == 3 and parts[2] == "tree":
        raise ValueError("Invalid GitHub tree URL: missing ref.")

    return owner, repo, ref
