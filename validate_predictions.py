import json
import logging.config

from db.predictions import fill_data_predictions


logging.config.fileConfig('logging.ini')
logging.getLogger('main').propagate = False
logging.getLogger('predictions').propagate = False
logging.getLogger('tracker').propagate = False


def validate():
    with open("predictions.json", "r+", encoding='utf-8') as f:
        all_predictions = json.load(f)

    with open("good_predictions.json", "r+", encoding='utf-8') as f:
        good_predictions = json.load(f)

    try:
        for prediction in all_predictions:
            if prediction in good_predictions:
                continue

            print(prediction)

            flag = str(input("Добавить (д/н)?: "))
            if flag.lower() == 'д' or flag.lower() == '':
                good_predictions.append(prediction)

            print()

    except (Exception, KeyboardInterrupt):
        raise
    finally:
        with open(f"good_predictions.json", "w+", encoding='utf-8') as f:
            json.dump(good_predictions, f, ensure_ascii=False, indent=2)


def fill_db_data():
    with open("good_predictions.json", "r+", encoding='utf-8') as f:
        good_predictions = json.load(f)

    flag = str(input("Добавляем good_predictions в БД (д/н)?: "))
    if flag.lower() == 'д' or flag.lower() == '':
        fill_data_predictions(good_predictions)


if __name__ == "__main__":
    # validate()
    fill_db_data()
