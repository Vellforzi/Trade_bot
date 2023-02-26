import mysql.connector
import threading


class DBWorker:

    def __init__(self, db_host, db_user, db_password, db_name):
        self.db_host = db_host
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        self.lock = threading.Lock()
        self.conn, self.db_cursor = self.connect()

    @property
    def cursor(self):
        self.reconnect()
        return self.db_cursor

    def connect(self):
        conn = mysql.connector.connect(
            user=self.db_user,
            password=self.db_password,
            host=self.db_host,
            database=self.db_name,
            buffered=True,
            # charset="utf8",
            autocommit=True,
            auth_plugin='mysql_native_password',
        )
        return conn, conn.cursor(dictionary=True)

    def reconnect(self):
        if not self.conn.is_connected():
            self.conn, self.db_cursor = self.connect()

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def all_users(self, ):
        q = """select * from users
                    """
        try:
            a = 2/0
            self.lock.acquire(True)
            self.cursor.execute(q)
            answer = self.cursor.fetchall()
            return answer
        except Exception as e:
            print(e)
        finally:
            self.lock.release()

    def add_user(self, user_id, name, login, password):
        q = """insert into users (id, name, login, password, created_dt) values (%s, %s, %s, %s, now())
                    """
        try:
            self.lock.acquire(True)
            self.cursor.execute(q, (user_id, name, login, password))
        finally:
            self.lock.release()

    def show_db(self):
        q = """SHOW DATABASES"""
        try:
            self.lock.acquire(True)
            self.cursor.execute(q)
            answer = self.cursor.fetchall()
            return answer
        except Exception as e:
            print(e)
        finally:
            self.lock.release()

    def create_table(self):
        tb_name = input("Table name: ")
        column_name = input("Column and its values (eg. Side VARCHAR(4)): ")
        q = f"CREATE TABLE {tb_name}({column_name})"
        try:
            self.lock.acquire(True)
            self.cursor.execute(q)
        except Exception as e:
            print(e)
        finally:
            self.lock.release()

    def show_tables(self):
        q = """SHOW TABLES"""
        try:
            self.lock.acquire(True)
            self.cursor.execute(q)
            answer = self.cursor.fetchall()
            return answer
        except Exception as e:
            print(e)
        finally:
            self.lock.release()

    def describe_table(self):
        tb_name = input("Table name: ")
        q = f"DESCRIBE {tb_name}"
        try:
            self.lock.acquire(True)
            self.cursor.execute(q)
            answer = self.cursor.fetchall()
            return answer
        except Exception as e:
            print(e)
        finally:
            self.lock.release()

    def open_table(self, ):
        tb_name = input("Table name: ")
        q = f"select * from {tb_name}"
        try:
            self.lock.acquire(True)
            self.cursor.execute(q)
            answer = self.cursor.fetchall()
            return answer
        except Exception as e:
            print(e)
        finally:
            self.lock.release()

    def insert_into(self, res):
        tb_name = input("Table name: ")
        q = f"INSERT INTO {tb_name} VALUES {res}"
        try:
            self.lock.acquire(True)
            self.cursor.execute(q)
            print(f"Data successfully added to the DB, in {tb_name} table")
        except Exception as e:
            print(e)
        finally:
            self.lock.release()

    def check_all_orders(self):
        q = f"SELECT * FROM orders WHERE Sell_finished IS NULL"
        try:
            self.lock.acquire(True)
            self.cursor.execute(q)
            answer = self.cursor.fetchall()
            return answer
        except Exception as e:
            print(e)
        finally:
            self.lock.release()

    def check_orders(self, strategy):
        q = f"SELECT * FROM orders WHERE Sell_finished IS NULL AND Strategy = %s"
        try:
            self.lock.acquire(True)
            self.cursor.execute(q, (strategy,))
            answer = self.cursor.fetchall()
            return answer
        except Exception as e:
            print(e)
        finally:
            self.lock.release()

    def check_bought_orders(self, strategy):
        q = f"SELECT Instrument FROM orders WHERE Side = 'buy' AND Strategy = %s"
        try:
            self.lock.acquire(True)
            self.cursor.execute(q, (strategy,))
            answer = self.cursor.fetchall()
            return answer
        except Exception as e:
            print(e)
        finally:
            self.lock.release()

    def add_buy_order(self, buy_order_time, instrument, side, buy_fill_order_price, buy_filled_total,
                      buy_status, buy_order_id, buy_fee, buy_finished, strategy):
        q = f"""INSERT INTO orders (Buy_order_time, Instrument, Side, 
        Buy_fill_order_price, Buy_filled_total, Buy_status, Buy_order_id, Buy_fee, Buy_finished, Strategy) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        try:
            self.lock.acquire(True)
            self.cursor.execute(q, (buy_order_time, instrument, side, buy_fill_order_price,
                                    buy_filled_total, buy_status, buy_order_id, buy_fee, buy_finished, strategy))
            print(f"Data successfully added to the DB, in 'orders' table.")
        except Exception as e:
            print(e)
        finally:
            self.lock.release()

    def add_sell_order_in_buy_order(self, sell_order_time, sell_fill_order_price, sell_filled_total, sell_status,
                                    sell_order_id, sell_fee, sell_finished, buy_order_id):
        q = f"""UPDATE orders SET Sell_order_time = %s, Sell_fill_order_price = %s, Sell_filled_total = %s, 
        Sell_status = %s, Sell_order_id = %s, Sell_fee = %s, Sell_finished = %s WHERE Buy_order_id = %s"""
        try:
            self.lock.acquire(True)
            self.cursor.execute(q, (sell_order_time, sell_fill_order_price, sell_filled_total, sell_status,
                                    sell_order_id, sell_fee, sell_finished, buy_order_id))
            print(f"Data successfully added to the DB, in 'orders' table.")
        except Exception as e:
            print(e)
        finally:
            self.lock.release()

    def update_buy_order_to_sell(self, buy_order_id):
        q = f"""UPDATE orders SET Side = 'sell' WHERE Buy_order_id = %s"""
        try:
            self.lock.acquire(True)
            self.cursor.execute(q, (buy_order_id,))
        except Exception as e:
            print(e)
        finally:
            self.lock.release()

    def update_sell_order_state(self, sell_status, sell_finished, sell_order_id):
        q = f"""UPDATE orders SET Sell_status = %s, Sell_finished = %s WHERE Sell_order_id = %s"""
        try:
            self.lock.acquire(True)
            self.cursor.execute(q, (sell_status, sell_finished, sell_order_id))
        except Exception as e:
            print(e)
        finally:
            self.lock.release()

    def update_buy_order_state(self, buy_status, buy_finished, buy_order_id):
        q = f"""UPDATE orders SET Buy_status = %s, Buy_finished = %s WHERE Buy_order_id = %s"""
        try:
            self.lock.acquire(True)
            self.cursor.execute(q, (buy_status, buy_finished, buy_order_id))
        except Exception as e:
            print(e)
        finally:
            self.lock.release()

    def upd_canceled_sell_order(self, sell_order_id):
        q = f"""UPDATE orders SET Side = 'buy', Sell_order_time = null, Sell_fill_order_price = null, 
        Sell_filled_total = null, Sell_status = 'canceled', Sell_order_id = null, Sell_fee = null 
        WHERE Sell_order_id = %s"""
        try:
            self.lock.acquire(True)
            self.cursor.execute(q, (sell_order_id,))
        except Exception as e:
            print(e)
        finally:
            self.lock.release()

    def upd_canceled_buy_order(self, sell_order_id):
        q = f"""UPDATE orders SET Buy_status = 'canceled' WHERE Sell_order_id = %s"""
        try:
            self.lock.acquire(True)
            self.cursor.execute(q, (sell_order_id,))
        except Exception as e:
            print(e)
        finally:
            self.lock.release()

    def live_sell_order_counter(self, strategy):
        q = f"""SELECT count(*) FROM orders WHERE Sell_status = 'live' AND Strategy = %s"""
        try:
            self.lock.acquire(True)
            self.cursor.execute(q, (strategy,))
            answer = self.cursor.fetchall()
            return answer
        except Exception as e:
            print(e)
        finally:
            self.lock.release()

    def get_all_settings(self):
        q = f"""SELECT id, Strategy, Description FROM settings"""
        settings = {}
        try:
            self.lock.acquire(True)
            self.cursor.execute(q)
            answer = self.cursor.fetchall()
            for row in answer:
                settings.update({row['id']: row})
            return settings
        except Exception as e:
            print(e)
        finally:
            self.lock.release()

    def get_settings(self, strategy_name):
        q = f"""SELECT * FROM settings WHERE Strategy = %s"""
        try:
            self.lock.acquire(True)
            self.cursor.execute(q, (strategy_name,))
            answer = self.cursor.fetchone()
            return answer
        except Exception as e:
            print(e)
        finally:
            self.lock.release()
