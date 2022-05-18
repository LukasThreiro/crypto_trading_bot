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

	binanceTest = ExchangeConnectionFactory().getExchangeConnection("BinanceTestnet")
	#response = binanceTest.placeOrder("WAVESUSDT", "LIMIT", 12, "BUY", 6.1, "GTC")
	response = binanceTest.canelOrder("WAVESUSDT", 46706760)
	print("response:\n" + str(response))


	tl.start(block = True)