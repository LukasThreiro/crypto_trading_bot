
class StrategyPlanner:
	def __init__(self):
		self.scheme = [
			{
				"exchange": "BinanceTestnetFeatures",
				"strategyName": "LinearRegression",
				"strategyParams": {
					"symbol": "WAVESUSDT",
					"safeAsset": "USDT",
					"runInterval": 10, # minutes
					"candleInterval": 1, # minutes
					"numberOfCandles": 12
				}
			},
			{
				"exchange": "BinanceTestnetFeatures",
				"strategyName": "LinearRegression",
				"strategyParams": {
					"symbol": "BNBBUSD",
					"safeAsset": "BUSD",
					"runInterval": 10, # minutes
					"candleInterval": 1, # minutes
					"numberOfCandles": 12
				}
			}
		]