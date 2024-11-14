from datetime import datetime

import db
from schemas import Prediction


def main():
    db.add_list_predictions([
        Prediction(
            prediction_id=1,
            dttm_created=datetime.now(),
            text='test prediction 1'
        )
    ])


if __name__ == '__main__':
    main()
