import asyncio
import hashlib
import logging
import random
from datetime import datetime, timedelta, timezone

from app.domain.ports.file_storage import IFileStorage
from app.domain.ports.job_repository import IJobRepository
from app.domain.ports.message_queue import IMessageQueue
from app.domain.value_objects.job_status import JobStatus

logger = logging.getLogger(__name__)


def _seeded_rng(report_type: str, date_range: str) -> random.Random:
    """Deterministic RNG — same report_type + date_range always produces same report."""
    seed = int(hashlib.md5(f"{report_type}:{date_range}".encode()).hexdigest(), 16)
    return random.Random(seed)


def _sales_summary(rng: random.Random, date_range: str) -> dict:
    products = [
        "Pro Analytics Plan", "Starter Plan", "Enterprise Suite",
        "Data Insights Add-on", "API Access Pack", "Custom Dashboard",
    ]
    orders = rng.randint(800, 3500)
    avg_order = round(rng.uniform(80, 450), 2)
    total_revenue = round(orders * avg_order, 2)

    top_products = []
    for name in rng.sample(products, 4):
        pct = rng.uniform(0.08, 0.30)
        top_products.append({
            "product": name,
            "units_sold": rng.randint(50, 600),
            "revenue_usd": round(total_revenue * pct, 2),
        })
    top_products.sort(key=lambda x: x["revenue_usd"], reverse=True)

    revenue_by_day = []
    for i in range(30):
        day = (datetime.now(timezone.utc) - timedelta(days=29 - i)).strftime("%Y-%m-%d")
        revenue_by_day.append({
            "date": day,
            "revenue_usd": round(max(0, rng.gauss(total_revenue / 30, total_revenue / 80)), 2),
            "orders": rng.randint(max(1, orders // 45), max(2, orders // 18)),
        })

    return {
        "report_type": "Sales Summary",
        "period": date_range,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_revenue_usd": total_revenue,
            "total_orders": orders,
            "avg_order_value_usd": avg_order,
            "revenue_growth_vs_prev_period_pct": round(rng.uniform(-5, 28), 1),
            "refund_rate_pct": round(rng.uniform(1.5, 4.5), 2),
        },
        "top_products": top_products,
        "revenue_by_day": revenue_by_day,
    }


def _revenue_by_country(rng: random.Random, date_range: str) -> dict:
    countries = [
        ("Colombia", "CO"), ("Mexico", "MX"), ("Argentina", "AR"),
        ("Chile", "CL"), ("Peru", "PE"), ("Brazil", "BR"),
        ("Ecuador", "EC"), ("Uruguay", "UY"), ("Panama", "PA"),
    ]
    total = round(rng.uniform(600_000, 4_500_000), 2)
    weights = sorted([rng.random() for _ in countries], reverse=True)
    w_sum = sum(weights)

    breakdown = []
    for (country, code), w in zip(countries, weights, strict=False):
        rev = round(total * w / w_sum, 2)
        breakdown.append({
            "country": country,
            "country_code": code,
            "revenue_usd": rev,
            "share_pct": round(rev / total * 100, 1),
            "orders": rng.randint(200, 8000),
            "avg_order_value_usd": round(rng.uniform(60, 380), 2),
            "growth_vs_prev_pct": round(rng.uniform(-8, 35), 1),
        })

    return {
        "report_type": "Revenue by Country",
        "period": date_range,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_revenue_usd": total,
            "active_countries": len(countries),
            "top_market": breakdown[0]["country"],
            "top_market_share_pct": breakdown[0]["share_pct"],
        },
        "by_country": breakdown,
    }


def _user_activity(rng: random.Random, date_range: str) -> dict:
    mau = rng.randint(8_000, 45_000)
    dau = round(mau * rng.uniform(0.08, 0.22))
    new_users = rng.randint(500, 3_000)

    features = [
        "Dashboard", "Report Builder", "Analytics Explorer",
        "API Console", "Data Exports", "Team Settings",
    ]
    feature_usage = sorted([
        {
            "feature": f,
            "sessions": rng.randint(200, 5000),
            "avg_session_min": round(rng.uniform(2, 25), 1),
            "satisfaction_score": round(rng.uniform(3.5, 5.0), 1),
        }
        for f in features
    ], key=lambda x: x["sessions"], reverse=True)

    return {
        "report_type": "User Activity",
        "period": date_range,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "monthly_active_users": mau,
            "daily_active_users": dau,
            "dau_mau_ratio": round(dau / mau, 3),
            "new_users": new_users,
            "returning_users": mau - new_users,
            "retention_rate_pct": round(rng.uniform(55, 82), 1),
            "avg_session_duration_min": round(rng.uniform(8, 28), 1),
            "sessions_per_user_per_month": round(rng.uniform(3, 12), 1),
        },
        "peak_activity_hours_utc": sorted(rng.sample(range(8, 20), 4)),
        "feature_usage": feature_usage,
    }


