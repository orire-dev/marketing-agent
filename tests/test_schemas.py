"""
Unit tests for schemas
"""

import pytest
from app.schemas import (
    GenerateRequest, GenerateResponse, CreativeOption,
    CopyVariants, DesignSpec, ComplianceResult, OptionScores,
    Channel, AssetFormat, Language
)


def test_generate_request():
    """Test GenerateRequest schema"""
    request = GenerateRequest(
        product_scope="crypto",
        channel=Channel.SOCIAL,
        asset=AssetFormat.SOCIAL_1X1,
        languages=[Language.EN, Language.DE],
        style_guidance="clean, premium"
    )
    
    assert request.product_scope == "crypto"
    assert request.channel == Channel.SOCIAL
    assert len(request.languages) == 2


def test_copy_variants():
    """Test CopyVariants schema"""
    copy = CopyVariants(
        headline_variants=["Headline 1", "Headline 2"],
        cta_variants=["Start Trading"]
    )
    
    assert len(copy.headline_variants) == 2
    assert len(copy.cta_variants) == 1


def test_compliance_result():
    """Test ComplianceResult schema"""
    compliance = ComplianceResult(
        status="pass",
        flags=[],
        required_disclaimers=["Capital at risk"],
        suggested_safe_edits=[]
    )
    
    assert compliance.status == "pass"
    assert len(compliance.required_disclaimers) == 1
