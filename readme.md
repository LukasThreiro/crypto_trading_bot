# Crypto Trading Bot

## Przygotowanie środowiska
(wszystko robimy z poziomu folderu crypto_trading_bot)

`sudo apt-get update`

`sudo apt-get install python3`

`sudo apt-get install python3-pip`

`sudo apt-get install python3-virtualenv`

`virtualenv .venv`

`. .venv/bin/activate`

`pip3 install -e .`


Następnie w katalogu ct_bot/config należy utworzyć następujące pliki konfiguracyjne:

1. Plik exchangeCredentials.py zawierający dane niezbędne do połączenia się z poszczególnymi giełdami (na podstawie pliku exchangeCredentialsExample.py)

2. Plik strategyPlanner.py zawierający konfigurację strategii, i ich przydział do konkretnych giełd (na podstawie pliku strategyPlannerExample.py)

## Uruchamianie systemu

Z poziomu głównego folderu wywołujemy

`bash run.sh`

