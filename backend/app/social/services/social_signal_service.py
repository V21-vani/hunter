"""Social signal service — converts raw social posts to structured SocialSignal objects.

The service:
1. Takes raw post data from adapters.
2. Runs signal detection (primary + indirect phrases).
3. Extracts structured fields (company, author, role, skills, stipend, remote, contact).
4. Classifies as primary hiring signal or indirect signal.
5. Computes confidence score.
6. Marks verification status as 'social_lead_not_verified' (required by Phase 3).
7. Persists via the database layer.
"""

from typing import Any

from app.core.logging import get_logger
from app.social.models.social_signal import SocialSignal
from app.db.repositories.social_signal_repository import SocialSignalRepository
from app.social.services.signal_classification import classify_signal
from app.social.services.signal_extraction import (
    detect_author,
    detect_company,
    extract_contact_instructions,
    extract_roles,
    extract_skills,
    extract_stipend,
    extract_remote,
    is_indirect_signal,
    compute_confidence,
)

logger = get_logger(__name__)


class SocialSignalService:
    """Service for processing raw social posts into structured signals."""

    def __init__(self, session, repository=None):
        self.session = session
        self.repo = repository or SocialSignalRepository(session)

    def process_raw_post(self, raw_post: dict[str, Any]) -> SocialSignal:
        """Convert a raw post dict into a persistent SocialSignal."""
        # Extract fields from raw post
        post_id = raw_post.get("post_id") or raw_post.get("id") or ""
        post_text = raw_post.get("post_text") or raw_post.get("content") or ""
        post_url = raw_post.get("post_url") or raw_post.get("url") or ""
        post_date = raw_post.get("post_date") or raw_post.get("date")

        author = raw_post.get("author")
        author_role = raw_post.get("author_role")

        # Signal detection
        signal_type = classify_signal(post_text)
        is_indirect = is_indirect_signal(post_text)

        # Entity extraction
        company = detect_company(post_text) or raw_post.get("company")
        author = detect_author(post_text, author)
        author_role = extract_roles(post_text) or author_role

        # Field extraction
        mentioned_role = extract_roles(post_text)
        mentioned_stipend = extract_stipend(post_text)
        mentioned_remote = extract_remote(post_text)
        mentioned_skills = extract_skills(post_text)
        contact_instructions = extract_contact_instructions(post_text)

        # Determine verification status
        verification_status = self._determine_verification_status(
            post_text, signal_type, is_indirect, company
        )

        # Compute confidence
        primary_match = signal_type != "unknown"
        company_detected = bool(company or detect_company(post_text))
        confidence = compute_confidence(
            post_text=post_text,
            primary_match=primary_match,
            company_detected=company_detected,
            is_indirect=is_indirect,
            has_contact=bool(contact_instructions),
        )

        # Build signal
        signal = SocialSignal(
            platform=raw_post.get("platform", "unknown"),
            post_id=post_id,
            post_text=post_text[:2000],
            post_url=post_url,
            post_date=post_date,
            author=author,
            author_role=author_role,
            signal_type=signal_type,
            company=company,
            mentioned_role=mentioned_role,
            mentioned_stipend=mentioned_stipend,
            mentioned_remote=mentioned_remote,
            mentioned_skills=mentioned_skills,
            contact_instructions=contact_instructions,
            confidence_score=confidence,
            verification_status=verification_status,
            verification_evidence={"raw_post": raw_post},
            is_indirect_signal=is_indirect,
        )

        self.repo.create(self.session, signal)
        logger.info(
            "Social signal processed",
            platform=signal.platform,
            post_id=signal.post_id,
            company=signal.company,
            verification_status=signal.verification_status,
        )
        return signal

    def process_batch(self, raw_posts: list[dict[str, Any]]) -> list:
        """Process a batch of raw posts into signals."""
        signals = []
        for post in raw_posts:
            signal = self.process_raw_post(post)
            signals.append(signal)
        return signals

    def _determine_verification_status(
        self,
        post_text: str,
        signal_type: str,
        is_indirect: bool,
        company: str | None,
    ) -> str:
        """Determine verification status per Phase 3 requirements.

        A social post is a DISCOVERY SIGNAL, not proof of an active internship.
        If no official opening can be confirmed, mark as:
          SOCIAL LEAD - NOT VERIFIED
        """
        if is_indirect:
            return "indirect_signal"

        if signal_type == "unknown":
            return "social_lead_not_verified"

        # Primary hiring signals are still social leads until matched to an
        # official careers page or employer-owned application route.
        return "social_lead_not_verified"

    def get_by_company(self, company: str, limit: int = 50):
        """Retrieve signals by company."""
        return self.repo.get_by_company(self.session, company=company, limit=limit)
