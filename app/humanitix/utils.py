from urllib.parse import urlencode


def get_kwargs_as_query_string(**kwargs):
    """
    Converts supplied kwargs into a query string
    """

    # Manually checks for keys as the Humanitix API requires specific order & values
    params = {}

    if "page" in kwargs:
        params["page"] = kwargs["page"]

    if "page_size" in kwargs:
        params["page_size"] = kwargs["page_size"]

    if "inFutureOnly" in kwargs:
        params["inFutureOnly"] = str(kwargs["inFutureOnly"]).lower()

    if "since" in kwargs and kwargs["since"] is not None:
        params["since"] = kwargs["since"]

    if "overrideLocation" in kwargs:
        params["overrideLocation"] = kwargs["overrideLocation"]

    if "eventDateId" in kwargs and kwargs["eventDateId"] is not None:
        params["eventDateId"] = kwargs["eventDateId"]

    if "status" in kwargs and kwargs["status"] is not None:

        valid_status = ["complete", "cancelled"]
        supplied_status = kwargs["status"].lower()

        if supplied_status not in valid_status:
            raise ValueError(
                f"Invalid status supplied to event ticket url query. Must be one of {valid_status}"
            )

        params["status"] = supplied_status

    return urlencode(params)
