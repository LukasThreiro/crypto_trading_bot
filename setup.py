from setuptools import setup

setup(
	name = "crypto_trading_bot",
	include_package_data = True,
	packages = ["ct_bot", "logs"],
	install_requires = [
		"timeloop",
		"requests",
		"numpy",
		"scikit-learn"
	]
)