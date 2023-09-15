import pandas as pd
from yahoofinancials import YahooFinancials
import yfinance as yf
import numpy as np
import yahoo_fin.stock_info as si
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

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
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        self.get_ticker(url, 'Security', 'Symbol')
    
    def get_ticker_dow(self):
        url = 'https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average#Components'
        self.get_ticker(url, 'Company', 'Symbol')
    
    def get_ticker_nasdaq100(self):
        url = 'https://en.wikipedia.org/wiki/Nasdaq-100#Components'
        self.get_ticker(url, 'Company', 'Ticker')
        
    def get_sp500_companies(self):
        df2 = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies', attrs={'id': 'constituents'})[0]
        cols = ['Security', 'Symbol', 'GICS Sector']
        df2 = df2[cols]
        print(df2)
        
    def get_dow_companies(self):
        df3 = pd.read_html('https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average#Components', attrs={'id': 'constituents'})[0]
        cols = ['Company', 'Symbol', 'Industry']
        df3 = df3[cols]
        print(df3)
        
    def get_nasdaq_companies(self):
        df4 = pd.read_html('https://en.wikipedia.org/wiki/Nasdaq-100#Components', attrs={'id': 'constituents'})[0]
        print(df4.iloc[:, :3])     
        
    def get_market_cap(self):
        self.stock_obj = YahooFinancials(self.ticker)
        market_cap = self.stock_obj.get_market_cap()
        print(f'Market cap: ${market_cap} USD')
        return market_cap
    
    def get_eps(self):
        self.stock_obj = YahooFinancials(self.ticker)
        eps = self.stock_obj.get_earnings_per_share()
        print(f'Earning per share: {eps}')
        return eps
        
    def get_price_earnings_ratio(self):
        self.stock_obj = YahooFinancials(self.ticker)
        pe_ratio = self.stock_obj.get_pe_ratio()
        print(f'Price/earning ratio: {pe_ratio}')
        return pe_ratio
    
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

    def analyze_all_sp500(self):
        df_sp500 = self.analyze_all_companies('S&P 500', 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies', 'Symbol', 'GICS Sector')
        return df_sp500

    def analyze_all_dow(self):
        df_dow = self.analyze_all_companies('Dow Jones', 'https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average#Components', 'Symbol', 'Industry')
        return df_dow

    def analyze_all_nasdaq(self):
        df_nasdaq = self.analyze_all_companies('Nasdaq 100', 'https://en.wikipedia.org/wiki/Nasdaq-100#Components', 'Ticker', 'Company')
        return df_nasdaq

    def analyze_all_companies(self, index_name, url, symbol_column, sector_column):
        df = pd.read_html(url, attrs={'id': 'constituents'})[0]
        cols = [sector_column, symbol_column]
        df = df[cols]
        df['Current Price'] = np.nan
        df['Buyable Price'] = np.nan
        df['Status'] = np.nan

        for i, row in df.iterrows():
            ticker = row[symbol_column]
            self.ticker = ticker

            try:
                # Obtener datos de la acción
                stock_data = si.get_quote_table(ticker)
                if 'Previous Close' in stock_data:
                    current_price = float(stock_data['Previous Close'])

                    # Calcula el buyable price directamente
                    buyable_price = round((current_price * 0.8), 2)

                    if buyable_price > current_price:
                        status = 'Cheap'
                    else:
                        status = 'Expensive'
                    df.at[i, 'Current Price'] = current_price
                    df.at[i, 'Buyable Price'] = buyable_price
                    df.at[i, 'Status'] = status
                else:
                    print(f"No se encontraron datos para {ticker}")
            except Exception as e:
                print(f"Error al obtener datos para {ticker}: {e}")
        
        print(f"Análisis de todas las compañías en {index_name} completado.")
        return df


# Crear una instancia de la clase

analyzer = StockAnalyzer()

while True:
    try:
        opcion = int(input('Elige el índice: \n 1. S&P500 \n 2. Dow Jones \n 3. Nasdaq 100 \n '))
        
        if opcion == 1:
            opcion1 = int(input('\n 1. Quiero ver todas las compañias \n 2. Quiero una empresa en concreto \n 3. Quiero analizar todas las compañias\n'))
            if opcion1 == 1:
                analyzer.get_sp500_companies()
            elif opcion1 == 2:
                analyzer.get_ticker_sp500()
            elif opcion1 == 3:
                df_sp500 = analyzer.analyze_all_sp500()
                print(df_sp500)
                break
            else:
                print('Elige una opción válida entre 1, 2 y 3')
                continue
        elif opcion == 2:
            opcion2 = int(input('\n 1. Quiero ver todas las compañias \n 2. Quiero una empresa en concreto \n 3. Quiero analizar todas las compañias\n'))
            if opcion2 == 1:
                analyzer.get_dow_companies()
            elif opcion2 == 2:
                analyzer.get_ticker_dow()
            elif opcion2 == 3:
                df_dow = analyzer.analyze_all_dow()
                print(df_dow)
                break
            else:
                print('Elige una opción válida entre 1, 2 y 3')
                continue
        elif opcion == 3:
            opcion3 = int(input('\n 1. Quiero ver todas las compañias \n 2. Quiero una empresa en concreto \n 3. Quiero analizar todas las compañias\n'))
            if opcion3 == 1:
                analyzer.get_nasdaq_companies()
            elif opcion3 == 2:
                analyzer.get_ticker_nasdaq100()
            elif opcion3 == 3:
                df_nasdaq = analyzer.analyze_all_nasdaq()
                print(df_nasdaq)
                break
            else:
                print('Elige una opción válida entre 1, 2 y 3')
                continue
        else:
            print('Elige una opción válida entre 1, 2 y 3')
            continue

    except ValueError:
        print('Elige una opción válida entre 1, 2 y 3')
        print('*'*50)
