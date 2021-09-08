# Functions to implement our trading strategy.
import numpy as np
import trading.process as proc
import trading.indicators as indi

def random(stock_prices, period=7, amount=5000, fees=20, ledger='ledger_random.txt'):
    '''
    Randomly decide, every period, which stocks to purchase,
    do nothing, or sell (with equal probability).
    Spend a maximum of amount on every purchase.

    Input:
        stock_prices (ndarray): the stock price data
        period (int, default 7): how often we buy/sell (days)
        amount (float, default 5000): how much we spend on each purchase
            (must cover fees)
        fees (float, default 20): transaction fees
        ledger (str): path to the ledger file

    Output: None
    '''
    # initialize random number generator
    rng = np.random.default_rng()

    # create an initial portfolio

    # here, if the input 'stock_prices' is a single column
    # it will not have numpy.shape[1], since it only has 1 dimension
    # judge if the input is  a single column
    if len(stock_prices.shape) == 1:
        # change the single column into a 2-d array
        # transpose the metrix to make the numpy.shape[0] denotes day
        # numpy.shape[1] denotes stock number
        stock_prices = np.array([stock_prices]).T

    # N denotes the number of stocks
    N = stock_prices.shape[1]
    # create the list containing the money we allocate to the initial purchase for each stock
    available_amounts = [amount] * N
    # use function 'buy' update portfolio and log transactions for each stock
    portfolio = proc.create_portfolio(available_amounts, stock_prices, fees, ledger)

    # days denotes the total days of the trading
    days = stock_prices.shape[0]

    # after initializing the portfolio on day 0, every period will trade
    for trade_day in range(period, days, period):
        # we will decide to trade each of the stock
        for stock_number in range(N):
            # we decide buy or do nothing or sell randomly
            decision = rng.choice([-1,0,1])

            # 1 represents buy
            if decision == 1:
                # judge if the company's stock failed. if not, buy the stock.
                if not np.isnan(stock_prices[trade_day][stock_number]):
                    proc.buy(trade_day, stock_number, amount, stock_prices, fees, portfolio, ledger)
                # if the company failed(stock price is nan), we should not buy
                else:
                    continue

            # 0 represents do nothing
            elif decision == 0:
                continue

            # -1 represents sell
            else:
                # judge if the company's stock failed. If not, we can sell the stock.
                # also we should judge if we hold the stock. If not, we sell nothing
                if not np.isnan(stock_prices[trade_day][stock_number]) and portfolio[stock_number] != 0:
                    proc.sell(trade_day, stock_number, stock_prices, fees, portfolio, ledger)
                # if the company failed or we do not hold the shares of the stock, do nothing
                else:
                    continue

    # the last day is days-1, and we will sell all remaining stock
    for stock_number in range(N):
        # judge if the company's stock failed. if not, we can sell the stocks
        # and if we hold the stock. if not, we do not need to sell
        if not np.isnan(stock_prices[days-1][stock_number]) and portfolio[stock_number] != 0:
            proc.sell(days-1,stock_number, stock_prices, fees, portfolio, ledger)
        # if the company failed, we cannot sell the stock
        else:
            continue

    return None


