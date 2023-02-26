import datetime


def run(db, stock):
    while True:

        menu = """
    0. Подключиться к DB
    1. Подключиться к API
    2. Получить список ордеров.
    3. Получить информацию по ордеру.
    4. Проверить баланс.
    5. Создать ордер.
    6. Отменить ордер.
    7. Свечи.
    8. Тикерсы.
    9. Посмотреть всех пользователей в базе данных.
    10. Посмотреть список баз данных.
    11. Создать таблицу.
    12. Показать таблицы.
    13. Открыть таблицу.
    14. Обновить ордер.
    14. Exit
    """
        print(menu)
        choice = input("Выберите пункт: ")

        try:
            if choice == "2":
                print("Получаем список ордеров...")
                all_orders = stock.orders_list()
                ord_list = []
                if all_orders.get('code') == '0':
                    for order in all_orders.get('data', []):
                        ord_list.append(order.get('ordId'))
                    print("Список ордеров получен:", ord_list)
                else:
                    errmsg = ''
                    for msg in all_orders.get('data', []):
                        errmsg += f"{msg.get('sMsg')}\n"
                    print("Не удалось получить список ордеров:", errmsg)
                if not ord_list:
                    print("Список ордеров пуст.")

            elif choice == "3":
                print("Получаем информацию по ордеру...")
                instrument = input("Инструмент ордера: ")
                order_id = input("ID ордера: ")
                order_info = stock.order_info(instrument, order_id)
                order_dict = {}
                if order_info.get('code') == '0':
                    for order in order_info['data']:
                        order_dict.update(order)
                    new_time = datetime.datetime.utcfromtimestamp(int(order_dict["cTime"])//1000).strftime('%Y-%m-%d %H:%M:%S')
                    res = (f'("{new_time}", "{order_dict["instType"]}", "{order_dict["instId"]}", '
                           f'"{order_dict["side"]}", {order_dict["px"]}, {order_dict["sz"]}, '
                           f'"{order_dict["reduceOnly"]}", "{order_dict["state"]}")')
                    print(res)
                    q = input("Записать данные в таблицу?(y/n) ")
                    if q == "y":
                        db.insert_into(res)
                else:
                    errmsg = ''
                    for msg in order_info.get('data', []):
                        errmsg += f"{msg.get('sMsg')}\n"
                    print("Не удалось получить информацию по ордеру:", errmsg)

            elif choice == "4":
                print("Проверяем баланс...")
                positions = stock.get_positions()
                print(positions)
                instrument = input("Валюта: ")
                acc_balance = stock.get_balance(instrument)
                if acc_balance.get('code') == '0':
                    print(acc_balance)
                else:
                    errmsg = ''
                    for msg in acc_balance.get('data', []):
                        errmsg += f"{msg.get('sMsg')}\n"
                    print("Не удалось получить баланс:", errmsg)

            elif choice == "5":
                print("Создаём ордер...")
                instrument = input("Инструмент: ")
                trade_mode = input("Режим торговли: ")
                buy_sell = input("Buy или sell: ")
                order_type = input("Тип заказа: ")
                amount = input("Количество валюты: ")
                order_price = input("Цена ордера: ")
                new_order = stock.create_order(instrument, trade_mode, buy_sell, order_type, amount, order_price)
                if new_order.get('code') == '0':
                    print("Ордер размещён.")
                    print(new_order)
                else:
                    errmsg = ''
                    for msg in new_order.get('data', []):
                        errmsg += f"{msg.get('sMsg')}\n"
                    print("Не удалось создать ордер:", errmsg)

            elif choice == "6":
                instrument = input("Инструмент: ")
                order_id = input("ID ордера: ")
                order_cancelling = stock.cancel_order(instrument, order_id)
                if order_cancelling.get('code') == '0':
                    ord_list = []
                    for order in order_cancelling.get('data', []):
                        ord_list.append(order.get('ordId'))
                    print("Список отменённых ордеров", ord_list)
                else:
                    errmsg = ''
                    for msg in order_cancelling.get('data', []):
                        errmsg += f"{msg.get('sMsg')}\n"
                    print("Не удалось отменить ордера", errmsg)

            elif choice == "7":
                candlesticks = stock.candlesticks('BTC-USDT', limit=1)
                candles_keys = ['ts', 'o', 'h', 'l', 'c', 'vol', 'volCcy', 'volCcyQuote', 'confirm']
                candles_list = []
                candles_dict = {}
                for candle in candlesticks['data']:
                    candles_row = dict(zip(candles_keys, candle))
                    candles_list.append(candles_row)
                    candles_dict.update({candles_row['ts']: candles_row})
                print(candles_list)
                print(candles_dict)

            elif choice == "8":
                tickers = stock.tickers('SPOT')
                print(tickers)
                print(len(tickers['data']))

            elif choice == "9":
                print(db.all_users())

            elif choice == "10":
                print(db.show_db())

            elif choice == "11":
                print(db.create_table())

            elif choice == "12":
                print(db.show_tables())

            elif choice == "13":
                print(db.open_table())
                q = input("Создать новый ордер?(y/n) ")
                if q == "y":
                    return stock.create_order(instId=input("Инструмент: "),
                                              tdMode=input("Режим торговли: "),
                                              side=input("Buy или sell: "),
                                              ordType=input("Тип заказа: "),
                                              sz=input("Количество валюты: "),
                                              px=input("Цена ордера: "))

            elif choice == "14":
                print(db.add_sell_order_in_buy_order())

            else:
                return
        except AttributeError:
            err_connections = []
            if not db:
                err_connections.append('к DB')
            if not stock:
                err_connections.append('к API')

            print(f"Вы не подключены {' и '.join(err_connections)}")