from config.exchangeCredentials import ExchangeCredentials
from exchange_connections.binanceConnection import BinanceConnection

class ExchangeConnectionFactory:
	def __init__(self):
		self.credentials = ExchangeCredentials().credentials
		self.exchangeClasses = []

		self.exchangeClasses.append(BinanceConnection)

	def getExchangeConnection(self, name):
		if (name not in self.credentials.keys()):
			return None

		crs = self.credentials[name]

		for c in self.exchangeClasses:
			if (c.getExchange() == crs["exchange"]):
				return c(name, crs)
