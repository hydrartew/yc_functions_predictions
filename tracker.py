import logging

from yandex_tracker_client import TrackerClient
from yandex_tracker_client.objects import Resource

from config_data import settings

logger = logging.getLogger('tracker')


class YNYBTracker:
    def __init__(self):
        self.queue = 'YNYB'
        self.key_tag = 'ready_to_add_to_db'
        self.key_tag_after_issue_processing = 'added_to_db'

        self.tracker_url = 'https://st.yandex-team.ru/'

        self.token = settings.TRACKER_INTERNAL_TOKEN
        self.api_url = 'https://st-api.yandex-team.ru/'

        self.tracker_client = TrackerClient(token=self.token, base_url=self.api_url)

    @property
    def filter_target_issues(self) -> str:
        return 'Queue: {} tags: {} Status: closed "Sort by": Created ASC'.format(self.queue, self.key_tag)

    def get_issues(self) -> list[Resource]:
        logger.info('Start of the tracker issues search by filter')
        issues = self.tracker_client.issues.find(self.filter_target_issues)
        logger.info(f'{len(issues)} tracker issues found')

        return issues


ynyb_tracker = YNYBTracker()
