from datetime import datetime
import logging

class LogMaker:
	def __init__(self):
		logger = logging.getLogger("crypto_bot")
		logger.setLevel(logging,INFO)

		if (logger.hasHandlers()):
			logger.handlers.clear()

		filename = "logs/{}.log".format(datetime.now().strftime("%Y-%m-%d"))
		formatter = logging.Formatter("\n[%(levelname)s] %(asctime)s | %(message)s", "%Y-%m-%d %H:%M:%s")

		file_handler = logging.FileHandler(filename, encoding = "utf-8")
		file_handler.setFormatter(formatter)

		logger.addHandler(file_handler)

		self.logger = logger

	def logInfo(self, message):
		self.logger.info(message)

	def logWarning(self, message):
		self.logger.warning(message)

	# Gdy coś pójdzie nie tak w bloku TRY
	def logError(self, message):
		self.logger.exception(message)