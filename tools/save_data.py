import csv
import os

from tools.logger import Logger
logger = Logger(__name__).logger


class SaveLotteriesData(object):
    
    def __init__(self):
        self.data_table = None

    def save_data(self, db, data):
        found_data = None
        try:
            found_data = db.find_one(data)
        except Exception as e:
            logger.error(e)

        if not found_data:
            try:
                db.insert_one(data)
                flag = 1
            except Exception as e:
                logger.error(e)
                flag = 0
        else:
            flag = 1
        return flag

    def write_data(self, file, data):
        file_path = os.path.join(os.path.split(os.getcwd())[0], file)
        headers = ','.join(list(data.keys()))
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(headers + '\n')

        content = list(data.values())
        with open(file_path, 'a', encoding='utf-8', newline='') as csv_f:
            csv_writer = csv.writer(csv_f)
            csv_writer.writerow(content)
