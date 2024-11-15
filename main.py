import iso8601
from schemas import Prediction

import db
from tracker import ynyb_tracker

import logging.config

logging.config.fileConfig('logging.ini')
logger = logging.getLogger('main')

logging.getLogger('main').propagate = False
logging.getLogger('predictions').propagate = False
logging.getLogger('tracker').propagate = False


def get_list_predictions():
    logger.info('Start take Tracker issues for data_predictions')

    list_issues = ynyb_tracker.get_issues()
    current_prediction_id = db.get_max_prediction_id() + 1

    _list_predictions = []
    for prediction_id, issue in enumerate(list_issues, start=current_prediction_id):
        _list_predictions.append(
            Prediction(
                prediction_id=prediction_id,
                author_staff_login=issue.createdBy.id,
                dttm_created=iso8601.parse_date(issue.createdAt),
                text=issue.text_prediction,
                issue_key=issue.key
            )
        )
    logger.info(f'The list predictions was received successfully: {_list_predictions}')
    return _list_predictions


def main():
    db.add_list_predictions(list_predictions=get_list_predictions())


if __name__ == '__main__':
    main()
