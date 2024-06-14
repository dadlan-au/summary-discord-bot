import unittest
from pathlib import Path
from typing import Any, Dict

from dpn_pyutils.file import read_file_json, save_file_json

from app.config import get_config
from app.humanitix.client import HumanitixClient
from app.humanitix.models import Events, Tickets
from app.rendering.graphic import create_image_tix

config = get_config()


class TestHumanitix(unittest.IsolatedAsyncioTestCase):
    """
    Tests use cases for accessing Humanitix API
    """

    async def test_valid_connection(self):
        """
        Tests that the connection to Humanitix API is valid
        """

        from app.humanitix.client import HumanitixClient

        temp_file = Path("tests/data/events.json")

        if not temp_file.exists():
            client = HumanitixClient()
            response = await client.get_events()
            events = Events.model_validate(response)

            self.assertIsNotNone(events)

            save_file_json(temp_file, response)

    async def test_filter_events_by_name(self):
        """
        Tests that an event can be retrieved from the Humanitix API and filtered by name
        """

        from app.humanitix.client import HumanitixClient

        client = HumanitixClient()
        name = "mel"

        events = await client.filter_events_by_name(name)

        self.assertIsNotNone(events)

    async def test_render_output(self):
        """
        Tests rendering the output for the list of events
        """

        event_data = Events.model_validate(
            read_file_json(Path("tests/data/events.json"))
        )
        events = event_data.events

        summary_data = []
        for e in events:

            ticket_cache_path = Path(f"tests/data/tickets-{e.slug}.json")
            if not ticket_cache_path.exists():
                client = HumanitixClient()
                # ticket_data = Tickets.model_validate(await client.get_event_tickets(e.id))
                tickets_json = await client.get_event_tickets(e.id)
                save_file_json(
                    ticket_cache_path,
                    tickets_json,
                    overwrite=True,
                )
            else:
                tickets_json = read_file_json(ticket_cache_path)

            tickets = Tickets.model_validate(tickets_json).tickets
            summary_event: Dict[str, Any] = {
                "id": e.id,
                "name": e.name,
                "slug": e.slug,
            }

            if e.slug.startswith("dadlan-remote"):
                summary_event["isRemote"] = True
                summary_event["ordersCount"] = len(tickets)
            else:
                remote_question_id = [
                    q.id
                    for q in e.additionalQuestions
                    if config.LOANER_LAPTOP_QUESTION in q.question.lower()
                ].pop()

                e.ordersCount = len(tickets)
                e.contributions = sum(t.price for t in tickets)
                e.sparesNeeded = 0
                for t in tickets:
                    for d in t.additionalFields:
                        if d.questionId == remote_question_id:
                            if d.value is not None and d.value.lower() == "yes":
                                e.sparesNeeded += 1

            summary_event["orders"] = e.ordersCount
            summary_event["contributions"] = e.contributions
            summary_event["spares_needed"] = e.sparesNeeded

            summary_data.append(summary_event)

        summary_data.sort(key=lambda x: x["name"], reverse=False)

        render_data = {
            "events": summary_data,
            "total_orders": sum(event["orders"] for event in summary_data),
            "total_spares_needed": sum(
                event["spares_needed"] for event in summary_data
            ),
        }

        create_image_tix(render_data)

        save_file_json(Path("tests/data/summary.json"), render_data, overwrite=True)
