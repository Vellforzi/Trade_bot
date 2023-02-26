import datetime
import time


def run(db, stock, settings):  # Checking orders.
    while True:
        orders = db.check_orders(settings.strategy)  # Unfilled old sell-orders from DB.
        print(orders)
        if orders:
            print("There are incomplete sell-orders in DB...")
            for order in orders:
                if order["Sell_order_id"]:
                    print("There was found the sell-order in DB", order)
                    order_info = stock.order_info(order["Instrument"], order["Sell_order_id"])  # Take order from
                    # OKX stock with instrument (e.g. BTC-USDT) and order ID.
                    print("Info from OKX", order_info["data"][0])
                    if order_info.get("code") == '0':
                        order_info = order_info["data"][0]
                        print(f'Order state {order["Sell_order_id"]} = {order_info["state"]}')
                        try:
                            finished_time = datetime.datetime.utcfromtimestamp(int(order_info["fillTime"]) // 1000).\
                                strftime('%Y-%m-%d %H:%M:%S')
                        except ValueError:
                            finished_time = None
                        order_sold_or_not(db, order["Sell_order_id"], order_info["state"], finished_time,
                                          order['Sell_fill_order_price'], order['Buy_fill_order_price'],
                                          order['Sell_fee'])
                    else:
                        errmsg = ''
                        for msg in order_info.get('data', []):
                            errmsg += f"{msg.get('sMsg')}\n"
                        print("No information could be received on the order:", errmsg)
                else:
                    order_info = stock.order_info(order["Instrument"], order["Buy_order_id"])
                    if order_info.get("code") == '0':
                        order_info = order_info["data"][0]
                        print(order_info)
                        print("This is not sell-order. Let's check its buy status...")
                        order_bought_or_not(db, stock, settings, order_info)
                    else:
                        errmsg = ''
                        for msg in order_info.get('data', []):
                            errmsg += f"{msg.get('sMsg')}\n"
                        print("No information could be received on the order:", errmsg)
            print(f"Every orders in DB were checked and updated. Here it is: {orders}")
            print("Now let's work with the new instruments that were chosen.")
        db_pair_list = db.check_bought_orders(settings.strategy)  # The orders list that have a purchase (side = 'buy')
        # (live or filled, no matter).
        ready_pair_list = [x for x in settings.instruments if x not in db_pair_list]  # Difference between user's new
        # instruments list and list with already created "buy" orders.
        # Next we need count all placed sell-orders.
        counter = db.live_sell_order_counter(settings.strategy)  # How many 'live' orders in DB.
        print(f"Amount of sell orders - {counter[0]['count(*)']}")
        if counter[0]["count(*)"] < settings.total_orders:  # Compare variable 'counter' with value from
            # chosen strategy.
            create_orders_by_list(db, stock, ready_pair_list, settings.strategy, settings.trade_mode)  # And create new
            # 'buy' orders with "clean" instruments list.
        else:
            print("There are many incomplete sell orders. Please, wait...")
        time.sleep(settings.time_delay)


def create_orders_by_list(db, stock, ready_pair_list, strategy, trade_mode):  # Placing new buy-orders.
    for inst_id in ready_pair_list:
        print("Place an order...")
        new_orders = stock.create_order(inst_id, "cash", "buy", trade_mode, 100, px=None)  # Last argument with
        # None is quantity to buy or sell. Now I leave it.
        if new_orders.get('code') == '0':
            print("Order(-s) was/were placed...", new_orders)
            for order in new_orders['data']:
                order_info = stock.order_info(inst_id, order["ordId"])
                if order_info.get('code') == '0':
                    print("Order info...", order_info['data'][0])
                    order_info = order_info['data'][0]
                    try:
                        buy_finished = datetime.datetime.utcfromtimestamp(
                            int(order_info["fillTime"]) // 1000).strftime(
                            '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        buy_finished = None
                    buy_order_time = datetime.datetime.utcfromtimestamp(int(order_info["cTime"]) // 1000).\
                        strftime('%Y-%m-%d %H:%M:%S')
                    instrument = order_info["instId"]
                    side = "buy"
                    buy_fill_order_price = order_info["avgPx"]
                    buy_filled_total = order_info["accFillSz"]
                    buy_status = order_info["state"]
                    buy_order_id = order["ordId"]
                    buy_fee = order_info["fee"]
                    db.add_buy_order(buy_order_time, instrument, side, buy_fill_order_price, buy_filled_total,
                                     buy_status, buy_order_id, buy_fee, buy_finished, strategy)  # The function name
                    # speaks for itself.
        else:
            errmsg = ''
            for msg in new_orders.get('data', []):
                errmsg += f"{msg.get('sMsg')}\n"
            print("No information could be received on the order:", errmsg)
        time.sleep(1)


def order_sold_or_not(db, order_id, order_status, finished_time, sell_order_price, buy_order_price, sell_ord_fee):
    if order_status == "filled":
        db.update_sell_order_state(order_status, finished_time, order_id)  # Change order state in DB to 'filled'.
        print(f"Details for order {order_id} were successfully updated.")
        print(f"""Profit: {sell_order_price - (float(buy_order_price) + float(sell_ord_fee))}""")
    elif order_status == "partially_filled":
        db.update_sell_order_state(order_status, order_id, finished_time)
        print(f"Order {order_id} is partially filled.")
    elif order_status == "canceled":
        db.upd_canceled_sell_order(order_id)
        print("Sell order was canceled.")
    else:
        print("Sell order state is live. Please, wait...")


def create_sell_order(db, stock, settings, order_inst, b_filled_total, b_filled_ttl_price, buy_fee, buy_order_id):
    order_price = (float(b_filled_ttl_price) - float(buy_fee)) * (1 + settings.deal_profit)
    new_orders = stock.create_order(order_inst, "cash", "sell", settings.trade_mode, b_filled_total, order_price)
    if new_orders.get('code') == '0':
        print("Order was placed...", new_orders)
        for sell_order in new_orders['data']:
            order_info = stock.order_info(order_inst, sell_order["ordId"])
            if order_info.get('code') == '0':
                order_info = order_info['data'][0]
                print("Order info...", order_info)
                try:
                    finished_time = datetime.datetime.utcfromtimestamp(int(order_info["fillTime"]) // 1000).\
                        strftime('%Y-%m-%d %H:%M:%S')
                except ValueError:
                    finished_time = None
                sell_order_time = datetime.datetime.utcfromtimestamp(int(order_info["cTime"]) // 1000).\
                    strftime('%Y-%m-%d %H:%M:%S')
                db.add_sell_order_in_buy_order(sell_order_time, order_info["px"], order_info["sz"],
                                               order_info["state"], order_info["ordId"], order_info["fee"],
                                               finished_time, buy_order_id)  # Upd info for working instrument
                db.update_buy_order_to_sell(buy_order_id)  # The function name speaks for itself.
                if order_info["state"]:
                    try:
                        finished_time = datetime.datetime.utcfromtimestamp(
                            int(order_info["fillTime"]) // 1000).strftime('%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        finished_time = None
                    order_sold_or_not(db, order_info["ordId"], order_info["state"], finished_time, order_info["px"],
                                      b_filled_ttl_price, order_info["fee"])
                else:
                    print("Sell-order has been placed but for some reason not created in DB.")


def order_bought_or_not(db, stock, settings, order_info):
    if order_info["state"] == "filled":
        buy_finished = datetime.datetime.utcfromtimestamp(int(order_info["fillTime"]) // 1000).\
            strftime('%Y-%m-%d %H:%M:%S')
        db.update_buy_order_state(order_info["state"], buy_finished, order_info["ordId"])  # Change order state in DB
        # to 'filled'.
        print(f"Details for order {order_info['ordId']} were successfully updated. Buy-order is bought. "
              f"Placing sell-order...")
        create_sell_order(db, stock, settings, order_info["instId"], order_info["fillSz"], order_info["fillPx"],
                          order_info["fee"], order_info["ordId"])
    elif order_info["state"] == "partially_filled":
        db.update_buy_order_state(order_info["state"], order_info['ordId'], finished_time=None)
        print(f"Order {order_info['ordId']} is partially filled.")
    elif order_info["state"] == "canceled":
        db.upd_canceled_buy_order(order_info['ordId'])
        print("Buy order was canceled.")
    else:
        print("Buy order state is live. Please, wait...")
