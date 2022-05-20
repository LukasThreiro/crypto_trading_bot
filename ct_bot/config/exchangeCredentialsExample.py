class ExchangeCredentials:
	def __init__(self):
		self.credentials = {
			"BinanceTestnetSpot": {
				"exchange": "Binance",
				"is_testnet": True,
				"is_futures": True,
				"base_url": "https://testnet.binancefuture.com",
				"public_key": "",
				"secret_key": ""
			},
			"BinanceTestnetFeatures": {
				"exchange": "Binance",
				"is_testnet": True,
				"is_futures": True,
				"base_url": "https://testnet.binancefuture.com",
				"public_key": "",
				"secret_key": ""
			},
			"BinanceSpot": {
				"exchange": "Binance",
				"is_testnet": False,
				"is_futures": False,
				"base_url": "https://api.binance.com",
				"public_key": "",
				"secret_key": ""
			},
			"BinanceFeatures": {
				"exchange": "Binance",
				"is_testnet": False,
				"is_futures": True,
				"base_url": "https://fapi.binance.com",
				"public_key": "",
				"secret_key": ""
			}
		}