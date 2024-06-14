from datetime import datetime
from typing import Any, Dict, List

import httpx

from humanitix.models import Event, Events
from humanitix.utils import get_kwargs_as_query_string
from config import get_config

config = get_config()


class HumanitixClient:
    """
    This class is responsible for making requests to the Humanitix API
    https://api.humanitix.com/v1/documentation/static/index.html
    """

    base_path: str = f"{config.HUMANITIX_API}/v1"

    def __init__(self) -> None:
        pass

    async def make_api_call(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        """
        Makes a call to the Humanitix API, adding in the necessary headers and API keys
        """

        headers = {
            "x-api-key": config.HUMANITIX_API_TOKEN,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if "headers" in kwargs:
            headers.update(kwargs["headers"])
            del kwargs["headers"]

        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method, url=f"{self.base_path}/{path}", headers=headers, **kwargs
            )
            response.raise_for_status()
            return response.json()

    async def get_events(
        self,
        page: int = 1,
        page_size: int = 100,
        since: datetime | None = None,
        inFutureOnly: bool = True,
    ):
        """
        Gets the events from the Humanitix API
        """

        url_options = get_kwargs_as_query_string(
            page=page, pageSize=page_size, inFutureOnly=inFutureOnly, since=since
        )

        return await self.make_api_call("GET", f"events?{url_options}")

    async def get_event(self, event_id: str, overrideLocation: str | None = None):
        """
        Gets the event from the Humanitix API
        """

        url_options = ""
        if overrideLocation is not None:
            url_options = f"?overrideLocation={overrideLocation}"

        return await self.make_api_call("GET", f"events/{event_id}{url_options}")

    async def get_event_orders(
        self,
        event_id: str,
        event_date_id: str | None = None,
        page: int = 1,
        page_size: int = 100,
        since: datetime | None = None,
    ):
        """
        Gets the event orders from the Humanitix API
        """

        url_options = get_kwargs_as_query_string(
            page=page, pageSize=page_size, since=since, eventDateId=event_date_id
        )

        return await self.make_api_call(
            "GET", f"events/{event_id}/orders?{url_options}"
        )

    async def get_event_order(self, event_id: str, order_id: str):
        """
        Gets the event order from the Humanitix API
        """

        return await self.make_api_call("GET", f"events/{event_id}/orders/{order_id}")

    async def get_event_tickets(
        self,
        event_id: str,
        event_date_id: str | None = None,
        page: int = 1,
        page_size: int = 100,
        status: str = "complete",
        since: datetime | None = None,
    ):
        """
        Gets the event tickets from the Humanitix API
        """

        url_options = get_kwargs_as_query_string(
            page=page,
            pageSize=page_size,
            status=status,
            since=since,
            eventDateId=event_date_id,
        )

        return await self.make_api_call(
            "GET", f"events/{event_id}/tickets?{url_options}"
        )

    async def get_event_ticket(self, event_id: str, ticket_id: str):
        """
        Gets the event ticket from the Humanitix API
        """

        return await self.make_api_call("GET", f"events/{event_id}/tickets/{ticket_id}")

    async def filter_events_by_name(
        self, event_name_fragment: str | None
    ) -> List[Event] | None:
        """
        Filters events by the supplied name fragment
        """

        events = Events.model_validate(await self.get_events())
        if event_name_fragment is None:
            return events.events

        filtered_events = []
        for event in events.events:
            if event_name_fragment in event.name or event_name_fragment in event.slug:
                filtered_events.append(event)

        return filtered_events if filtered_events else None
