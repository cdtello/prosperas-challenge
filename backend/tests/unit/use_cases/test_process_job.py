from unittest.mock import AsyncMock, patch

import pytest

from app.domain.entities.job import Job
from app.domain.value_objects.job_status import JobStatus
from app.use_cases.process_job import ProcessJobUseCase, generate_report


@pytest.fixture
def job_repo():
    repo = AsyncMock()
    job = Job(user_id="u1", report_type="sales_summary", date_range="2024-01", format="json")
    job.status = JobStatus.PROCESSING
    repo.update_status.return_value = job
    return repo


@pytest.fixture
def storage():
    s = AsyncMock()
    s.upload_report.return_value = "https://s3.example.com/reports/job-1.json"
    return s


@pytest.fixture
def queue():
    return AsyncMock()


@pytest.mark.asyncio
async def test_process_job_happy_path(job_repo, storage, queue):
    with patch("app.use_cases.process_job.asyncio.sleep"):
        await ProcessJobUseCase(job_repo, storage, queue).execute("job-1", "receipt-handle")

    job_repo.update_status.assert_any_call("job-1", JobStatus.PROCESSING)
    storage.upload_report.assert_called_once()
    job_repo.update_status.assert_any_call("job-1", JobStatus.COMPLETED, storage.upload_report.return_value)
    queue.delete.assert_called_once_with("receipt-handle")


@pytest.mark.asyncio
async def test_process_job_not_found_deletes_message(job_repo, storage, queue):
    job_repo.update_status.return_value = None

    await ProcessJobUseCase(job_repo, storage, queue).execute("missing", "receipt-handle")

    queue.delete.assert_called_once_with("receipt-handle")
    storage.upload_report.assert_not_called()


@pytest.mark.asyncio
async def test_process_job_marks_failed_on_error(job_repo, storage, queue):
    storage.upload_report.side_effect = Exception("S3 error")

    with patch("app.use_cases.process_job.asyncio.sleep"):
        with pytest.raises(Exception, match="S3 error"):
            await ProcessJobUseCase(job_repo, storage, queue).execute("job-1", "receipt-handle")

    job_repo.update_status.assert_any_call("job-1", JobStatus.FAILED)
    queue.delete.assert_not_called()


# ── generate_report: deterministic data quality tests ────────────────────────

def test_generate_report_sales_summary_structure():
    report = generate_report("job-abc", "sales_summary", "2024-01")
    assert report["job_id"] == "job-abc"
    assert "summary" in report
    assert report["summary"]["total_revenue_usd"] > 0
    assert len(report["top_products"]) == 4
    assert len(report["revenue_by_day"]) == 30


def test_generate_report_is_deterministic():
    r1 = generate_report("job-1", "sales_summary", "2024-01")
    r2 = generate_report("job-2", "sales_summary", "2024-01")
    assert r1["summary"]["total_revenue_usd"] == r2["summary"]["total_revenue_usd"]


def test_generate_report_differs_by_date_range():
    r1 = generate_report("job-1", "sales_summary", "2024-01")
    r2 = generate_report("job-1", "sales_summary", "2024-02")
    assert r1["summary"]["total_revenue_usd"] != r2["summary"]["total_revenue_usd"]


def test_generate_report_revenue_by_country():
    report = generate_report("job-x", "revenue_by_country", "2024-Q1")
    assert report["summary"]["active_countries"] == 9
    shares = [c["share_pct"] for c in report["by_country"]]
    assert abs(sum(shares) - 100.0) < 1.0


def test_generate_report_conversion_funnel_monotonic():
    report = generate_report("job-x", "conversion_funnel", "2024-01")
    steps = report["funnel_steps"]
    for i in range(1, len(steps)):
        assert steps[i]["users"] <= steps[i - 1]["users"]


def test_generate_report_user_activity():
    report = generate_report("job-x", "user_activity", "2024-01")
    s = report["summary"]
    assert s["daily_active_users"] <= s["monthly_active_users"]
    assert 0 < s["dau_mau_ratio"] < 1


def test_generate_report_product_performance():
    report = generate_report("job-x", "product_performance", "2024-01")
    assert report["summary"]["total_arr_usd"] == round(report["summary"]["total_mrr_usd"] * 12, 2)


def test_generate_report_unknown_type_falls_back_to_sales():
    report = generate_report("job-x", "unknown_type", "2024-01")
    assert "summary" in report
    assert "total_revenue_usd" in report["summary"]
