import logging
import os
from datetime import datetime


class Logger:

    LOG_FILE_PATH = f"{os.getcwd()}/logs"

    def __init__(self, name, level=logging.DEBUG):

        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        self.create_dir()

        today = datetime.now()
        file_name = today.strftime("Log_%Y%m%d.txt")
        log_file = f"{self.LOG_FILE_PATH}/{file_name}"

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Adicionar os manipuladores ao logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def get_logger(self):
        return self.logger

    def create_dir(self):

        if not os.path.isdir(self.LOG_FILE_PATH):
            os.mkdir(self.LOG_FILE_PATH)
