
class LinearRegressionStrategy:
	def __init__(self, exchangeConnectionName, params):
		self._strategyName = LinearRegressionStrategy.getStrategyName()
		self._exchangeConnectionName = exchangeConnectionName
		self._symbol = params["symbol"]
		self._runInterval = params["runInterval"] # in minutes
		self._candleInterval = params["candleInterval"] # in seconds
		self._numberOfCandles = params["numberOfCandles"]
		self._index = 0
		self._classString = str({
			"strategyName": LinearRegressionStrategy.getStrategyName(),
			"exchangeConnectionName": exchangeConnectionName,
			"params": params
		})

	def toString(self):
		return self._classString

	@staticmethod
	def getStrategyName():
		return "LinearRegression"

	def getExchangeConnectionName(self):
		return self._exchangeConnectionName

	def checkIfTakeAction(self, minutes, exchangeConnection):
		if ((minutes - 1) % self._runInterval == 0):
			self._index += 1
			print("Mój czas: " + str(minutes) + ", mój indeks: " + str(self._index))