from logMaker import LogMaker
from exchangeConnectionFactory import ExchangeConnectionFactory
from strategyFactory import StrategyFactory
from config.strategyPlanner import StrategyPlanner

logMaker = LogMaker()
logMaker.info("Rozpoczęcie przywracania stanu bezpiecznego.")

# WCZYTANIE PLANU DZIAŁANIA
plan = StrategyPlanner().plan

# UTWORZENIE POTRZEBNYCH POŁĄCZEŃ DO GIEŁD
connFactory = ExchangeConnectionFactory()
neededExchangeConnections = dict()

for c in plan:
	if (c["exchangeConnection"] not in neededExchangeConnections.keys()):
		try:
			conn = connFactory.getExchangeConnection(c["exchangeConnection"])

			if (conn is None):
				Exception()

			neededExchangeConnections[c["exchangeConnection"]] = conn
					
		except:
			logMaker.exception("Nie udało się utworzyć połączenia z giełdą " + c["exchangeConnection"])
			exit()


# UTWORZENIE STRATEGII
strFactory = StrategyFactory()
scheme = []

for p in plan:
	try:
		strategy = strFactory.getStrategy(
			p["strategyName"],
			p["exchangeConnection"],
			p["strategyParams"]
		)

		if (strategy is None):
			Exception()

		scheme.append(strategy)
	except:
		logMaker.exception("Nie udało się utworzyć strategii " + str(p))
		exit()

for strategy in scheme:
	conn = neededExchangeConnections[strategy.getExchangeConnectionName()]

	try:
		strategy.toASafeState(conn, logMaker)
	except:
		logMaker.exception(
			"Błąd podczas podejmowania akcji przez strategię " + strategy.toString()
		)

logMaker.info("Przywrócono stan bezpieczny.")