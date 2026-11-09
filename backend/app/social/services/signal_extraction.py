"""Signal extraction — extract structured fields from raw post text."""

from __future__ import annotations

import re

from app.social.utils.signal_detection import (
    CONTACT_PHRASES,
    INDIRECT_SIGNAL_PHRASES,
    PRIMARY_HIRING_PHRASES,
    normalize,
)

TECH_ROLE_KEYWORDS = [
    "engineer",
    "developer",
    "intern",
    "developer intern",
    "engineering intern",
    "software",
    "backend",
    "frontend",
    "full stack",
    "ml",
    "ai",
    "data",
    "devops",
    "cloud",
    "security",
    "cybersecurity",
    "security engineer",
    "sre",
    "site reliability",
    "qa",
    "tester",
]

SKILL_KEYWORDS = [
    "python", "javascript", "typescript", "java", "go", "rust", "cpp",
    "react", "angular", "vue", "node.js", "django", "flask", "spring",
    "pytorch", "tensorflow", "keras", "scikit-learn", "huggingface",
    "aws", "gcp", "azure", "docker", "kubernetes", "terraform",
    "git", "github", "ci/cd", "linux", "bash", "sql", "postgresql",
    "mongodb", "redis", "graphql", "rest", "openai", "llm",
    "agent", "machine learning", "deep learning", "nlp", "cloud",
    "devops", "infrastructure", "kafka", "elasticsearch", "c++",
]


def detect_company(post_text: str) -> str | None:
    """Attempt to identify the company name from post text."""
    normalized = normalize(post_text)
    match = re.search(r"at\s+([a-z0-9.\-]+)", normalized)
    if match:
        return match.group(1).strip()
    match = re.search(r"(?:from|of)\s+([a-z0-9.\-]+)", normalized)
    if match:
        return match.group(1).strip()
    match = re.search(r"https?://([a-z0-9.\-]+)\.", normalized)
    if match:
        return match.group(1).strip()
    return None


def detect_author(post_text: str, author: str | None = None) -> str | None:
    """Attempt to extract author name."""
    if author:
        return author
    match = re.search(r"posted\s+by\s+([^.,!?]+)", post_text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    match = re.search(r"from\s+([^.,!?]+)", post_text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None


def extract_roles(post_text: str) -> str | None:
    """Attempt to extract mentioned role from post text."""
    normalized = normalize(post_text)
    for role in TECH_ROLE_KEYWORDS:
        if role in normalized:
            return role
    return None


def extract_skills(post_text: str) -> list[str]:
    """Extract mentioned skills from post text."""
    normalized = normalize(post_text)
    skills: list[str] = []
    for skill in SKILL_KEYWORDS:
        if skill in normalized:
            skills.append(skill)
    return skills[:10]


def extract_stipend(post_text: str) -> str | None:
    """Attempt to extract mentioned stipend from post text."""
    normalized = normalize(post_text)
    match = re.search(r"(\$?\d+)\s*(lpa|annual|month|pa|per\s*month)", normalized)
    if match:
        return match.group(0)
    match = re.search(r"stipend\s+of\s+([^.,!?]+)", normalized)
    if match:
        return match.group(1).strip()
    return None


def extract_remote(post_text: str) -> str | None:
    """Attempt to extract mentioned remote eligibility."""
    normalized = normalize(post_text)
    if "remote" in normalized or "work from anywhere" in normalized:
        return "remote"
    if "onsite" in normalized:
        return "onsite"
    if "hybrid" in normalized:
        return "hybrid"
    return None


def extract_contact_instructions(post_text: str) -> str | None:
    """Extract contact instructions from post text."""
    normalized = normalize(post_text)
    for phrase in CONTACT_PHRASES:
        if phrase in normalized:
            idx = normalized.find(phrase)
            context = post_text[max(0, idx - 50): idx + 100].strip()
            return context[:150]
    return None


def is_indirect_signal(post_text: str) -> bool:
    """Check if the post contains only indirect signal phrases."""
    normalized = normalize(post_text)
    for phrase in INDIRECT_SIGNAL_PHRASES:
        if phrase in normalized:
            return True
    return False


def compute_confidence(
    *,
    post_text: str,
    primary_match: bool,
    company_detected: bool,
    is_indirect: bool,
    has_contact: bool,
) -> float:
    """Compute a confidence score for the signal."""
    score = 0.5  # Baseline
    if primary_match:
        score += 0.3
    if company_detected:
        score += 0.1
    if is_indirect:
        score -= 0.2  # Indirect signals are less confident as vacancies
    if has_contact:
        score += 0.1
    return min(1.0, max(0.0, score))
