from trading_strategies.linearRegressionStrategy import LinearRegressionStrategy

class StrategyFactory:
	def __init__(self):
		self.strategies = []
		self.strategies.append(LinearRegressionStrategy)

	def getStrategy(self, name, exchangeConnectionName, params):
		for s in self.strategies:
			if (s.getStrategyName() == name):
				return s(exchangeConnectionName, params)
