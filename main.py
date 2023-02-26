from manual_run import run as manual_run
from auto_run import run as auto_run
from DB import DBWorker  # BD class
from OKX_trading import Okex  # stock's API class
from Settings import Settings  # settings class


def db_connect(data):  # DB instance
    return DBWorker(db_host=data.db_host, db_user=data.db_user, db_password=data.db_password,
                    db_name=data.db_name)


def api_connect(data, demo=True):  # stock's instance
    return Okex(api_key=data.api_key, api_secret=data.api_secret, pass_phrase=data.pass_phrase, demo=demo)


if __name__ == "__main__":  # bot startup
    print("Creating the DB instance...")
    settings = Settings()
    db = db_connect(settings)
    if not db:
        print("Failed to create the DB class instance.")
        exit(0)
    print("DB instance created.")
    options = db.get_all_settings()  # take info from database like dicts in dict
    print("Available strategies: ")
    for key, option in options.items():
        print(f"ID: {option['id']} Strategy: {option['Strategy']} Description: {option['Description']}")
    while True:
        try:
            q = input("Enter the strategy ID: ")
            res = options.get(int(q))
            if res:
                break
        except ValueError:
            print("Just the strategy ID must be entered.")
    print(res)
    tmp = db.get_settings(res['Strategy'])  # take info from database according to chosen strategy
    settings.update(tmp)  # update settings according to chosen strategy
    print("Creating the OKX stock instance...")
    stock = api_connect(settings)
    if stock:
        print("OKX instance created.")
    while True:
        run = input("Auto or manual mode?(a/m) ")
        if run == 'a':
            auto_run(db, stock, settings)
        elif run == 'm':
            manual_run(db, stock)
        else:
            break
