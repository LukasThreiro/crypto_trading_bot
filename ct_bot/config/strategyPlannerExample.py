
class StrategyPlanner:
	def __init__(self):
		self.scheme = [
			{
				"exchange": "BinanceTestnet",
				"strategyName": "LinearRegression",
				"strategyParams": {
					"symbol": "WAVESUSDT",
					"runInterval": 10, # minutes
					"candleInterval": 60, # seconds
					"numberOfCandles": 12
				}
			},
			{
				"exchange": "BinanceTestnet",
				"strategyName": "LinearRegression",
				"strategyParams": {
					"symbol": "BNBBUSD",
					"runInterval": 10, # minutes
					"candleInterval": 60, # seconds
					"numberOfCandles": 12
				}
			}
		]