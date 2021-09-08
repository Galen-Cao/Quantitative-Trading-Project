import numpy as np

def generate_stock_price(days, initial_price, volatility):
    '''
    Generates daily closing share prices for a company,
    for a given number of days.

    Input:
        days (int): a positive integer denotes a period of time
        initial_price (int or float): stock price at initial date
        volatility (float): volatility of a stock, larger than 0

    Output:
        stock_prices (array): an array of stock price in each days
    '''
    # Set stock_prices to be a zero array with length days
    stock_prices = np.zeros(days)
    # Set stock_prices in row 0 to be initial_price
    stock_prices[0] = initial_price
    # Set total_drift to be a zero array with length days
    totalDrift = np.zeros(days)
    # Set up the default_rng from Numpy
    rng = np.random.default_rng()
    # Loop over a range(1, days)
    for day in range(1, days):
        # Get the random normal increment
        inc = rng.normal(0,volatility)
        # Add stock_prices[day-1] to inc to get NewPriceToday
        NewPriceToday = stock_prices[day-1] + inc
        # Get the drift from the news
        d = news(1, volatility)
        # Get the duration
        duration = len(d)
        # Judge if the drift day will be out of range, then add the drift to the next days
        if day + duration > days:
            totalDrift[day:] += d[day+duration-days:]
        else:
            totalDrift[day:day+duration] += d
        # Add today's drift to today's price
        NewPriceToday += totalDrift[day]
        # Set stock_prices[day] to NewPriceToday or to NaN if it's negative
        if NewPriceToday <= 0:
            stock_prices[day] = np.nan
        else:
            stock_prices[day] = NewPriceToday
    return stock_prices


def news(chance, volatility):
    '''
    Simulate the news with %chance

    Input:
        chance (float): the probability of an event happening is chance%
        volatility (float): volatility of a stock, larger than 0
    Output:
        final (array): drift of stock price during the period of an event's influence
    '''
    # Choose whether there's news today
    rng = np.random.default_rng()
    news_today = rng.choice([0,1], p=[1-chance/100,chance/100])
    if news_today:
        # Calculate m and drift
        m = rng.normal(0,2.0)
        drift = m * volatility
        # Randomly choose the duration
        duration = rng.integers(3,15)
        final = drift * np.ones(duration)
        return final
    else:
        return np.zeros(1)

