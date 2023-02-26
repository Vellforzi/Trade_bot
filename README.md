# Trade_bot
Trade_bot
Hello everyone!
This is my first project in dev. Look, check, comment.:)

This app connects with OKX stock exchange, you choose strategy from strategy and bot complete all trade-path using your strategy (place order, check order and do some actions depending on order state).

STEP 1.
You need to create database 'test' in MySQL and create two tables in this DB.

First table - 'orders':

CREATE TABLE orders (
Buy_order_time datetime,
Instrument varchar(20),
Side varchar(4),
Buy_fill_order_price double,
Buy_filled_total double,
Buy_status varchar(10),
Sell_order_time datetime,
Sell_fill_order_price double,
Sell_filled_total	double,
Sell_status	varchar(10),
Buy_order_id varchar(50),
Sell_order_id	varchar(50),
Buy_fee	double,
Sell_fee double,
Buy_finished datetime,
Sell_finished	datetime,
id int unsigned auto_increment,
Strategy varchar(50)
CONSTRAINT orders_PK PRIMARY KEY (id))

Second table - Settings:

CREATE TABLE Settings (
id int unsigned auto_increment, 
Strategy varchar(20),
Description varchar(150),
Total_orders int,
Deal_profit double,
Instruments varchar(100),
Time_delay double,
Api_key varchar(250),
Api_secret varchar(250),
Pass_phrase varchar(250),
CONSTRAINT settings_PK PRIMARY KEY (id))

AND add some settings. For example:

INSERT INTO settings (Strategy, Description, Total_orders, Deal_profit, Instruments, Time_delay, Api_key, Api_secret, Pass_phrase)
VALUES ('strategy_1', '2% profit with buy and sell comission', 10, 0.02, 'BTC-USDT,LTC-USDT,ETH-USDT,OKB-USDT,JFI-USDT,UNI-USDT',
60, '*your api_key*', '*your api_secret*', '*your pass_phrase*')

First table need for bot, it places order on OKX and add it to DB ('orders' table) and change info of order if it's needed.
Second table is just general options.

STEP 2.
Open Settings.py.

self.db_host = 'your address'
self.db_user = 'your name'
self.db_password = "your password"
self.db_name = 'test'

You need to add your host, user name and password.
Don't use manual_run. It is not finish yet.

That's all. RUN main.py.
