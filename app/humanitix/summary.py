from datetime import datetime, timezone
from typing import Any, Dict, List

from config import get_config
from dpn_pyutils.common import get_logger
from humanitix.client import HumanitixClient
from humanitix.models import DateRange, Event, Tickets

log = get_logger(__name__)

config = get_config()


def get_next_event_date(event: Event) -> DateRange | None:
    now = datetime.now(timezone.utc)
    upcoming = [
        d for d in event.dates
        if not d.disabled and not d.deleted and d.endDate > now
    ]
    return min(upcoming, key=lambda d: d.startDate) if upcoming else None


async def create_summary_from_event_data(events: List[Event]):
    """
    Generates a summary data structure from the event data
    """

    summary_data = []
    for e in events:
        client = HumanitixClient()

        next_date = get_next_event_date(e)
        if next_date is None:
            log.warning("No upcoming date found for event %s (%s), skipping", e.name, e.id)
            continue

        tickets = Tickets.model_validate(
            await client.get_event_tickets(e.id, event_date_id=next_date.id)
        ).tickets

        event_name = str(e.name).strip()
        if config.RENDER_TIX_REPLACE_WORD_FROM_NAME:
            event_name = event_name.replace(
                config.RENDER_TIX_REPLACE_WORD_FROM_NAME, ""
            ).strip()

        summary_event: Dict[str, Any] = {
            "id": e.id,
            "name": event_name,
            "slug": e.slug,
            "orders": len(tickets),
            "public": e.public,
            "published": e.published,
        }

        e.sparesNeeded = 0
        e.contributions = sum(t.price for t in tickets)

        if e.slug.startswith("dadlan-remote"):
            summary_event["isRemote"] = True
        else:
            remote_question_id = [
                q.id
                for q in e.additionalQuestions
                if config.LOANER_LAPTOP_QUESTION in q.question.lower()
            ].pop()

            for t in tickets:
                for d in t.additionalFields:
                    if d.questionId == remote_question_id:
                        if d.value is not None and d.value.lower() == "yes":
                            e.sparesNeeded += 1

        summary_event["contributions"] = e.contributions
        summary_event["spares_needed"] = e.sparesNeeded

        summary_data.append(summary_event)

    # Sorting first by name for entries with orders equal to zero
    summary_data.sort(key=lambda x: (x["orders"] == 0, x["name"] if x["orders"] == 0 else ''), reverse=False)

    # Sorting again by orders in reverse order, keeping the alphabetical order for entries with zero orders intact
    summary_data.sort(key=lambda x: x["orders"], reverse=True)

    return {
        "events": summary_data,
        "total_orders": sum(event["orders"] for event in summary_data),
        "total_spares_needed": sum(event["spares_needed"] for event in summary_data),
    }
