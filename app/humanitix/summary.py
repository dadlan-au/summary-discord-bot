from typing import Any, Dict, List

from config import get_config
from humanitix.client import HumanitixClient
from humanitix.models import Event, Tickets

config = get_config()


async def create_summary_from_event_data(events: List[Event]):
    """
    Generates a summary data structure from the event data
    """

    summary_data = []
    for e in events:

        client = HumanitixClient()
        tickets = Tickets.model_validate(await client.get_event_tickets(e.id)).tickets

        summary_event: Dict[str, Any] = {
            "id": e.id,
            "name": e.name,
            "slug": e.slug,
            "orders": len(tickets),
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

    summary_data.sort(key=lambda x: x["name"], reverse=False)

    return {
        "events": summary_data,
        "total_orders": sum(event["orders"] for event in summary_data),
        "total_spares_needed": sum(event["spares_needed"] for event in summary_data),
    }
