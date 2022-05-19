import numpy as np
from sklearn.linear_model import LinearRegression

class LinearRegressionStrategy:
	def __init__(self, exchangeConnectionName, params):
		self._strategyName = LinearRegressionStrategy.getStrategyName()
		self._exchangeConnectionName = exchangeConnectionName
		self._symbol = params["symbol"]
		self._runInterval = params["runInterval"] # minutes
		self._candleInterval = params["candleInterval"] # minutes
		self._numberOfCandles = params["numberOfCandles"]
		self._index = 0
		self._classString = str({
			"strategyName": LinearRegressionStrategy.getStrategyName(),
			"exchangeConnectionName": exchangeConnectionName,
			"params": params
		})

		self._baseAsset = None
		self._quoteAsset = None


	def toString(self):
		return self._classString

	@staticmethod
	def getStrategyName():
		return "LinearRegression"

	def getExchangeConnectionName(self):
		return self._exchangeConnectionName

	def _log(self, logMaker, message):
		msg = self._exchangeConnectionName
		msg += " "
		msg += self.getStrategyName()
		msg += " "
		msg += self._symbol
		msg += " index="
		msg += str(self._index)
		msg += ": "
		msg += message

		logMaker.info(msg)

	def _makePrediction(self, histCandles):
		# DATA PREPARATION
		tmpX = []
		tmpY = []
		step = 0

		for candle in histCandles:
			step += 1
			avgPrice = (candle["high"] + candle["low"]) / 2
			tmpX.append(step)
			tmpY.append(avgPrice)

		X = np.array(tmpX).reshape((-1, 1))
		Y = np.array(tmpY)

		# CREATE MODEL AND PREDICT PRICE
		model = LinearRegression()
		model.fit(X, Y)
		component = int((float(self._runInterval) / float(self._candleInterval)) * (0.5))
		newX = np.array([step + component]).reshape((-1, 1))
		predictedY = model.predict(newX)[0]

		return predictedY

	def _baseAssetTransaction(self, exchangeConnection, side, priceOfBaseAsset, logMaker):
		if ((self._baseAsset is None) or (self-_quoteAsset is None)):
			info = exchangeConnection.getContractInfo(self._symbol)
			self._baseAsset = info["baseAsset"]
			self._quoteAsset = info["quoteAsset"]

		balances = exchangeConnection.getBalances([self._baseAsset, self._quoteAsset])




	def checkIfTakeAction(self, minutes, exchangeConnection, logMaker):
		if ((minutes - 1) % self._runInterval == 0):
			self._index += 1

			# MAKE PREDICTION
			histCandles = exchangeConnection.getHistoricalCandles(
				self._symbol, self._candleInterval, self._numberOfCandles
			)

			# Jaka będzie cena 1 BASE_ASSET wyrażona w QUOTE_ASSET
			prediction = self._makePrediction(histCandles)

			# GET CURRENT PRICES
			# currentPrices["bid"]: kwota QUOTE_ASSET, za którą można sprzedać 1 BASE_ASSET
			# currentPrices["ask"]: kwota QUOTE_ASSET, za którą można kupić 1 BASE_ASSET
			# bid < ask
			currentPrices = exchangeConnection.getBidAsk(self._symbol)

			# MAKE A DECISION
			if (prediction > currentPrices["ask"] * 1.01):
				# Jeśli przyszła cena BASE_ASSET wyrażona w QUOTE_ASSET będzie wyższa,
				# niż obecnie oferowana cena KUPNA
				self._baseAssetTransaction(exchangeConnection, "BUY", currentPrices["ask"], logMaker)
			elif (prediction < currentPrices["bid"] * (1.0 / 1.01)):
				# Jeśli przyszła cena BASE_ASSET wyrażona w QUOTE_ASSET będzie niższa,
				# niż obecnie oferowana cena SPRZEDAŻY
				self._baseAssetTransaction(exchangeConnection, "SELL", currentPrices["bid"], logMaker)
			else:
				self._log(logMaker, "Brak akcji")

	def toASafeState(self, exchangeConnection, logMaker):
		pass