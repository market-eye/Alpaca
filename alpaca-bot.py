import alpaca_trade_api as tradeapi
import threading
from alpaca_trade_api import StreamConn
import datetime
import os
import asyncio
import alpaca_db

# Get environment variables
key_id = os.getenv('APCA_API_KEY_ID')
secret_key = os.environ.get('APCA_API_SECRET_KEY')
base_url =  os.environ.get('APCA_API_BASE_URL')
data_stream = 'alpacadatav1'
ws_url = 'wss://data.alpaca.markets'

database = os.environ['POSTGRES_DB']
dbUser = os.environ['POSTGRES_USER'] 
dbPwd = os.environ['POSTGRES_PASSWORD']
dbHost = os.environ['POSTGRES_SERVICE_HOST']
dbPort = os.environ['POSTGRES_SERVICE_PORT']

script_start = datetime.datetime.now()
symbols = ['AAPL', 'MSFT']
 
print('Do dbInstance')
# Initialise and connect to the database
dbInstance = alpaca_db.PostgresDB(database, dbUser, dbPwd, dbHost, dbPort)

print('Do connApi')
# Connect to the Alpaca API
connApi = tradeapi.stream2.StreamConn(
    key_id, secret_key, base_url=base_url, data_url=ws_url, data_stream=data_stream
)

async def handle_signal(channel, symbol, value):
    if (datetime.datetime.now() - script_start).seconds > 30:
        print('Closing connection for ' + str(symbol))
        await connApi.unsubscribe([r'^T.' + str(symbol), r'^AM.' + str(symbol)])
        dbInstance.close()
    else:
        print(str(channel) + '.' + str(symbol))
        print(str(value))
        print(' ')


@connApi.on(r'^AM.*$', symbols)  # AM. denotes minute bars, symbols is the list of tickers to listen for
async def on_bar(connApi, channel, bar):
    symbol = bar.symbol
    close = float(bar.close)
    print('-- AM Hit --')
    await handle_signal(channel, symbol, close)


@connApi.on(r'^T.*$', symbols)  # T. denotes a trade event, symbols is the list of tickers to listen for
async def on_trade(connApi, channel, trade):
    symbol = str(trade.symbol)
    price = float(trade.price)
    print('-- T Hit --')
    timeNow = datetime.datetime.now()
    command = "INSERT INTO TRADE_AUDIT(ID, SYMBOL, TRADE_PRICE) VALUES ('%s', '%s', %s);" % (timeNow, symbol, price)
    dbInstance.execute(command) 
    await handle_signal(channel, symbol, price)


async def kickoff_trades():
    await connApi.subscribe(['T.AAPL', 'T.MSFT'])


async def kickoff_bars():
    await connApi.subscribe(['AM.AAPL', 'AM.MSFT'])


if __name__ == '__main__':
    print('start CREATE TABLE')
    dbInstance.execute('CREATE TABLE TRADE_AUDIT(ID TIMESTAMP NOT NULL, SYMBOL TEXT NOT NULL,TRADE_PRICE FLOAT NOT NULL, PRIMARY KEY( ID ));')
#    dbInstance.execute('CREATE TABLE TRADE_AUDIT(\
#            ID          TEXT  NOT NULL,\
#            SYMBOL      TEXT  NOT NULL,\
#            TRADE_PRICE FLOAT NOT NULL,\
#            PRIMARY KEY( ID ));')
    print('Done CREATE TABLE ')
    loop = asyncio.new_event_loop()
    loop.create_task(kickoff_trades())
    loop.run_forever()
