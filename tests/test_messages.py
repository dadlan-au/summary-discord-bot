import random
import unittest
from pathlib import Path

from app.config import get_config
from app.render import render_template, split_rendered_text_max_length

config = get_config()


class TestMessages(unittest.TestCase):
    """
    Tests some message uses cases
    """

    def generate_sample_threads(self, num_threads: int = 10):
        """
        Generates sample threads that have the right format but are totally made up
        """

        base_url = "https://discord.com/channels/"

        def generate_number(length):
            range_start = 10 ** (length - 1)
            range_end = (10**length) - 1
            # trunk-ignore(bandit/B311)
            return random.randint(range_start, range_end)

        threads = []
        for _ in range(num_threads):
            channel_id = generate_number(19)
            thread_id = generate_number(19)
            threads.append(
                {
                    "parent": {"name": "very-long-channel-name-here"},
                    "jump_url": f"{base_url}{channel_id}/{thread_id}",
                }
            )

        return threads

    def test_max_length(self):
        """
        Tests for a maximum length of a rendered message
        """

        channels = []

        threads = self.generate_sample_threads(40)

        rendered_template = render_template(
            Path("app/template.jinja2"), channels, threads
        )

        print(rendered_template)
        print(f"Length of template: {len(rendered_template)}")

        messages = split_rendered_text_max_length(
            rendered_template, config.DISCORD_MAX_MESSAGE_LENGTH
        )

        print(f"There are {len(messages)}:")
        for m in messages:
            print(f"\t Message length: {len(m)}")
            print(f"\t\t {m[0:30]} .. {m[-30:]}")





