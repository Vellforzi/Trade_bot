class Settings:

    def __init__(self,):
        self.id = None
        self.strategy = None
        self.description = None
        self.total_orders = None
        self.deal_profit = None
        self.instruments = []
        self.time_delay = None
        self.api_key = None
        self.api_secret = None
        self.pass_phrase = None
        self.trade_mode = None
        self.db_host = '***'  # add your host
        self.db_user = '***'  # add user name
        self.db_password = "***"  # add you password
        self.db_name = 'test'

    def update(self, data):
        self.id = data['id']
        self.strategy = data['Strategy']
        self.description = data['Description']
        self.total_orders = data['Total_orders']
        self.deal_profit = data['Deal_profit']
        self.instruments = data['Instruments'].split(',')
        self.time_delay = data['Time_delay']
        self.api_key = data['api_key']
        self.api_secret = data['Api_secret']
        self.pass_phrase = data['Pass_phrase']
        self.trade_mode = data['Trade_mode']

