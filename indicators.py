import numpy as np

def moving_average(stock_price, n = 7, weights = []):
    '''
    Calculates the n-day (possibly weighted) moving average for a given stock over time.

    Input:
        stock_price (ndarray): single column with the share prices over time for one stock,
            up to the current day.
        n (int, default 7): period of the moving average (in days).
        weights (list, default []): must be of length n if specified. Indicates the weights
            to use for the weighted average. If empty, return a non-weighted average.

    Output:
        ma (ndarray): the n-day (possibly weighted) moving average of the share price over time.
    '''
    # calculate the total days of the stock
    N = len(stock_price)

    # set up a null numpy array
    ma = np.array([])

    # if weights is empty, calculate a non-weighted average
    if weights == []:
        # use for loop to calculate each day's average
        # only n-th day and later have the average,ignore the firt n-1 days (notice the index starts from 0 )
        for i in range(n-1, N):
            # first, judge if the stock price is nan(i.e. company failed)
            # if not, compute the average
            if not np.isnan(stock_price[i]):
                # calculate n-day moving average. it should starts from i-n+1,...i (total n days)
                ma = np.append(ma, np.average(stock_price[i-n+1:i+1]))

            # if the company failed
            else:
                # do not calculate the average anymore
                break

    # if weights is specified
    else:
        for i in range(n-1, N):
            # first, judge if the stock price is nan(i.e. company failed)
            # if not, compute the average
            if not np.isnan(stock_price[i]):
                # put the weights in method np.average to calculate a weighted average
                ma= np.append(ma, np.average(stock_price[i-n+1:i+1], weights = weights))
            # if the company failed, do not calculate the average anymore
            else:
                break

    return ma



def oscillator(stock_price, n = 7, osc_type = 'stochastic'):
    '''
    Calculates the level of the stochastic or RSI oscillator with a period of n days.

    Input:
        stock_price (ndarray): single column with the share prices over time for one stock,
            up to the current day.
        n (int, default 7): period of the moving average (in days).
        osc_type (str, default 'stochastic'): either 'stochastic' or 'RSI' to choose an oscillator.

    Output:
        osc (ndarray): the oscillator level with period $n$ for the stock over time.
    '''
    # calculate the total days of the stock
    N = len(stock_price)
    # set up a null numpy array
    osc = np.array([])

    # if calculate stochastic oscillator
    if osc_type == 'stochastic':
        # use for loop to calculate each day's stochastic oscillator
        # only n-th day and later have the indicator,ignore the firt n-1 days (notice the index starts from 0 )
        for i in range(n-1, N):

            # first, judge if the stock price is nan(i.e. company failed)
            # if not
            if not np.isnan(stock_price[i]):

                # find the highest and lowest proce during day i to day i-n+1 (n days)
                highest_price = np.max(stock_price[i-n+1:i+1])
                lowest_price = np.min(stock_price[i-n+1:i+1])
                # the difference between today's price and the lowest price
                delta = stock_price[i] - lowest_price
                # the difference between the highest price and the lowest price
                delta_max = highest_price - lowest_price

                # if  the highest price and the lowest price is same: 0/0 situation
                if delta_max == 0:
                    osc = np.append(osc, np.nan)

                else:
                    # oscillator is the ratio delta / delta_max
                    osc = np.append(osc, delta / delta_max)
            # if company failed, do not calculate the indicator anymore
            else:
                break

    # if calculate RSI
    elif osc_type == 'RSI':
        # use for loop to calculate each day's RSI
        # only n-th day and later have the indicator,ignore the firt n-1 days (notice the index starts from 0 )
        for i in range(n-1, N):

            # first, judge if the stock price is nan(i.e. company failed)
            # if not
            if not np.isnan(stock_price[i]):

                # calculate the difference between stock price during day i to day i+n-1
                # difference should be stock_price[i-n+1]-stock_price[i-n]...to stock_price[i-1]-stock_price[i-2]
                differences = np.array([stock_price[(i-n+2)+j]-stock_price[(i-n+1)+j] for j in range(n-1)])
                # find all positve values and negative values in numpy array 'differences'
                positive_diff = differences[differences > 0]
                negative_diff = differences[differences < 0]

                # judge if there are elements in array
                if len(positive_diff) != 0 and len(negative_diff) != 0:
                    # calculate average
                    postive_average = np.average(positive_diff)
                    negative_average = np.average(negative_diff)
                    # RS is the ration of these 2 averages, negative_diff should take absolute value
                    RS = postive_average / np.abs(negative_average)
                    # RSI on this day is 1 - 1/(1+RS)
                    osc = np.append(osc, 1 - 1 / (1 + RS))
                # if there is no elements in positive_diff (decreasing stock prices)
                elif len(positive_diff) == 0 and len(negative_diff) != 0:
                    # RSI is 0
                    osc = np.append(osc, 0)
                # if there is no elements in positive_diff (increasing stock prices)
                elif len(positive_diff) != 0 and len(negative_diff) == 0:
                    # RSI is 1
                    osc = np.append(osc, 1)
                # if there is no elements in both positive_diff and negative_diff
                else:
                    # put nan value
                    osc = np.append(osc, np.nan)


            # if company failed, we do not calculate the indicator anymore
            else:
                break

    return osc
