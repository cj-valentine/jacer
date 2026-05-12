"""Direct tests for the materialisation service.

The router tests exercise this through HTTP; these tests exercise edge cases
of the fortnight parity logic without going through the API layer.
"""

from datetime import UTC, datetime

from jacer.models import Template, TemplateItem
from jacer.repositories.memory import InMemoryRepository
from jacer.services.materialise import materialise_day, materialise_horizon


def _now() -> datetime:
    return datetime.now(UTC)


def _setup_fortnightly(week_a_start: str = "2026-05-11"):
    """Build a fortnightly template with a Week-A and a Week-B item, both Monday."""
    repo = InMemoryRepository()
    template = Template(
        id="tp1",
        name="Fortnightly",
        cadence="fortnightly",
        week_a_start_date=week_a_start,
        is_locked=True,
        created_at=_now(),
        updated_at=_now(),
    )
    repo.save_template(template)
    repo.save_template_item(
        TemplateItem(
            id="a1",
            template_id="tp1",
            day_of_week=0,
            week_slot="A",
            title="Week A standup",
        )
    )
    repo.save_template_item(
        TemplateItem(
            id="b1",
            template_id="tp1",
            day_of_week=0,
            week_slot="B",
            title="Week B standup",
        )
    )
    return repo


def test_fortnightly_week_a_fires_on_reference_week():
    repo = _setup_fortnightly("2026-05-11")
    created = materialise_day(repo, "2026-05-11")
    assert len(created) == 1
    assert created[0].title == "Week A standup"


def test_fortnightly_week_b_fires_on_second_week():
    repo = _setup_fortnightly("2026-05-11")
    created = materialise_day(repo, "2026-05-18")
    assert len(created) == 1
    assert created[0].title == "Week B standup"


def test_fortnightly_week_a_fires_again_on_third_week():
    repo = _setup_fortnightly("2026-05-11")
    created = materialise_day(repo, "2026-05-25")
    assert len(created) == 1
    assert created[0].title == "Week A standup"


def test_fortnightly_item_without_week_slot_fires_every_week():
    repo = _setup_fortnightly("2026-05-11")
    # Add an "every week" item to the same fortnightly template
    repo.save_template_item(
        TemplateItem(
            id="both",
            template_id="tp1",
            day_of_week=0,
            week_slot=None,
            title="Both weeks standup",
        )
    )
    week_a = materialise_day(repo, "2026-05-11")
    repo._materialised.clear()
    week_b = materialise_day(repo, "2026-05-18")
    assert any(t.title == "Both weeks standup" for t in week_a)
    assert any(t.title == "Both weeks standup" for t in week_b)


def test_fortnightly_before_reference_date_does_not_fire():
    repo = _setup_fortnightly("2026-05-11")
    created = materialise_day(repo, "2026-05-04")  # before reference
    assert created == []


def test_materialise_horizon_creates_across_days():
    repo = InMemoryRepository()
    template = Template(
        id="tp1",
        name="Daily standup",
        cadence="weekly",
        is_locked=True,
        created_at=_now(),
        updated_at=_now(),
    )
    repo.save_template(template)
    # An item for every weekday Mon-Fri
    for dow in range(5):
        repo.save_template_item(
            TemplateItem(
                id=f"i{dow}",
                template_id="tp1",
                day_of_week=dow,
                title=f"Day {dow}",
            )
        )

    # 14 days from a Monday = 2 full weeks = 10 weekday items
    created = materialise_horizon(repo, "2026-05-11", days=14)
    assert len(created) == 10


def test_status_inferred_from_default_time():
    repo = InMemoryRepository()
    template = Template(
        id="tp1",
        name="W",
        is_locked=True,
        created_at=_now(),
        updated_at=_now(),
    )
    repo.save_template(template)
    repo.save_template_item(
        TemplateItem(
            id="i1",
            template_id="tp1",
            day_of_week=0,
            title="With time",
            default_time="09:00",
        )
    )
    repo.save_template_item(
        TemplateItem(
            id="i2",
            template_id="tp1",
            day_of_week=0,
            title="Without time",
        )
    )

    created = materialise_day(repo, "2026-05-11")
    by_title = {t.title: t for t in created}
    assert by_title["With time"].status == "scheduled"
    assert by_title["Without time"].status == "today"