def crossing_averages(stock_prices, m=50, n=200, amount=5000, fees=20, ledger='ledger_crossing.txt'):
    '''
    use 2 different moving averages over time to decide which stocks to purchase,
    if fast moving average crosses the slow moving average from below, buy the stock.
    if fast moving average crosses the slow moving average from above, sell the stock.
    Spend a maximum of amount on every purchase.

    Input:
        stock_prices (ndarray): the stock price data
        m (int, default 50): the fast period we use to compute the moving average
        n (int, default 200): the slow period we use to compute the moving average
        amount (float, default 5000): how much we spend on each purchase (must cover fees)
        fees (float, default 20): transaction fees
        ledger (str): path to the ledger file

    Output: None
    '''
    # create an initial portfolio

    # here, if the input 'stock_prices' is a single column
    # it will not have numpy.shape[1], since it only has 1 dimension
    # judge if the input is  a single column
    if len(stock_prices.shape) == 1:
        # change the single column into a 2-d array
        # transpose the metrix to make the numpy.shape[0] denotes day
        # numpy.shape[1] denotes stock number
        stock_prices = np.array([stock_prices]).T

    # N denotes the number of stocks
    N = stock_prices.shape[1]
    # create the list containing the money we allocate to the initial purchase for each stock
    available_amounts = [amount] * N
    # use function 'buy' update portfolio and log transactions for each stock
    portfolio = proc.create_portfolio(available_amounts, stock_prices, fees, ledger)

    # days denotes the total days of the trading
    days = stock_prices.shape[0]

    # set up null lists to store each stock's moving average
    SMA , FMA = [] , []
    # calculate each stock's slow and fast moving average and store in the list
    for stock_number in range(N):
        SMA.append(indi.moving_average(stock_prices[:,stock_number], n = n))
        FMA.append(indi.moving_average(stock_prices[:,stock_number], n = m))

    # after obtaining each stock's SMA and FMA, find the crossing point over time
    # only the n-th day and later, have both SMA and FMA
    for trade_day in range(n+1, days):
        # find the cross point for each stock
        for stock_number in range(N):

            #if the company failed at some day, the lenth of FMA and SMA will be shorter.
            # i.e. SMA (same as FMA) may not have the index to 'trade_day'
            # we must keep the index 'trade_day - n' we use in SMA[] in the range
            if trade_day - n > len(SMA[stock_number]) - 1:
                # it denotes the company has faied at this day, skip this stock and never trade it
                continue

            # the company does not fail, we use the strategy to decide trading
            else:
                # judge if FMA crosses SMA from below, buy
                # notice that FMA's first element(index 0) is on m-th day; SMA's first element is on n-th day
                if FMA[stock_number][trade_day-m] >= SMA[stock_number][trade_day-n] and FMA[stock_number][trade_day-m-1] < SMA[stock_number][trade_day-1-n]:
                    proc.buy(trade_day, stock_number, amount, stock_prices, fees, portfolio, ledger)

                # judge if FMA crosses SMA from above, sell
                elif FMA[stock_number][trade_day-m] <= SMA[stock_number][trade_day-n] and FMA[stock_number][trade_day-m-1] > SMA[stock_number][trade_day-1-n]:
                    # judge if we hold the stock
                    if portfolio[stock_number] != 0:
                        proc.sell(trade_day, stock_number, stock_prices, fees, portfolio, ledger)
                    # if not, do nothing
                    else:
                        continue

    # the last day is days-1, and we will sell all remaining stock
    for stock_number in range(N):
        # judge if the company's stock failed. if not, we can sell the stocks
        # and if we hold the stock. if not, we do not need to sell
        if not np.isnan(stock_prices[days-1][stock_number]) and portfolio[stock_number] != 0:
            proc.sell(days-1,stock_number, stock_prices, fees, portfolio, ledger)
        # if the company failed, we cannot sell the stock
        else:
            continue

    return None


