from yahoofinancials import YahooFinancials
import yahoo_fin.stock_info as si
import pandas as pd

'''
- buscar añadir otros indices europeos
- añadir método de elección de empresas basados en ESG scores
- convertir el "earnings_dict" en un dataframe o lista
'''

class StockAnalyzer:
    def __init__(self):
        self.ticker = None
        self.stock_obj = None

    def get_ticker(self, url, name_column, symbol_column):
        df = pd.read_html(url, attrs={'id': 'constituents'})[0]
        empresa_input = input('Empresa: ').title()
        self.ticker = df[df[name_column].str.contains(empresa_input)][symbol_column].iat[0]
        print(f'Ticker: {self.ticker}')
        print('*'*50)
    
    def get_ticker_sp500(self):
        url = 'https://en.m.wikipedia.org/wiki/List_of_S%26P_500_companies'
        self.get_ticker(url, 'Security', 'Symbol')
    
    def get_ticker_dow(self):
        url = 'https://en.m.wikipedia.org/wiki/Dow_Jones_Industrial_Average#Components'
        self.get_ticker(url, 'Company', 'Symbol')
    
    def get_ticker_nasdaq100(self):
        url = 'https://en.m.wikipedia.org/wiki/Nasdaq-100#Components'
        self.get_ticker(url, 'Company', 'Ticker')
    
    def analyze_stock(self):
        self.stock_obj = YahooFinancials(self.ticker)
        price_dict = self.stock_obj.get_stock_price_data()[self.ticker]
        current = price_dict['regularMarketPreviousClose']
        currency = price_dict['currency']
        shares_outstanding = self.stock_obj.get_num_shares_outstanding()
        pe_ratio = self.stock_obj.get_pe_ratio()
        eps_dict = self.stock_obj.get_earnings_per_share()

        projected_gr = si.get_analysts_info(self.ticker)['Growth Estimates'][self.ticker]
        projected_gr = projected_gr.str.rstrip('%').astype(float)
        x = projected_gr[4]

        earnings_dict = {0: round(self.stock_obj.get_earnings_per_share(), 2)}
        for i in range(1, 10):
            earnings_dict[i] = round(earnings_dict[i-1] + (earnings_dict[i-1] * (x / 100)), 2)

        intrinsic_price_dict = {9: earnings_dict[9] * pe_ratio}
        for i in range(8, -1, -1):
            intrinsic_price_dict[i] = intrinsic_price_dict[i+1] / (1 + 0.15)

        current_intrinsic_price = round(intrinsic_price_dict[0], 2)
        buyable_price = round((current_intrinsic_price * 0.8), 2)

        if buyable_price > self.stock_obj.get_daily_high():
            print(f'{self.ticker}: Cheap\nTarget = <${buyable_price}\nCurrent = ${current}.')
        else:
            print(f'{self.ticker}: Expensive\nTarget = <${buyable_price}\nCurrent = ${current}')

# Crear una instancia de la clase y realizar el análisis
analyzer = StockAnalyzer()

while True:
    try:
        opcion = int(input('Elige el índice: \n 1. S&P500 \n 2. Dow Jones \n 3. Nasdaq 100 \n'))
        
        if opcion == 1:
            analyzer.get_ticker_sp500()
            break
        elif opcion == 2:
            analyzer.get_ticker_dow()
            break
        elif opcion == 3:
            analyzer.get_ticker_nasdaq100()
            break
        else:
            print('Elige una opción válida entre 1, 2 y 3')

    except ValueError:
        print('Elige una opción válida entre 1, 2 y 3')
        print('*'*50)

analyzer.analyze_stock()
