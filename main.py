from datetime import datetime

from db import db_ydb
from schemas import Prediction


def main():
    db_ydb.add_list_predictions([
        Prediction(
            prediction_id=1,
            dttm_created=datetime.now(),
            text='test prediction 1'
        )
    ])


if __name__ == '__main__':
    main()
