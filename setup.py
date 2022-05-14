from setuptools import setup

setup(
	name = "crypto_trading_bot",
	include_package_data = True,
	install_requires = [
		"xlrd",
		"cx_Oracle"
	]
)