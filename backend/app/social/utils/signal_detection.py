"""Signal detection utilities — phrase matching for hiring signals."""

from __future__ import annotations

import re

# Primary hiring signal phrases (exact / near-exact matches)
PRIMARY_HIRING_PHRASES = [
    "we're hiring interns",
    "we are hiring interns",
    "hiring interns",
    "looking for engineering interns",
    "looking for interns",
    "dm me your resume",
    "dm me your cv",
    "building our engineering team",
    "looking for talented developers",
    "need someone to work on our ai platform",
    "students welcome",
    "open to freshers",
    "founding engineer",
    "founding engineers",
    "hiring for our upcoming product",
    "internship openings",
    "looking for contributors who can join our team",
    "we're looking for interns",
    "we are looking for interns",
    "seeking engineering interns",
    "seeking interns",
    "hiring for internships",
    "looking for interns for",
    "hiring fresh graduates",
    "open to student interns",
    "looking for junior developers",
    "hiring junior engineers",
    "looking for backend interns",
    "looking for frontend interns",
    "looking for full stack interns",
    "looking for ml interns",
    "looking for ai interns",
]

# Indirect signal phrases (must never be represented as confirmed vacancies)
INDIRECT_SIGNAL_PHRASES = [
    "recently raised funding",
    "funded",
    "raised",
    "new engineering team",
    "establishing engineering team",
    "new product launch",
    "product expansion",
    "expansion",
    "hiring multiple engineers",
    "hiring several engineers",
    "joining our team",
    "join our team",
    "building a team",
    "hiring for growth",
    "scaling engineering",
    "new product requiring engineering",
    "engineering resources",
]

# Contact / DM instruction phrases
CONTACT_PHRASES = [
    "dm me",
    "dm me your resume",
    "dm your resume",
    "send me your resume",
    "email me at",
    "reach out to me",
    "messenger",
    "whatsapp",
]

# Role / domain keywords for classification
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


def normalize(text: str) -> str:
    """Normalize text for signal matching: lowercase, collapse whitespace, strip punctuation."""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\s]", " ", text)
    return text.strip()


def detect_signal_type(post_text: str) -> str:
    """Classify the signal type from post text."""
    normalized = normalize(post_text)
    for phrase in PRIMARY_HIRING_PHRASES:
        if phrase in normalized:
            if "intern" in normalized or "student" in normalized:
                return "internship_post"
            if "engineering" in normalized or "engineer" in normalized:
                return "engineering_follower_post"
            if "hiring" in normalized and "team" in normalized:
                return "team_hiring_post"
            return "hiring_post"
    for phrase in INDIRECT_SIGNAL_PHRASES:
        if phrase in normalized:
            return "indirect_signal"
    return "unknown"


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
    skill_keywords = [
        "python", "javascript", "typescript", "java", "go", "rust", "cpp",
        "react", "angular", "vue", "node.js", "django", "flask", "spring",
        "pytorch", "tensorflow", "keras", "scikit-learn", "huggingface",
        "aws", "gcp", "azure", "docker", "kubernetes", "terraform",
        "git", "github", "ci/cd", "linux", "bash", "sql", "postgresql",
        "mongodb", "redis", "graphql", "rest", "openai", "llm",
        "agent", "machine learning", "deep learning", "nlp", "cloud",
        "devops", "infrastructure", "kafka", "elasticsearch", "c++",
    ]
    for skill in skill_keywords:
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
