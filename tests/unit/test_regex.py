"""Unit tests for AI analyzer response parsing."""

import pytest
from analyzers.analyzer_ai import AIJobAnalyzer


class TestResponseParsing:
    """Test the regex-based response parsing without needing an API key."""

    @pytest.fixture
    def parser(self):
        """Create a parser method reference (doesn't need API key)."""
        # We can't instantiate AIJobAnalyzer without API key,
        # so we call the static-compatible method directly
        class MockAnalyzer:
            pass
        analyzer = MockAnalyzer()
        analyzer._parse_analysis_response = AIJobAnalyzer._parse_analysis_response.__get__(analyzer)
        return analyzer

    def test_parse_standard_response(self, parser):
        response = """SCORE: 85
STRENGTHS:
- Strong Python skills from thesis project
- Relevant ML experience at PSA International
- Located in Netherlands with valid visa
CONCERNS:
- Limited professional experience
- No Django knowledge mentioned
FIT: This is a great match for a junior developer transitioning into industry.
RECOMMENDATION: Apply immediately and emphasize thesis project."""

        result = parser._parse_analysis_response(response)
        assert result['score'] == 85
        assert len(result['strengths']) == 3
        assert len(result['concerns']) == 2
        assert 'great match' in result['fit_assessment']
        assert 'Apply' in result['recommendation']

    def test_parse_low_score(self, parser):
        response = """SCORE: 30
STRENGTHS:
- Some transferable skills
CONCERNS:
- Missing 5 years of experience
- Wrong specialization
FIT: Not a good fit due to experience gap.
RECOMMENDATION: Skip this role."""

        result = parser._parse_analysis_response(response)
        assert result['score'] == 30
        assert len(result['concerns']) == 2

    def test_parse_missing_sections(self, parser):
        response = "SCORE: 60"
        result = parser._parse_analysis_response(response)
        assert result['score'] == 60
        assert result['strengths'] == []
        assert result['concerns'] == []

    def test_parse_no_score(self, parser):
        response = "This job looks interesting."
        result = parser._parse_analysis_response(response)
        assert result['score'] == 0
