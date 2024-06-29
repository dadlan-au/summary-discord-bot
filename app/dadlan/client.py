import httpx
from config import get_config
from dpn_pyutils.common import get_logger

log = get_logger(__name__)

config = get_config()


def get_variable(variable_name: str, default_value: str) -> str:
    """
    Gets a variable from the DadLAN WAN Portal
    """

    url = f"{config.DADLAN_WAN_API_URL}/api/v1/sys/variables/{variable_name}"
    headers = {"X-Authorization": config.DADLAN_WAN_API_KEY}

    response = httpx.get(url, headers=headers)

    if response.status_code != 200:
        log.error(
            "Failed to get variable '%s'. %s: %s",
            variable_name,
            response.status_code,
            response.text,
        )
        return default_value

    return response.json()["value"]


def set_variable(variable_name: str, value: str) -> None:
    """
    Sets the variable to a specific value
    """

    url = f"{config.DADLAN_WAN_API_URL}/api/v1/sys/variables/{variable_name}"
    headers = {"X-Authorization": config.DADLAN_WAN_API_KEY}

    response = httpx.put(url, headers=headers, json={"value": value})

    if response.status_code != 200:
        log.error(
            "Failed to set variable '%s'. %s: %s",
            variable_name,
            response.status_code,
            response.text,
        )
        response.raise_for_status()
