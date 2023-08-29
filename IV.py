from yahoofinancials import YahooFinancials
import yahoo_fin.stock_info as si
import pandas as pd


# SP500
def list_wikipedia_sp500() -> pd.DataFrame:
    url = 'https://en.m.wikipedia.org/wiki/List_of_S%26P_500_companies'
    df = pd.read_html(url, attrs={'id': 'constituents'})[0]
    return df

def ticker_sp500():
    tickers_sp500 = list_wikipedia_sp500()
    empresa_input = input('Empresa: ')
    empresa_capitalizada = empresa_input.title()  # Capitalizar la primera letra
    ticker = tickers_sp500[tickers_sp500['Security'].str.contains(empresa_capitalizada)].Symbol
    ticker = ticker.to_string(index=False).strip()
    print(f'Ticker: {ticker}')
    return ticker


# DOW JONES
def list_wikipedia_dowjones() -> pd.DataFrame:
    url = 'https://en.m.wikipedia.org/wiki/Dow_Jones_Industrial_Average#Components'
    df = pd.read_html(url, attrs={'id': 'constituents'})[0]
    return df

def ticker_dow():
    tickers_dow = list_wikipedia_dowjones()
    empresa_input = input('Empresa: ')
    empresa_capitalizada = empresa_input.title()  # Capitalizar la primera letra
    ticker = tickers_dow[tickers_dow['Company'].str.contains(empresa_capitalizada)].Symbol
    ticker = ticker.to_string(index=False).strip()
    print(f'Ticker: {ticker}')
    return ticker


# NASDAQ 100
def list_wikipedia_nas100() -> pd.DataFrame:
    url = 'https://en.m.wikipedia.org/wiki/Nasdaq-100#Components'
    df = pd.read_html(url, attrs={'id': 'constituents'})[0]
    return df

def ticker_nas100():
    tickers_nas100 = list_wikipedia_nas100()
    empresa_input = input('Empresa: ')
    empresa_capitalizada = empresa_input.title()  # Capitalizar la primera letra
    ticker = tickers_nas100[tickers_nas100['Company'].str.contains(empresa_capitalizada)].Ticker
    ticker = ticker.to_string(index=False).strip()
    print(f'Ticker: {ticker}')
    return ticker

while True:
    try:
        opcion = int(input('Elige el índice: \n 1. S&P500 \n 2. Dow Jones \n 3. Nasdaq 100 \n'))
        
        if opcion == 1:
            ticker = ticker_sp500()
            break
        elif opcion == 2:
            ticker = ticker_dow()
            break
        elif opcion == 3:
            ticker = ticker_nas100()
            break
        else:
            print('Elige una opción válida entre 1, 2 y 3')

    except ValueError:
        print('Elige una opción válida entre 1, 2 y 3')
        print('*'*50)

#-----------------------------------------------------------------------------
stock_obj = YahooFinancials(ticker)

# Obtener el precio de una acción y algunos ratios financieros
price_dict = stock_obj.get_stock_price_data()[ticker]
current = price_dict['regularMarketPreviousClose']
currency = price_dict['currency']
shares_outstandings = stock_obj.get_num_shares_outstanding()
PERatio=stock_obj.get_pe_ratio()
EarningPerShare_dict = stock_obj.get_earnings_per_share()


# Obtener el estimado de crecimiento de los proximos 5 años
Projected_GR = si.get_analysts_info(ticker)['Growth Estimates'][ticker]
print(f'Ratio de crecimiento para los próximos 5 años para {ticker} es:\n{Projected_GR}')

print('-'*50)
df= Projected_GR.to_frame(name='GR')
df['GR']= df['GR'].str.rstrip('%').astype(float)

x=df._get_value(4, 'GR')


# Se pronostica el EPS de los proximos 10 años
earnings_dict = {0:round(stock_obj.get_earnings_per_share(),2)}

for i in range(1,10):

    j = i - 1

    earnings_dict[i] = round(earnings_dict[j]+(earnings_dict[j] * (x/100)),2)

print(f'EPS próximos 10 años:\n{earnings_dict}')
print('-'*50)


# Se calcula el precio intrinseco de la acción usando la inducción hacia atras (backward induction) con el ratio P/E
intrinsic_price_dict = {9: earnings_dict[9]*(PERatio)}

for i in range(8,-1,-1):

    j = i + 1

    intrinsic_price_dict[i] = intrinsic_price_dict[j]/(1+0.15)


# Se calcula el precio de compra de la acción con un margen de seguridad del 80%
current_intrinsic_price = round(intrinsic_price_dict[0],2)
buyable_price = round((current_intrinsic_price * 0.8), 2)


# Se compara el precio de compra con el precio actual de la acción
if buyable_price > stock_obj.get_daily_high(): 
    print(f'{ticker}: Cheap\nTarget = <${buyable_price}\nCurrent = ${current}.')

else:
    print(f'{ticker}: Expensive\nTarget = <${buyable_price}\nCurrent = ${current}')