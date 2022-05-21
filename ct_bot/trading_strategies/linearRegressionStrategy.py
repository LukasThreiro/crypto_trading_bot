import numpy as np
from sklearn.linear_model import LinearRegression

class LinearRegressionStrategy:
	def __init__(self, exchangeConnectionName, params):
		self._strategyName = LinearRegressionStrategy.getStrategyName()
		self._exchangeConnectionName = exchangeConnectionName
		self._symbol = params["symbol"]
		self._safeAsset = params["safeAsset"]
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
		self._lotSize = None

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

	def _ensureDataCompletness(self, exchangeConnection):
		if (
				(self._baseAsset is None)
				or (self._quoteAsset is None)
				or (self._lotSize is None)
		):
			info = exchangeConnection.getContractInfo(self._symbol)
			self._baseAsset = info["baseAsset"]
			self._quoteAsset = info["quoteAsset"]
			self._lotSize = info["lotSize"]


	def _baseAssetLimitTransaction(self, exchangeConnection, side, priceOfBaseAsset, logMaker):
		# Uzupełnij informacje o BASE_ASSET i QUOTE_ASSET, jeśli potrzeba
		self._ensureDataCompletness(exchangeConnection)

		# Pobierz info o aktualnym saldzie BASE_ASSET i QUOTE_ASSET
		balances = exchangeConnection.getBalances([self._baseAsset, self._quoteAsset])

		# Ustal kwotę transakcji
		if (side == "BUY"):
			# KUPUJEMY BASE_ASSET po max cenie priceOfBaseAsset [QUOTE_ASSET]
			baseAssetAmount = balances[self._quoteAsset]["walletBalance"] / priceOfBaseAsset
		elif (side == "SELL"):
			# SPRZEDAJEMY BASE_ASSET po min cenie priceOfBaseAsset [QUOTE_ASSET]
			baseAssetAmount = balances[self._baseAsset]["walletBalance"]

		# Upewnij się, że kwota jest wystarczająca
		if (baseAssetAmount / self._lotSize < 1):
			baseAssetAmount = 0

		# Złóż zamówienie
		if (baseAssetAmount > 0):
			exchangeConnection.placeOrder(
				symbol = self._symbol, # symbol
				orderType = "LIMIT", # orderType
				quantity = baseAssetAmount, # quantity
				side = side, # side
				price = priceOfBaseAsset, # price
				tif = "GTC" # Time in Force
			)

		# Zapisz w logach
		if (side == "BUY"):
			if (baseAssetAmount > 0):
				msg = "Złożono zamówienie kupna {0} {1} po max cenie {2} {3} za 1 {1}.".format(
					baseAssetAmount, self._baseAsset, priceOfBaseAsset, self._quoteAsset
				)
			else:
				msg = "Decyzja: dalej trzymaj {0}".format(self._baseAsset)
		elif (side == "SELL"):
			if (baseAssetAmount > 0):
				msg = "Złożono zamówienie sprzedaży {0} {1} po min cenie {2} {3} za 1 {1}.".format(
					baseAssetAmount, self._baseAsset, priceOfBaseAsset, self._quoteAsset
				)
			else:
				msg = "Decyzja: dalej trzymaj {0}".format(self._quoteAsset)

		self._log(logMaker, msg)

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
			if (prediction > currentPrices["ask"] * 1.02):
				# Jeśli przyszła cena BASE_ASSET wyrażona w QUOTE_ASSET będzie wyższa,
				# niż obecnie oferowana cena KUPNA
				self._baseAssetLimitTransaction(exchangeConnection, "BUY", currentPrices["ask"], logMaker)
			elif (prediction < currentPrices["bid"] * (1.0 / 1.02)):
				# Jeśli przyszła cena BASE_ASSET wyrażona w QUOTE_ASSET będzie niższa,
				# niż obecnie oferowana cena SPRZEDAŻY
				self._baseAssetLimitTransaction(exchangeConnection, "SELL", currentPrices["bid"], logMaker)
			else:
				self._log(logMaker, "Niewystarczające przesłanki do podjęcia decyzji")

	def toASafeState(self, exchangeConnection, logMaker):
		self._ensureDataCompletness(exchangeConnection)
		
		# anulowanie wszystkich wiszących zamówień
		exchangeConnection.cancelAllOrders(self._symbol)
		self._log(logMaker, "Anulowano wszystkie zamówienia.")

		if (self._safeAsset is None):
			return

		if (self._safeAsset == self._baseAsset):
			side = "BUY"
		elif (self._safeAsset == self._quoteAsset):
			side = "SELL"

		# Pobierz info o aktualnym saldzie BASE_ASSET i QUOTE_ASSET
		balances = exchangeConnection.getBalances([self._baseAsset, self._quoteAsset])

		# Pobierz info o aktualnych cenach
		currentPrices = exchangeConnection.getBidAsk(self._symbol)

		# Ustal kwotę transakcji
		if (side == "BUY"):
			# KUPUJEMY BASE_ASSET po max cenie priceOfBaseAsset [QUOTE_ASSET]
			priceOfBaseAsset = currentPrices["ask"]
			baseAssetAmount = balances[self._quoteAsset]["walletBalance"] / priceOfBaseAsset
		elif (side == "SELL"):
			# SPRZEDAJEMY BASE_ASSET po min cenie priceOfBaseAsset [QUOTE_ASSET]
			priceOfBaseAsset = currentPrices["bid"]
			baseAssetAmount = balances[self._baseAsset]["walletBalance"]

		# Upewnij się, że kwota jest wystarczająca
		if (baseAssetAmount / self._lotSize < 1.0):
			baseAssetAmount = 0

		# Złóż zamówienie
		if (baseAssetAmount > 0):
			exchangeConnection.placeOrder(
				symbol = self._symbol, # symbol
				orderType = "LIMIT", # orderType
				quantity = baseAssetAmount, # quantity
				side = side, # side
				price = priceOfBaseAsset, # price
				tif = "GTC" # Time in Force
			)

		# Wypisz komunikat w logach
		if (baseAssetAmount > 0):
			self._log(logMaker, "Próba powrotu to bezpiecznej waluty " + self._safeAsset)
		else:
			self._log(logMaker, "Wszystkie środki znajdują się w bezpiecznej walucie " + self._safeAsset)








