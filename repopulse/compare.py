"""Compare two HealthReport instances (branches, tags, paths, or repositories)."""

from __future__ import annotations

from repopulse.models import CheckDelta, CheckResult, ComparisonReport, HealthReport

_STATUS_RANK = {"fail": 0, "warn": 1, "pass": 2}


def _status_rank(status: str | None) -> int:
    if status is None:
        return -1
    return _STATUS_RANK.get(status, -1)


def _classify_change(
    baseline: CheckResult | None,
    target: CheckResult | None,
) -> tuple[str, int]:
    """Return (change_label, score_delta)."""
    if baseline is None and target is not None:
        return "added", target.score
    if baseline is not None and target is None:
        return "removed", -baseline.score

    assert baseline is not None and target is not None
    score_delta = target.score - baseline.score
    base_rank = _status_rank(baseline.status)
    target_rank = _status_rank(target.status)

    if score_delta > 0 or target_rank > base_rank:
        return "improved", score_delta
    if score_delta < 0 or target_rank < base_rank:
        return "regressed", score_delta
    return "unchanged", 0


def build_comparison(
    baseline: HealthReport,
    target: HealthReport,
    *,
    baseline_label: str | None = None,
    target_label: str | None = None,
) -> ComparisonReport:
    """Diff two health reports check-by-check."""
    base_label = baseline_label or baseline.repository.full_name
    tgt_label = target_label or target.repository.full_name

    base_by_key = {check.key: check for check in baseline.checks}
    target_by_key = {check.key: check for check in target.checks}
    keys = sorted(set(base_by_key) | set(target_by_key))

    deltas: list[CheckDelta] = []
    improved: list[str] = []
    regressed: list[str] = []
    unchanged: list[str] = []

    for key in keys:
        base_check = base_by_key.get(key)
        target_check = target_by_key.get(key)
        change, score_delta = _classify_change(base_check, target_check)
        title = (target_check or base_check).title  # type: ignore[union-attr]
        delta = CheckDelta(
            key=key,
            title=title,
            baseline_status=base_check.status if base_check else None,
            target_status=target_check.status if target_check else None,
            baseline_score=base_check.score if base_check else None,
            target_score=target_check.score if target_check else None,
            score_delta=score_delta,
            change=change,  # type: ignore[arg-type]
        )
        deltas.append(delta)
        if change == "improved":
            improved.append(key)
        elif change == "regressed":
            regressed.append(key)
        elif change == "unchanged":
            unchanged.append(key)
        elif change == "added":
            # Newly present check: treat as improvement if it is not a fail.
            if target_check and target_check.status != "fail":
                improved.append(key)
            elif target_check and target_check.status == "fail":
                regressed.append(key)
        elif change == "removed":
            regressed.append(key)

    return ComparisonReport(
        baseline_label=base_label,
        target_label=tgt_label,
        baseline_repository=baseline.repository.full_name,
        target_repository=target.repository.full_name,
        baseline_score=baseline.total_score,
        target_score=target.total_score,
        baseline_max_score=baseline.max_score,
        target_max_score=target.max_score,
        score_delta=target.total_score - baseline.total_score,
        baseline_grade=baseline.grade,
        target_grade=target.grade,
        checks=deltas,
        improved=improved,
        regressed=regressed,
        unchanged=unchanged,
        config={
            "baseline": baseline.config,
            "target": target.config,
        },
    )


def has_regression(comparison: ComparisonReport) -> bool:
    """True when overall score dropped or any check regressed/removed as fail."""
    if comparison.score_delta < 0:
        return True
    return bool(comparison.regressed)
