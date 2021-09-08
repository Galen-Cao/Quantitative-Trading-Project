# Evaluate performance.
import numpy as np
import trading.data as data
import trading.strategy as stra
import trading.process as proc
import matplotlib.pyplot as plt

def read_ledger(ledger_file):
    '''
    Reads and reports useful information from ledger_file.

    Input:
        ledger_file (str): path to the ledger file we want to read

    Output:
        each_stock_profit (list): store each stock's earnings
            postive means profit, negative means loss
    '''
    # print a title first
    print('For this strategy: ','\n')

    # read all information in the ledger_file
    # type is str, move away the ','
    all_transactions = np.loadtxt(ledger_file, dtype = 'str', delimiter = ',')

    # output the total number of transactions performed
    total_transaction_number = len(all_transactions)
    print(f'The toal number of transactions over 5 years is: {total_transaction_number}.','\n')

    # output the total amount spent and earned over 5 years
    total_amount_spent = 0
    total_amount_earned = 0
    # loop over all transactions
    for transaction in all_transactions:
        # if the transaction is buy, spent money
        if transaction[0] == 'buy':
            total_amount_spent += float(transaction[5])
        # if the transaction is sell, earn money
        else:
            total_amount_earned += float(transaction[5])
    # output 2 decimals
    print(f'The total amount spent over 5 years is: {round(np.abs(total_amount_spent),2)}.')
    print(f'The total amount earned over 5 years is {round(total_amount_earned,2)}.','\n')

    # output the overall profit or loss(notice the total_amount_spent < 0)
    overall_money = total_amount_earned + total_amount_spent
    # if overall_money larger than 0, make a profit over 5 years
    if overall_money > 0:
        print(f'The overall profit over 5 years is: {round(overall_money,2)}.','\n')
    # if overall_money less than 0, loss money over 5 years
    elif overall_money < 0:
        print(f'The overall loss over 5 years is: {round(np.abs(overall_money),2)}.','\n')
    # if overall_money is 0
    else:
        print(f'No loss or profit over 5 years.','\n')

    # output the portfolio for each stock before the last day
    # set up a dictionary to show each stock's portfolio
    portfolios = {}
    # loop over all transactions
    for transaction in all_transactions:
        # calculate the portfolio before the last day
        # transaction[1] denotes date
        if transaction[1] != '1824':
            # if buy one stock
            # transaction[0] denotes transaction type
            if transaction[0] == 'buy':
                # if the stock key not exist yet,create it and add the current portfolio
                # transaction[2] denotes the stock number
                if 'stock'+ transaction[2] not in portfolios:
                    # transaction[3] denotes the shares of the stock
                    portfolios['stock' + transaction[2]] = int(transaction[3])
                # if the stock key exist, add this transaction
                else:
                    portfolios['stock' + transaction[2]] += int(transaction[3])
            # if sell the stock
            elif transaction[0] == 'sell':
                # clear the stock's portfolio
                portfolios['stock' + transaction[2]] = 0
    print('The state of your portfolio before the last day is shown below.')
    # plot a figure to show the portfolio
    fig1 , ax1 = plt.subplots(1,1,figsize=(7, 4))
    # N denote the number of stocks
    N = len(portfolios.keys())
    x_axis = [i for i in range(N)]
    ax1.bar(x_axis,portfolios.values())
    ax1.set_xlabel('Stock Number')
    ax1.set_ylabel('Number of shares')
    ax1.set_title('Portfolio before last day')
    ax1.set_xticks(range(N))
    # add the y-value on each bar, use zip() to map value in two lists one by one
    for a,b in zip(x_axis,portfolios.values()):
        # only set y-value if not 0
        if b != 0:
            ax1.text(a,b,b,ha='center',va='bottom',fontsize=7)
    plt.show()


    # output if we still hold some stock that cannot sell on the last day 
    for transaction in all_transactions:
        # the last day, sell the stock
        if transaction[1] == '1824' and transaction[0] == 'sell':
            portfolios['stock' + transaction[2]] = 0
    for stock, shares in portfolios.items():
        if shares != 0:
            print(f'The {stock} delisted, so we still hold {shares} shares cannot sell.')
    print('\n')


    # plot the money we profit or loss over time

    print('The money we hold on each day is shown below.')
    # set up a null list to log our money, before start, we have 0.
    money_hold = [0]

    # only use the date, stock number and money cost, i.e.(1,2,5) columns of the file
    # use this method, we can obtain a numpy array with float number
    transaction_data = np.loadtxt(ledger_file, delimiter = ',',usecols = (1,2,5))

    # loop over time (5 years)
    for date in range(1825):
        # first, if the date equals to transaction date, it returns bool value
        # second, we use the bool value find the transaction on this day
        transaction_this_day =  transaction_data[transaction_data[:,0] == date]
        # sum all this day's transaction and the third column value is the money we get or loss
        this_day_money = np.sum(transaction_this_day, axis = 0)[2]
        # add this amount to yesterday's money is the total profit or loss on this day
        # add it into the list
        money_hold.append(money_hold[date] + this_day_money)

    # plot the figure
    fig2 , ax2 = plt.subplots(1,1,figsize=(8,6))
    # x denots date
    x = [i for i in range(1826)]
    # y is the money we hold on each day
    ax2.plot(x, money_hold, 'c-',label = 'the amount of money')
    # set x,y axis label
    ax2.set_xlabel('Date',fontsize = 14)
    ax2.set_ylabel('Money',fontsize = 14)
    # plot a benchmark which is 0 to show if we loss or profit
    y = [0] * len(x)
    ax2.plot(x,y,'r--',label = 'benchmark')
    ax2.set_title('Money holdings each day')
    ax2.legend(loc = 'upper center')
    plt.show()


    # compute each stock's loss or profit and shown in a figure
    print('Each stock\'s return is shown below.' )
    # seu up a list to store each stock's earnings
    each_stock_profit = []
    for stock_number in range(N):
        # find the stock_number's all transaction, and sum the profit(or loss)

        # first, if the stock equals to stock_number, it returns bool value
        # second, we use the bool value find the transaction on this day
        # third, since the third column is profit(or loss), we sum it and add it into the list
        each_stock_profit.append(sum(transaction_data[transaction_data[:,1] == stock_number][:,2]))

    fig3 , ax3 = plt.subplots(1,1,figsize=(8,6))
    x_axis = [i for i in range(N)]
    ax3.bar(x_axis,each_stock_profit)
    ax3.set_xlabel('Stock Number')
    ax3.set_ylabel('Return')
    ax3.set_title('Each stock\'s return')
    ax3.set_xticks(range(N))
    plt.show()

    return each_stock_profit
