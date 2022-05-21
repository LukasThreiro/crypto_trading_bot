from timeloop import Timeloop
from datetime import timedelta

from logMaker import LogMaker
from exchangeConnectionFactory import ExchangeConnectionFactory
from strategyFactory import StrategyFactory
from config.strategyPlanner import StrategyPlanner

tl = Timeloop()

@tl.job(interval = timedelta(minutes = 1))
def main_loop():
	main_loop.counter += 1
	main_loop.logMaker.info("Rozpoczęcie przebiegu pętli numer " + str(main_loop.counter))

	for strategy in main_loop.scheme:
		conn = main_loop.conns[strategy.getExchangeConnectionName()]

		try:
			strategy.checkIfTakeAction(main_loop.counter, conn, main_loop.logMaker)
		except:
			main_loop.logMaker.exception(
				"Błąd podczas podejmowania akcji przez strategię " + strategy.toString()
			)

if (__name__ == "__main__"):
	logMaker = LogMaker()
	logMaker.info("Start systemu.")

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

	# PRZYPISANIE DO PĘTLI
	main_loop.counter = 0
	main_loop.conns = neededExchangeConnections
	main_loop.scheme = scheme
	main_loop.logMaker = logMaker

	# URUCHOMIENIE SYSTEMU
	tl.start(block = True)
	