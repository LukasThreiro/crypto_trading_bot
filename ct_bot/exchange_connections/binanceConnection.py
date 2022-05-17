import requests
import json

class BinanceConnection:
	def __init__(self, is_testnet, name, credentials):
		self._name = name
		self._testnet = is_testnet
		self._base_url = credentials["base_url"]
		self._public_key = credentials["public_key"]
		self._secret_key = credentials["secret_key"]
		self._headers = {'X-MBX-APIKEY': self._public_key}

	def getName(self):
		return self._name

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
			raise Exception("ERROR _makeRequest status code: " + str(response.status_code))


	def getBidAsk(self, baseAsset, quoteAsset):
		data = dict()
		data["symbol"] = baseAsset + quoteAsset
		ob_data = self._makeRequest("GET", "/api/v3/ticker/bookTicker", data)

		response = {
			"symbol": data["symbol"],
			"bid": float(ob_data["bidPrice"]),
			"bidQty": float(ob_data["bidQty"]),
			"ask": float(ob_data["askPrice"]),
			"askQty": float(ob_data["askQty"])
		}

		return response