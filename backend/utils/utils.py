import hashlib
import re
from bs4 import BeautifulSoup
import difflib


# ----------------------------
# HTML Cleaning & Hashing
# ----------------------------
def clean_html(html: str) -> str:
    """
    Cleans HTML content:
    - Removes scripts, styles, and comments
    - Extracts visible text
    - Collapses multiple spaces/newlines
    """
    soup = BeautifulSoup(html, "html.parser")

    # Remove script and style tags
    for tag in soup(["script", "style"]):
        tag.extract()

    # Get text only
    text = soup.get_text(separator=" ")

    # Collapse multiple spaces and newlines
    text = re.sub(r"\s+", " ", text).strip()

    return text


def hash_content(content: str) -> str:
    """
    Creates a SHA256 hash of cleaned content.
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def clean_and_hash(html: str) -> tuple[str, str]:
    """
    Cleans HTML and returns both the cleaned text and its hash.
    """
    cleaned = clean_html(html)
    hashed = hash_content(cleaned)
    return cleaned, hashed


# ----------------------------
# Diffing
# ----------------------------
def diff_text(old_text: str, new_text: str) -> str:
    """
    Returns a unified diff between old_text and new_text.
    """
    old_lines = old_text.splitlines()
    new_lines = new_text.splitlines()

    diff = difflib.unified_diff(
        old_lines,
        new_lines,
        fromfile="old",
        tofile="new",
        lineterm="",
    )

    return "\n".join(diff)


def get_diff_html(old_html: str, new_html: str) -> str:
    """
    Helper to clean HTML first, then compute diff.
    """
    old_clean = clean_html(old_html)
    new_clean = clean_html(new_html)
    return diff_text(old_clean, new_clean)

def detect_changes(old_text: str, new_text: str) -> dict:
    """
    Returns a summary dict with:
    - old_hash
    - new_hash
    - diff
    """
    old_hash = hash_content(old_text)
    new_hash = hash_content(new_text)
    diff = diff_text(old_text, new_text)
    return {
        "old_hash": old_hash,
        "new_hash": new_hash,
        "diff": diff,
        "changed": old_hash != new_hash
    }