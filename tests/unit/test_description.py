"""Unit tests for description enrichment validation logic."""

import pytest
import re


class TestLanguageDetection:
    """Test the language detection logic from ValidatedEnricher."""

    def _detect_language(self, text):
        """Mirror the fixed ValidatedEnricher._detect_language: count occurrences."""
        dutch_words = ['een', 'van', 'het', 'de', 'en', 'is', 'voor', 'met', 'aan', 'bij']
        words = text.lower().split()
        dutch_count = sum(1 for word in words if word in dutch_words)
        if dutch_count > 15:
            return 'dutch'
        elif dutch_count > 5:
            return 'mixed'
        return 'english'

    def test_english_text(self):
        text = "We are looking for a Python developer with Django experience to join our team."
        assert self._detect_language(text) == 'english'

    def test_dutch_text(self):
        # With occurrence counting, a Dutch text with repeated stop words is detected
        text = ("Wij zijn op zoek naar een developer voor het team. "
                "De kandidaat is verantwoordelijk voor de ontwikkeling van het platform. "
                "Een sterke achtergrond in Python is een vereiste voor de functie. "
                "Het is van belang dat de kandidaat aan de eisen voldoet.")
        assert self._detect_language(text) == 'dutch'

    def test_mixed_text(self):
        text = "We zoeken een developer voor het team. Must have experience with Python en Java voor de backend."
        assert self._detect_language(text) == 'mixed'


class TestExperienceExtraction:
    """Test experience years extraction regex."""

    def _extract_years(self, text):
        patterns = [
            r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
            r'minimaal\s+(\d+)\s+jaar',
            r'at\s+least\s+(\d+)\s+years?',
        ]
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return int(match.group(1))
        return None

    def test_standard_format(self):
        assert self._extract_years("3+ years of experience") == 3

    def test_dutch_format(self):
        assert self._extract_years("minimaal 5 jaar ervaring") == 5

    def test_at_least_format(self):
        assert self._extract_years("at least 2 years") == 2

    def test_no_experience(self):
        assert self._extract_years("Junior position, no experience needed") is None


class TestQualityScore:
    """Test description quality scoring logic."""

    def _quality_score(self, text):
        score = 0
        if len(text) > 2000: score += 30
        elif len(text) > 1000: score += 20
        elif len(text) > 500: score += 10
        sections = ['requirements', 'responsibilities', 'qualifications', 'about']
        for section in sections:
            if section in text.lower():
                score += 10
        if text.count('\n') > 5: score += 10
        if text.count('-') > 5: score += 10
        return min(score, 100)

    def test_short_text_low_score(self):
        assert self._quality_score("Short description") < 20

    def test_long_structured_text_high_score(self):
        text = "About us\n" + "Requirements:\n" + "- Python\n" * 10 + \
               "Responsibilities:\n" + "- Build stuff\n" * 10 + \
               "Qualifications:\n" + "- BSc required\n" * 10
        text = text * 5  # Make it long enough
        score = self._quality_score(text)
        assert score >= 60
