# (C) Copyright IBM Corp. 2024.
# Licensed under the Apache License, Version 2.0 (the “License”);
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#  http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an “AS IS” BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
################################################################################

import pytest
from dpk_connector.core.middlewares import DelayingProtegoRobotParser
from pytest_mock import MockerFixture


@pytest.mark.parametrize(
    "ua,expected",
    [
        ("Mozilla", 7.7),
        ("MSIE", 10),
        ("Macintosh", 60),
        ("ua1", None),
        ("ua2", None),
    ],
)
def test_robots_crawl_delay(mocker: MockerFixture, ua: str, expected: float):
    robots_txt = """
User-agent: *
Crawl-delay: 7.7
User-agent: MSIE
Crawl-delay: 10
User-agent: Macintosh
Crawl-delay: 10000
User-agent: ua1
Crawl-delay: not numeric value
User-agent: ua2
"""
    crawler = mocker.patch("dpk_connector.core.middlewares.Crawler")
    parser = DelayingProtegoRobotParser(robots_txt.encode("utf-8"), crawler.spider)
    parser.max_delay = 60
    assert parser.delay(ua) == expected


@pytest.mark.parametrize(
    "ua,expected",
    [
        ("Mozilla", 10),
        ("MSIE", 60),
        ("Macintosh", 60),
        ("ua1", None),
        ("ua2", None),
    ],
)
def test_robots_request_rate(mocker: MockerFixture, ua: str, expected: float):
    robots_txt = """
User-agent: *
Request-rate: 1/10s
User-agent: MSIE
Request-rate: 1/1m 0900-1730
User-agent: Macintosh
Request-rate: 2/1h 0000-1736
User-agent: ua1
Request-rate: invalid value
User-agent: ua2
"""
    crawler = mocker.patch("dpk_connector.core.middlewares.Crawler")
    parser = DelayingProtegoRobotParser(robots_txt.encode("utf-8"), crawler.spider)
    parser.max_delay = 60
    assert parser.delay(ua) == expected