def get_data(method = 'read', initial_price = None, volatility = None):
    '''
    Generates or reads simulation data for one or more stocks over 5 years,
    given their initial share price and volatility.

    Input:
        method (str): either 'generate' or 'read' (default 'read').
            If method is 'generate', use generate_stock_price() to generate
                the data from scratch.
            If method is 'read', use Numpy's loadtxt() to read the data
                from the file stock_data_5y.txt.

        initial_price (list): list of initial prices for each stock (default None)
            If method is 'generate', use these initial prices to generate the data.
            If method is 'read', choose the column in stock_data_5y.txt with the closest
                starting price to each value in the list, and display an appropriate message.

        volatility (list): list of volatilities for each stock (default None).
            If method is 'generate', use these volatilities to generate the data.
            If method is 'read', choose the column in stock_data_5y.txt with the closest
                volatility to each value in the list, and display an appropriate message.

        If no arguments are specified, read price data from the whole file.

    Output:
        sim_data (ndarray): NumPy array with N columns, containing the price data
            for the required N stocks each day over 5 years.
    '''
    # if method is 'generate'

    # if all arguments are specified
    if method == 'generate' and initial_price != None and volatility != None:
        # set days equal to 5 years (1825 days)
        days = 1825
        # the number of companies should equal to the initial price's number
        company_number = len(initial_price)
        # initialize the sim_data
        sim_data = np.zeros([days, company_number])
        # generate simulated data for each company
        for i in range(company_number):
            sim_data[:,i] = generate_stock_price(days, initial_price[i], volatility[i])
        return sim_data
    # if lack some arguments when method is 'generate'
    elif method == 'generate' and initial_price != None and volatility == None:
        print('Please specify the volatility for each stock.')
        return None
    elif method == 'generate' and initial_price == None and volatility != None:
        print('Please specify the initial price for each stock.')
        return None
    elif method == 'generate' and initial_price == None and volatility == None:
        print('Please specify the initial price and volatility for each stock.')
        return None

    # if method is 'read'

    # if set an initial_price
    elif method == 'read' and initial_price != None and volatility == None:
        # first figure out the numbers of columns should return
        N = len(initial_price)
        # read all of the data in the file
        sim_data = np.loadtxt('stock_data_5y.txt')
        # first line of sim_data denotes the volatility of each company
        vol = sim_data[0]
        # second line of sim_data denotes the initial prices of each company
        init_prices = sim_data[1]
        # set a null list to contain the indexs
        indexs = []
        # for each given initial_price, we should find the closest initial prices in the data
        for i in range(N):
            # use method numpy.argmin to find the indexs of the closest initial prices
            indexs.append(np.abs(init_prices - initial_price[i]).argmin())
        # map all indexs to the values in iniial prices and volatilities in the data
        initialprices = np.array([init_prices[i] for i in indexs])
        volatilities = np.array([vol[i] for i in indexs])
        # print what we find the closest initial prices and volatilities in the data
        print(f'Found data with initial prices {initialprices} and volatilities {volatilities}.')
        # return the columns of the data with the closest initial prices
        sim_data = sim_data[1:,indexs]
        return sim_data

    # if set a volatility
    elif method == 'read' and initial_price == None and volatility != None:
        # first figure out the numbers of columns should return
        N = len(volatility)
        # read all of the data in the file
        sim_data = np.loadtxt('stock_data_5y.txt')
        # first line of sim_data denotes the volatility of each company
        vol = sim_data[0]
        # second line of sim_data denotes the initial prices of each company
        init_prices = sim_data[1]
        # set a null list to contain the indexs
        indexs = []
        # for each given volatility, we should find the closest volatilities in the data
        for i in range(N):
            # use method numpy.argmin to find the indexs of the closest initial prices
            indexs.append(np.abs(vol - volatility[i]).argmin())
        # map all indexs to the values in iniial prices and volatilities in the data
        initialprices = np.array([init_prices[i] for i in indexs])
        volatilities = np.array([vol[i] for i in indexs])
        # print what we find the closest initial prices and volatilities in the data
        print(f'Found data with initial prices {initialprices} and volatilities {volatilities}.')
        # return the columns of the data with the closest volatilities
        sim_data = sim_date[1:,indexs]
        return sim_data

    # if both initial_price and volatility are specified
    elif method == 'read' and initial_price != None and volatility != None:
        # here we would ignore volatility
        # first figure out the numbers of columns should return
        N = len(initial_price)
        # read all of the data in the file
        sim_data = np.loadtxt('stock_data_5y.txt')
        # first line of sim_data denotes the volatility of each company
        vol = sim_data[0]
        # second line of sim_data denotes the initial prices of each company
        init_prices = sim_data[1]
        # set a null list to contain the indexs
        indexs = []
        # for each given initial_price, we should find the closest initial prices in the data
        for i in range(N):
            # use method numpy.argmin to find the indexs of the closest initial prices
            indexs.append(np.abs(init_prices - initial_price[i]).argmin())
        # map all indexs to the values in iniial prices and volatilities in the data
        initialprices = np.array([init_prices[i] for i in indexs])
        volatilities = np.array([vol[i] for i in indexs])
        # print what we find the closest initial prices and volatilities in the data
        print(f'Found data with initial prices {initialprices} and volatilities {volatilities}.')
        print('Input argument volatility ignored.')
        # return the columns of the data with the closest initial prices
        sim_data = sim_data[1:,indexs]
        return sim_data

    # if no arguments specified
    elif method == 'read' and initial_price == None and volatility == None:
        # the first line of the file would be the volatility that can skip
        sim_data = np.loadtxt('stock_data_5y.txt',skiprows = 1)
        return sim_data