def momentum(stock_prices, osc_type='stochastic', n=7,T_over=0.8, T_under=0.2, amount=5000, fees=20, cool_off_period = 10, ledger='ledger_momentum.txt'):
    '''
    use oscillators over time to decide which stocks to purchase,
    when oscillator is above a threshold of 0.7 to 0.8, the stock is considered overvalued, sell it.
    when oscillator is below a threshold of 0.2 to 0.3, the stock is considered undervalued, buy it.
    Spend a maximum of amount on every purchase.

    Input:
        stock_prices (ndarray): the stock price data
        osc_type (str, default 'stochastic'): either 'stochastic' or 'RSI' to choose an oscillator.
        n (int, default 7): period of the moving average (in days).
        T_over (float, default 0.8): a threshold set usually betwween 0.7 and 0.8
        T_under (float, default 0.2): a threshold set usually betwween 0.2 and 0.3
            (must keep T_over + T_under = 1)
        amount (float, default 5000): how much we spend on each purchase (must cover fees)
        fees (float, default 20): transaction fees
        cool_off_period (int, default 10): the cool off periods between each transaction
        ledger (str): path to the ledger file

    Output: None
    '''
    # create an initial portfolio

    # here, if the input 'stock_prices' is a single column
    # it will not have numpy.shape[1], since it only has 1 dimension
    # judge if the input is  a single column
    if len(stock_prices.shape) == 1:
        # change the single column into a 2-d array
        # transpose the metrix to make the numpy.shape[0] denotes day
        # numpy.shape[1] denotes stock number
        stock_prices = np.array([stock_prices]).T

    # N denotes the number of stocks
    N = stock_prices.shape[1]
    # create the list containing the money we allocate to the initial purchase for each stock
    available_amounts = [amount] * N
    # use function 'buy' update portfolio and log transactions for each stock
    portfolio = proc.create_portfolio(available_amounts, stock_prices, fees, ledger)

    # days denotes the total days of the trading
    days = stock_prices.shape[0]

    # set a null list to contain each stock's oscillator
    osc = []

    # calculate each stock's oscillator and store in the list
    # set periods for  function 'moving_average'
    period_ave = 3
    for stock_number in range(N):
        # we use stochastic oscillator (default) and period is 7 days
        stock_osc = indi.oscillator(stock_prices[:,stock_number], n = n, osc_type = osc_type)
        # to better indicate and reduce fluctuation, use moving_average to smooth
        osc.append(indi.moving_average(stock_osc, n = period_ave))

    # we set each stock's cool off period, default is 10 days.
    cool_off = [cool_off_period] * N

    # notice that only (n+period_ave-1)-th day and later have the averaged oscillators
    # so set the start day of oscillator is k
    k = n + period_ave -2
    for trade_day in range(k, days):

        # if each stock's cool_off day change from 10 to 0, this period should not trade but the day accumulates
        for stock_number in range(N):

            # if cool_off[stock_number]<cool_off_period, it denotes the stock trade in the cool_off preriods
            if cool_off[stock_number] < cool_off_period:
                # the day should accumulates, until 10 it can trade again
                cool_off[stock_number] += 1

        # loop over each stock
        for stock_number in range(N):

            # first consider: if the company failed at some day, the lenth of osc is shorter
            # i.e. osc[trade_day] may not have the value if the company failed
            # we must keep the index 'trade_day - k' we use in osc[] in the range
            if trade_day - k > len(osc[stock_number]) - 1:
                # it denotes the company has faied at this day, skip this stock and never trade it
                continue

            # there is no company faied in this period
            else:
                # if the stock's oscillator is above T_over, and we hold the stock, sell it
                # notice we sell all shares of a stock at one time, so we do not need to consider cool_off when selling
                if osc[stock_number][trade_day-k] > T_over and portfolio[stock_number] != 0:
                    proc.sell(trade_day, stock_number, stock_prices, fees, portfolio, ledger)

                # if the stock's oscillator is below T_under,and does not in the cool off period (cool_off == 10), buy it
                elif osc[stock_number][trade_day-k] < T_under and cool_off[stock_number] == cool_off_period:
                    proc.buy(trade_day, stock_number, amount, stock_prices, fees, portfolio, ledger)
                    # after buying, we set cool_off to 0, so until next 20 days, we can buy again
                    cool_off[stock_number] = 0

    # the last day is days-1, and we will sell all remaining stock
    for stock_number in range(N):
        # judge if the company's stock failed. if not, we can sell the stocks
        # and if we hold the stock. if not, we do not need to sell
        if not np.isnan(stock_prices[days-1][stock_number]) and portfolio[stock_number] != 0:
            proc.sell(days-1,stock_number, stock_prices, fees, portfolio, ledger)
        # if the company failed, we cannot sell the stock
        else:
            continue

    return None
