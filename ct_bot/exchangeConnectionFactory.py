from config.exchangeCredentials import ExchangeCredentials
from exchange_connections.binanceConnection import BinanceConnection

class ExchangeConnectionFactory:
	def __init__(self):
		self.credentials = ExchangeCredentials().credentials

	def getExchangeConnection(self, name):
		if (name not in self.credentials.keys()):
			return None

		if (name == "BinanceTestnet"):
			return BinanceConnection(True, name, self.credentials[name])
		elif (name == "Binance"):
			return BinanceConnection(False, name, self.credentials[name])
