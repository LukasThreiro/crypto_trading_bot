from datetime import datetime
import logging

class LogMaker:
	def __init__(self):
		logger = logging.getLogger("crypto_bot")
		logger.setLevel(logging.DEBUG)

		if (logger.hasHandlers()):
			logger.handlers.clear()

		filename = "../logs/{}.log".format(datetime.now().strftime("%Y-%m-%d"))
		formatter = logging.Formatter("\n[%(levelname)s] %(asctime)s | %(message)s", "%Y-%m-%d %H:%M:%S")

		file_handler = logging.FileHandler(filename, mode = "a", encoding = "utf-8", delay = False)
		file_handler.setFormatter(formatter)

		logger.addHandler(file_handler)

		self.logger = logger

	def debug(self, message):
		self.logger.debug(message)

	def info(self, message):
		self.logger.info(message)

	def warning(self, message):
		self.logger.warning(message)

	# Gdy coś pójdzie nie tak w bloku TRY
	def exception(self, message):
		self.logger.exception(message)