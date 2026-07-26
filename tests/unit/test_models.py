"""Unit tests for domain models."""

from datetime import datetime

from docforge.core.document import (
    ALLOWED_LICENCES,
    ImageCandidate,
    LicenceType,
    SemanticModel,
)
from docforge.core.project import Project, UserAccount
from docforge.core.rendering import (
    JobStatus,
    RenderEstimate,
    RenderingDecision,
    RenderingJob,
)


def test_allowed_licences_contains_expected():
    assert LicenceType.PUBLIC_DOMAIN in ALLOWED_LICENCES
    assert LicenceType.CC0 in ALLOWED_LICENCES
    assert LicenceType.CC_BY in ALLOWED_LICENCES
    assert LicenceType.CC_BY_SA in ALLOWED_LICENCES
    assert LicenceType.UNSUPPORTED not in ALLOWED_LICENCES
    assert LicenceType.UNKNOWN not in ALLOWED_LICENCES


def test_rendering_decision_defaults():
    d = RenderingDecision(chapter_id="ch1")
    assert d.chapter_id == "ch1"
    assert d.pull_quote is False
    assert d.callout is False


def test_rendering_job_defaults():
    job = RenderingJob(id="job-1")
    assert job.status == JobStatus.QUEUED
    assert job.progress == 0
    assert job.error is None


def test_render_estimate_defaults():
    est = RenderEstimate()
    assert est.estimated_rendering_seconds == 0
    assert est.image_placeholder_count == 0


def test_semantic_model_empty():
    m = SemanticModel(document_id="doc-1")
    assert m.chapters == []
    assert m.statistics.chapter_count == 0


def test_image_candidate_licence():
    c = ImageCandidate(provider="wikimedia", url="http://x.com/img.jpg", title="Test")
    assert c.licence == LicenceType.UNKNOWN

    c2 = ImageCandidate(
        provider="wikimedia", url="http://x.com/img.jpg", title="Test", licence=LicenceType.CC_BY
    )
    assert c2.licence == LicenceType.CC_BY


def test_user_account_model():
    ua = UserAccount(
        id=1, username="admin", password_hash="$2b$12$abc", created_at=datetime.utcnow()
    )
    assert ua.username == "admin"


def test_project_model():
    p = Project(
        id="proj-1",
        name="Test",
        job_id="job-1",
        input_filename="test.docx",
        config_snapshot={},
        output_paths=[],
        template="minimal",
        language="en",
        ai_model="gpt-4o",
        status=JobStatus.COMPLETED,
        created_at=datetime.utcnow(),
    )
    assert p.template == "minimal"
