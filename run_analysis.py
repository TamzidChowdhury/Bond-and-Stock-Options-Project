'''
@project       : Queens College CSCI 365/765 Computational Finance
@Instructor    : Dr. Alex Pang
@Date          : June 2021

@Student Name  : Mohammed Chowdhury, Kyle Coleman, Tamzid Chowdhury

@Date          : Nov 2021

'''

import pandas as pd
import datetime

from yahoofinancials import YahooFinancials
from stock import Stock
from DCF_model import DiscountedCashFlowModel
from utils import MyYahooFinancials

from TA import SimpleMovingAverages
from TA import ExponentialMovingAverages
from TA import RSI
import yfinance as yf



def run():
    ''' 
    Read in the input file. 
    Call the DCF to compute its DCF value and add the following columns to the output file.
    You are welcome to add additional valuation metrics as you see fit

    Symbol
    EPS Next 5Y in percent
    DCF Value
    Current Price
    Sector
    Market Cap
    Beta
    Total Assets
    Total Debt
    Free Cash Flow
    P/E Ratio
    Price to Sale Ratio
    RSI
    10 day EMA
    20 day SMA
    50 day SMA
    200 day SMA

    '''
    input_fname = "StockUniverse.csv"
    output_fname = "StockUniverseOutput.csv"


    as_of_date = datetime.date(2021, 12, 1)
    df = pd.read_csv(input_fname)
    # TODO
    results = []
    for index, row in df.iterrows():
        symbol = row['Symbol'] # Remove
        print(f"Running analysis on {symbol}, please wait...") #
        stock = Stock(symbol, 'annual')
        stock.get_daily_hist_price(datetime.date(2020, 1, 1), as_of_date)
        model = DiscountedCashFlowModel(stock, as_of_date)

        short_term_growth_rate = float(row['EPS Next 5Y in percent'])/100
        medium_term_growth_rate = short_term_growth_rate/2
        long_term_growth_rate = 0.04

        model.set_FCC_growth_rate(short_term_growth_rate, medium_term_growth_rate, long_term_growth_rate)
        
        fair_value = model.calc_fair_value()
        print("DCF",fair_value)
        listOfPriceDicts = stock.ohlcv_df.loc['prices'].values[0]
        rsi_indicator = RSI(stock.ohlcv_df)
        rsi_indicator.run()
        emaPeriods = [10]
        smaPeriods = [20,50,200]
        ema_indicator = ExponentialMovingAverages(stock.ohlcv_df, emaPeriods)
        ema_indicator.run()
        ema10 = ema_indicator.get_series(10)
        sma_indicator = SimpleMovingAverages(stock.ohlcv_df, smaPeriods)
        sma_indicator.run()
        sma20 = sma_indicator.get_series(20)
        sma50 = sma_indicator.get_series(50)
        sma200 = sma_indicator.get_series(200)
        rsi14 = rsi_indicator.get_series()
        ema10results = []
        sma20results = []
        sma50results = []
        sma200results = []
        rsi14results = []
        for i in range(len(ema10)-5, len(ema10)):
            ema10results.append(ema10.tail(5)[i])

        for i in range(len(sma20)-5, len(sma20)):
            sma20results.append(sma20.tail(5)[i])
        
        for i in range(len(sma50)-5, len(sma50)):
            sma50results.append(sma50.tail(5)[i])
        
        for i in range(len(sma200)-5, len(sma200)):         
            sma200results.append(sma200.tail(5)[i])

        for i in range(len(rsi14)-5,len(rsi14)):
            rsi14results.append(rsi14.tail(5)[i])
            
        
        yfinance = MyYahooFinancials(symbol)

        def get_marketcap():
            return yfinance.get_market_cap()

        def get_revenue():
            return yfinance.get_total_revenue()

        def get_PE_ratio():
            return yfinance.get_pe_ratio()

        def get_PS_ratio():
            return (get_marketcap() / get_revenue())

        def get_sector():
            stock = yf.Ticker(symbol)
            return stock.info['sector']
        
        yfinance = MyYahooFinancials(symbol,'annual')

        #print(fair_value)
        print(f"Finishing analysis on {symbol}, please wait...")
        stockStats = [symbol, row['EPS Next 5Y in percent'], fair_value, listOfPriceDicts[len(listOfPriceDicts)- 1]['close'], get_sector(), get_marketcap(), stock.get_beta(), stock.get_cash_and_cash_equivalent(), stock.get_total_debt(), stock.get_free_cashflow(), get_PE_ratio(), get_PS_ratio(), rsi14results, ema10results, sma20results, sma50results, sma200results]
        results.append(stockStats)
        # pull additional fields
        # ...
    #print(results)
    ndf = pd.DataFrame(columns=("Symbol","EPS Next 5Y in percent","DCF value","Current Price","Sector","Market Cap","Beta","Total Assets","Total Debt","Free Cash Flow","P/E Ratio","P/S Ratio","RSI","10 day EMA","20 day SMA","50 day SMA","200 day SMA"))
    for i in range(0,len(results)):
        ndf.loc[i] = results[i]
    odf = ndf.to_csv(output_fname, index=False)
    print("*********************************************")
    print("***ANALYSIS COMPLETED FOR ALL STOCKS***")
    print("*********************************************")
    print(f"All DCF data has been outputted to  {output_fname}.")
    print("NOTE : The technical indicator columns will only show last 5 days")
    # save the output into a StockUniverseOutput.csv file
    
    # ....
    
    # end TODO

    
if __name__ == "__main__":
    run()
