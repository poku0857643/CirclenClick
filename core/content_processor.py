"""Content preprocessing and text extraction."""

import re
from typing import Dict, List, Optional
from dataclasses import dataclass

from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ProcessedContent:
    """Processed content with metadata."""

    text: str
    cleaned_text: str
    sentences: List[str]
    claims: List[str]
    metadata: Dict[str, any]

    @property
    def has_claims(self) -> bool:
        """Check if content has extractable claims."""
        return len(self.claims) > 0


class ContentProcessor:
    """Processes and cleans text content for verification."""

    def __init__(self):
        """Initialize the content processor."""
        self.logger = logger

    def process(
        self,
        text: str,
        url: Optional[str] = None,
        platform: Optional[str] = None,
        author: Optional[str] = None
    ) -> ProcessedContent:
        """Process raw text content.

        Args:
            text: Raw text to process
            url: Optional source URL
            platform: Optional platform name (facebook, twitter, threads)
            author: Optional author/username

        Returns:
            ProcessedContent instance with cleaned text and metadata
        """
        self.logger.info(f"Processing content from {platform or 'unknown platform'}")

        # Clean the text
        cleaned_text = self._clean_text(text)

        # Split into sentences
        sentences = self._split_sentences(cleaned_text)

        # Extract potential claims (basic implementation)
        claims = self._extract_claims(sentences)

        # Build metadata
        metadata = {
            "url": url,
            "platform": platform,
            "author": author,
            "original_length": len(text),
            "cleaned_length": len(cleaned_text),
            "sentence_count": len(sentences),
            "claim_count": len(claims)
        }

        return ProcessedContent(
            text=text,
            cleaned_text=cleaned_text,
            sentences=sentences,
            claims=claims,
            metadata=metadata
        )

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text.

        Args:
            text: Raw text

        Returns:
            Cleaned text
        """
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)

        # Remove URLs
        text = re.sub(r'http[s]?://\S+', '', text)

        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s.,!?;:\'\"-]', '', text)

        # Trim
        text = text.strip()

        return text

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences.

        Args:
            text: Cleaned text

        Returns:
            List of sentences
        """
        # Simple sentence splitting (can be improved with spaCy or NLTK)
        sentences = re.split(r'(?<=[.!?])\s+', text)

        # Filter out very short sentences
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

        return sentences

    def _extract_claims(self, sentences: List[str]) -> List[str]:
        """Extract potential factual claims from sentences.

        This is a basic implementation. A more sophisticated version would use
        a trained model to identify check-worthy claims.

        Args:
            sentences: List of sentences

        Returns:
            List of potential claims
        """
        claims = []

        # Keywords that often indicate factual claims
        claim_indicators = [
            r'\d+%',  # Percentages
            r'\d+\s+(billion|million|thousand)',  # Large numbers
            r'(according to|study shows|research found|report states)',
            r'(is|are|was|were)\s+(the|a)\s+',  # Definitive statements
            r'(first|largest|biggest|most|least)',  # Superlatives
            r'(every|all|no|none)',  # Absolutes
        ]

        for sentence in sentences:
            # Check if sentence contains claim indicators
            for indicator in claim_indicators:
                if re.search(indicator, sentence, re.IGNORECASE):
                    claims.append(sentence)
                    break

            # Also include sentences with certain patterns
            if self._is_likely_claim(sentence):
                if sentence not in claims:
                    claims.append(sentence)

        self.logger.debug(f"Extracted {len(claims)} potential claims from {len(sentences)} sentences")

        return claims

    def _is_likely_claim(self, sentence: str) -> bool:
        """Check if a sentence is likely a factual claim.

        Args:
            sentence: Sentence to check

        Returns:
            True if likely a claim
        """
        # Filter out questions
        if sentence.strip().endswith('?'):
            return False

        # Filter out very short sentences
        if len(sentence.split()) < 3:
            return False

        # Filter out personal opinions
        opinion_markers = ['i think', 'i believe', 'in my opinion', 'i feel', 'seems like']
        if any(marker in sentence.lower() for marker in opinion_markers):
            return False

        # Check for factual indicators
        factual_verbs = ['is', 'are', 'was', 'were', 'has', 'have', 'will', 'shows', 'proves']
        if any(f' {verb} ' in sentence.lower() for verb in factual_verbs):
            return True

        return False
