import logging

from yandex_tracker_client import TrackerClient
from yandex_tracker_client.objects import Resource

from config_data import settings

logger = logging.getLogger('tracker')


class YNYBTracker:
    def __init__(self):
        self.queue = 'YNYB'
        self.key_tag = 'ready_to_add_to_db'
        self.excluding_tag = 'added_to_db'

        self.tracker_url = 'https://st.yandex-team.ru/'

        self.token = settings.TRACKER_INTERNAL_TOKEN
        self.api_url = 'https://st-api.yandex-team.ru/'

        self.tracker_client = TrackerClient(token=self.token, base_url=self.api_url)

    @property
    def filter_target_issues(self) -> str:
        return 'Queue: {} tags: {} tags: !{} Status: closed "Sort by": Created ASC'.format(
            self.queue, self.key_tag, self.excluding_tag
        )

    def get_issues(self) -> list[Resource]:
        logger.info('Start of the tracker issues search by filter')
        issues = self.tracker_client.issues.find(self.filter_target_issues)
        logger.info(f'{len(issues)} tracker issues found')

        return issues

    def change_key_tag(self, list_issues: list[str | Resource]) -> None:
        if len(list_issues) == 0:
            logger.info(f'List issues for adding a tag {self.excluding_tag} is empty')
            return

        if isinstance(list_issues[0], Resource):
            list_issues = [i.key for i in list_issues]

        logger.info(f'Start bulk update Tracker issues: {list_issues}')

        bulk_change = self.tracker_client.bulkchange.update(
            list_issues,
            tags={'add': [self.excluding_tag]}
        )

        logger.info(f'Tracker bulk_change.status: {bulk_change.status}, next action: bulk_change.wait()')
        bulk_change = bulk_change.wait()
        logger.info(f'Tracker bulk_change.status after wait(): {bulk_change.status}')

        return


ynyb_tracker = YNYBTracker()