def _conversion_funnel(rng: random.Random, date_range: str) -> dict:
    visitors = rng.randint(50_000, 300_000)
    step_names = [
        "Landing Page Visit", "Sign Up Started", "Email Verified",
        "Profile Completed", "First Report Created", "Paid Subscription",
    ]
    counts = [visitors]
    for _ in step_names[1:]:
        counts.append(round(counts[-1] * rng.uniform(0.38, 0.78)))

    funnel = []
    for i, (name, count) in enumerate(zip(step_names, counts, strict=False)):
        prev = counts[i - 1] if i > 0 else count
        funnel.append({
            "step": i + 1,
            "name": name,
            "users": count,
            "conversion_from_previous_pct": round(count / prev * 100, 1) if i > 0 else 100.0,
            "drop_off_pct": round((1 - count / prev) * 100, 1) if i > 0 else 0.0,
            "overall_pct": round(count / visitors * 100, 2),
        })

    biggest_drop = max(range(1, len(counts)), key=lambda i: counts[i - 1] - counts[i])

    return {
        "report_type": "Conversion Funnel",
        "period": date_range,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_visitors": visitors,
            "paying_customers": counts[-1],
            "overall_conversion_pct": round(counts[-1] / visitors * 100, 2),
            "biggest_dropoff_step": step_names[biggest_drop],
            "biggest_dropoff_pct": round(
                (counts[biggest_drop - 1] - counts[biggest_drop])
                / counts[biggest_drop - 1] * 100, 1
            ),
        },
        "funnel_steps": funnel,
    }


def _product_performance(rng: random.Random, date_range: str) -> dict:
    plans = [
        {"name": "Starter", "price_usd": 29},
        {"name": "Professional", "price_usd": 99},
        {"name": "Business", "price_usd": 249},
        {"name": "Enterprise", "price_usd": 799},
    ]
    products = []
    for plan in plans:
        subs = rng.randint(50, 2000)
        mrr = round(subs * plan["price_usd"] * rng.uniform(0.88, 1.0), 2)
        products.append({
            "plan": plan["name"],
            "price_usd_per_month": plan["price_usd"],
            "active_subscriptions": subs,
            "new_this_period": rng.randint(10, 200),
            "churned_this_period": rng.randint(5, 80),
            "mrr_usd": mrr,
            "churn_rate_pct": round(rng.uniform(1.5, 6.5), 2),
            "avg_lifetime_months": round(rng.uniform(8, 36), 1),
            "nps_score": rng.randint(32, 72),
        })

    total_mrr = sum(p["mrr_usd"] for p in products)
    total_subs = sum(p["active_subscriptions"] for p in products)

    return {
        "report_type": "Product Performance",
        "period": date_range,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_mrr_usd": round(total_mrr, 2),
            "total_arr_usd": round(total_mrr * 12, 2),
            "total_active_subscriptions": total_subs,
            "avg_revenue_per_user_usd": round(total_mrr / total_subs, 2),
            "expansion_mrr_pct": round(rng.uniform(5, 18), 1),
        },
        "by_plan": products,
    }


_GENERATORS = {
    "sales_summary": _sales_summary,
    "revenue_by_country": _revenue_by_country,
    "user_activity": _user_activity,
    "conversion_funnel": _conversion_funnel,
    "product_performance": _product_performance,
}


def generate_report(job_id: str, report_type: str, date_range: str) -> dict:
    rng = _seeded_rng(report_type, date_range)
    generator = _GENERATORS.get(report_type, _sales_summary)
    report = generator(rng, date_range)
    report["job_id"] = job_id
    return report


class ProcessJobUseCase:
    def __init__(
        self,
        job_repo: IJobRepository,
        storage: IFileStorage,
        queue: IMessageQueue,
    ) -> None:
        self._job_repo = job_repo
        self._storage = storage
        self._queue = queue

    async def execute(self, job_id: str, receipt_handle: str) -> None:
        logger.info("Processing job %s", job_id)

        job = await self._job_repo.update_status(job_id, JobStatus.PROCESSING)
        if job is None:
            logger.warning("Job %s not found — deleting orphan message", job_id)
            await self._queue.delete(receipt_handle)
            return

        try:
            processing_time = random.randint(5, 15)
            logger.info("Job %s (%s) processing for %ds", job_id, job.report_type, processing_time)
            await asyncio.sleep(processing_time)

            report = generate_report(job_id, job.report_type, job.date_range)
            result_url = await self._storage.upload_report(job_id, report)

            await self._job_repo.update_status(job_id, JobStatus.COMPLETED, result_url)
            await self._queue.delete(receipt_handle)
            logger.info("Job %s COMPLETED", job_id)

        except Exception:
            await self._job_repo.update_status(job_id, JobStatus.FAILED)
            logger.exception("Job %s FAILED — SQS retrying → DLQ after 3 attempts", job_id)
            raise
