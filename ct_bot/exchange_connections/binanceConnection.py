import time
import requests
import json
import hmac
import hashlib

from urllib.parse import urlencode


class BinanceConnection:
	def __init__(self, name, credentials):
		self._exchange = BinanceConnection.getExchange()
		self._name = name
		self._testnet = credentials["is_testnet"]
		self._futures = credentials["is_futures"]
		self._base_url = credentials["base_url"]
		self._public_key = credentials["public_key"]
		self._secret_key = credentials["secret_key"]
		self._headers = {"X-MBX-APIKEY": self._public_key}

	@staticmethod
	def getExchange():
		return "Binance"

	def _makeRequest(self, method, endpoint, data):
		if (method == "GET"):
			response = requests.get(self._base_url + endpoint, params = data, headers = self._headers)
		elif (method == "POST"):
			response = requests.post(self._base_url + endpoint, params = data, headers = self._headers)
		elif (method == "DELETE"):
			response = requests.delete(self._base_url + endpoint, params = data, headers = self._headers)
		else:
			raise ValueError()

		if (response.status_code == 200):
			return response.json()
		else:
			raise Exception("_makeRequest status code: " + str(response.status_code))

	def _generateSignature(self, data):
		signature = hmac.new(
			self._secret_key.encode(),
			urlencode(data).encode(),
			hashlib.sha256
		).hexdigest()

		return signature

	def _tickToDecimals(self, tickSize):
		tickSizeStr = "{0:.8f}".format(tickSize)

		while (tickSizeStr[-1] == "0"):
			tickSizeStr = tickSizeStr[:-1]

		splitTick = tickSizeStr.split(".")

		if (len(splitTick) > 1):
			return len(splitTick[1])
		else:
			return 0

	# for binance spot only
	def _getExecutionPrice(self, symbol, orderID):
		info = self.getContractInfo(symbol)

		data = dict()
		data["timestamp"] = int(time.time() * 1000)
		data["symbol"] = symbol
		data["signature"] = self._generateSignature(data)

		trades = self._makeRequest("GET", "/api/v3/myTrades", data)
		avgPrice = 0

		if (trades is not None):
			executedQty = 0

			for t in trades:
				if t["orderId"] == orderID:
					executedQty += float(t["qty"])

			for t in trades:
				if t["orderId"] == orderID:
					fillPct = float(t["qty"]) / executedQty
					avgPrice += (float(t["price"]) * fillPct)

		return round(round(avgPrice / info["tickSize"]) * info["tickSize"], 8)

	def _prepareOrderStatus(self, orderStatus):
		if (orderStatus is None):
			return None

		if (not self._futures):
			if (orderStatus["status"] == "FILLED"):
				orderStatus["avgPrice"] = self._getExecutionPrice(symbol, orderStatus["orderId"])
			else:
				orderStatus["avgPrice"] = 0

		response = dict()
		response["orderID"] = orderStatus["orderId"]
		response["status"] = orderStatus["status"].lower()
		response["avgPrice"] = float(orderStatus["avgPrice"])
		response["executedQty"] = float(orderStatus["executedQty"])

		return response

	def getContractInfo(self, symbol):
		if (self._futures):
			exchangeInfo = self._makeRequest("GET", "/fapi/v1/exchangeInfo", dict())
		else:
			exchangeInfo = self._makeRequest("GET", "/api/v3/exchangeInfo", dict())

		contracts = dict()

		if (exchangeInfo is not None):
			for contractData in exchangeInfo["symbols"]:
				contracts[contractData["symbol"]] = contractData

		if (symbol not in contracts.keys()):
			return None

		rawInfo = contracts[symbol]
		info = dict()

		info["symbol"] = rawInfo["symbol"]
		info["baseAsset"] = rawInfo["baseAsset"]
		info["quoteAsset"] = rawInfo["quoteAsset"]

		if (self._futures):
			info["priceDecimals"] = rawInfo["pricePrecision"]
			info["quantityDecimals"] = rawInfo["quantityPrecision"]
			info["tickSize"] = 1 / pow(10, rawInfo["pricePrecision"])
			info["lotSize"] = 1 / pow(10, rawInfo["quantityPrecision"])
		else:
			for bFilter in rawInfo["filters"]:
				if (bFilter["filterType"] == "PRICE_fILTER"):
					info["tickSize"] = float(bFilter["tickSize"])
					info["priceDecimals"] = self._tickToDecimals(float(bFilter["tickSize"]))

				if (bFilter["filterType"] == "LOT_SIZE"):
					info["lotSize"] = float(bFilter["stepSize"])
					info["quantityDecimals"] = self._tickToDecimals(float(bFilter["stepSize"]))

		return info

	def getBidAsk(self, symbol):
		data = dict()
		data["symbol"] = symbol

		if (self._futures):
			ob_data = self._makeRequest("GET", "/fapi/v1/ticker/bookTicker", data)
		else:
			ob_data = self._makeRequest("GET", "/api/v3/ticker/bookTicker", data)

		response = {
			"symbol": data["symbol"],
			"bid": float(ob_data["bidPrice"]),
			"bidQty": float(ob_data["bidQty"]),
			"ask": float(ob_data["askPrice"]),
			"askQty": float(ob_data["askQty"])
		}

		return response

	def getHistoricalCandles(self, symbol, interval, limit):
		data = dict()
		data["symbol"] = symbol
		data["interval"] = interval

		if (limit > 1000):
			raise Exception("Max number of candles on Binance Spot is 1000")
		else:
			data["limit"] = limit

		if (self._futures):
			raw_candles = self._makeRequest("GET", "/fapi/v1/klines", data)
		else:
			raw_candles = self._makeRequest("GET", "/api/v3/klines", data)

		candles = []

		for raw_candle in raw_candles:
			c = dict()
			c["symbol"] = data["symbol"]
			c["openTS"] = raw_candle[0]
			c["open"] = raw_candle[1]
			c["high"] = raw_candle[2]
			c["low"] = raw_candle[3]
			c["close"] = raw_candle[4]
			c["volume"] = raw_candle[5]
			c["closeTS"] = raw_candle[6]
			candles.append(c)

		return sorted(candles, key = lambda d: d["openTS"])

	def getBalances(self, assets):
		data = dict()
		data["timestamp"] = int(time.time() * 1000)
		data["signature"] = self._generateSignature(data)

		if (self._futures):
			accountData = self._makeRequest("GET", "/fapi/v1/account", data)
		else:
			accountData = self._makeRequest("GET", "/api/v3/account", data)

		if (accountData is None):
			return None

		assetsDict = dict()

		if (self._futures):
			for x in accountData["assets"]:
				tmp = dict()
				tmp["walletBalance"] = float(x["walletBalance"])
				tmp["marginBalance"] = float(x["marginBalance"])
				assetsDict[x["asset"]] = tmp
		else:
			for x in accountData["balances"]:
				tmp = dict()
				tmp["walletBalance"] = float(x["free"])
				tmp["marginBalance"] = 0.0
				assetsDict[x["asset"]] = tmp

		balances = dict()

		for a in assets:
			if (a in assetsDict.keys()):
				balances[a] = assetsDict[a]
			else:
				balances[a] = {"walletBalance": 0.0, "marginBalance": 0.0}

		return balances

	def placeOrder(self, symbol, orderType, quantity, side, price = None, tif = None):
		info = self.getContractInfo(symbol)

		if (info is None):
			raise Exception("Market %s not available", baseAsset + quoteAsset)

		data = dict()
		data["symbol"] = symbol
		data["side"] = side
		data["quantity"] = round(int(quantity / info["lotSize"]) * info["lotSize"], 8)
		data["type"] = orderType.upper()

		if (price is not None):
			data["price"] = round(round(price / info["tickSize"]) * info["tickSize"], 8)
			data["price"] = "%.*f" % (info["priceDecimals"], data["price"])  # Avoids scientific notation

		if (tif is not None):
			data["timeInForce"] = tif

		data["timestamp"] = int(time.time() * 1000)
		data["signature"] = self._generateSignature(data)

		if (self._futures):
			orderStatus = self._makeRequest("POST", "/fapi/v1/order", data)
		else:
			orderStatus = self._makeRequest("POST", "/api/v3/order", data)

		return self._prepareOrderStatus(orderStatus)


	def canelOrder(self, symbol, orderID):
		data = dict()
		data["orderId"] = orderID
		data["symbol"] = symbol
		data["timestamp"] = int(time.time() * 1000)
		data["signature"] = self._generateSignature(data)

		if (self._futures):
			orderStatus = self._makeRequest("DELETE", "/fapi/v1/order", data)
		else:
			orderStatus = self._makeRequest("DELETE", "/api/v3/order", data)

		return self._prepareOrderStatus(orderStatus)


	def getOrderStatus(self, symbol, orderID):
		data = dict()
		data["orderId"] = orderID
		data["symbol"] = symbol
		data["timestamp"] = int(time.time() * 1000)
		data["signature"] = self._generateSignature(data)

		if (self._futures):
			orderStatus = self._makeRequest("GET", "/fapi/v1/order", data)
		else:
			orderStatus = self._makeRequest("GET", "/api/v3/order", data)

		return self._prepareOrderStatus(orderStatus)




