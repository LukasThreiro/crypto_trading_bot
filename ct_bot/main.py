from timeloop import Timeloop
from datetime import timedelta

from logMaker import LogMaker
from exchangeConnectionFactory import ExchangeConnectionFactory

tl = Timeloop()

@tl.job(interval = timedelta(seconds = 1))
def main_loop():
	main_loop.counter += 1

	if (main_loop.counter % 5 == 0):
		print("jedna wiadomość")

if (__name__ == "__main__"):
	main_loop.counter = 0
	LogMaker().info("Start systemu.")

	ss = ExchangeConnectionFactory().getExchangeConnection("BinanceTestnet")
	lolxd = ss.getBidAsk("BTC", "USDT")
	print("result: " + str(lolxd))

	tl.start(block = True)