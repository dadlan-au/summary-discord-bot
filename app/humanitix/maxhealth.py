import json
from typing import Dict

from config import get_config
from dadlan.client import get_variable

config = get_config()


async def apply_maxhealth_info(summary_data: Dict) -> Dict:
    """
    Loads and applies the MaxHealth data to the summary data
    """

    max_health_data = json.loads(
        get_variable(config.RENDER_TIX_MAXHEALTH_VAR_NAME, "{}")
    )

    for event in summary_data["events"]:
        if event["name"] in max_health_data:
            event["maxhealth"] = max_health_data[event["name"]]
        else:
            event["maxhealth"] = 0

    summary_data["total_maxhealth"] = sum(
        event["maxhealth"] for event in summary_data["events"]
    )

    return summary_data
