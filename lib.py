import pandas as pd
import numpy as np

import seaborn as sns
import matplotlib.pyplot as plt
import datetime as dt

# Constants
this_year = str(dt.datetime.today().year)
last_year = str(dt.datetime.today().year - 1)
this_month = ('0'+str(dt.datetime.today().month)) if (dt.datetime.today().month) < 10 else str(dt.datetime.today().month)
last_month = ('0'+str(dt.datetime.today().month-1)) if (dt.datetime.today().month-1) < 10 else str(dt.datetime.today().month-1)

def year(x):
    return str(x)[6:]

def month(x):
    return str(x)[3:5]

def day(x):
    return str(x)[0:2]

def calc_balance(tra):
    balance = [tra['Balance'][0]]
    tra = tra.drop(['Balance'], axis=1)
    for i in range(1, tra.shape[0]):
        balance.append(float(balance[i - 1]) + float(tra['Transaction'][i]))
    tra['Balance'] = pd.DataFrame(balance)
    return tra

def most_recent(tra):
    n = tra.shape[0] - 1
    if (float(tra['Transaction'][n]) < 0):
        print('Last transaction on', tra['Date'][n])
        print('Withdraw', -float(tra['Transaction'][n]), 'for', tra['Source'][n], 'for', tra['Item'][n])
    else:
        print('Last transaction on', tra['Date'][n])
        print('Deposit', tra['Transaction'][n], 'from', tra['Source'][n], 'for', tra['Item'][n])
    print('-')
    print('Current balance: $%.2f' % tra['Balance'][n])

def add_tra(tra, date, source, item, trans):
    n = tra.shape[0] - 1
    new = pd.DataFrame({'Date' : date, 'Source' : source, 'Item' : item, 'Transaction' : str(trans)}, index=[n + 1])
    new['Balance'] = tra['Balance'][n] + float(new['Transaction'])
    tra = pd.concat([tra, new])
    return tra

def graph_trans(df, year):
    sns.set()
    fig, ax = plt.subplots(figsize=(16,8))

    df.plot(x='Date', y='Balance', ax=ax)
    
    ax.set_title('Transactions in ' + year)
    ax.set_ylabel('Savings ($)');

# Graph from https://chrisalbon.com/python/data_visualization/matplotlib_grouped_bar_plot/
def graph_trend(df, year, n):
    sns.set()
    fig, ax = plt.subplots(figsize=(18,12))

    width = 1 / (n + 1)
    months = list(range(1,13))
    amounts = []
    # Top n categories for transactions throughout the year
    topcat = df['Category'].value_counts()[0:n]

    for m in range(1,13):
        mo = ('0' + str(m)) if m < 10 else str(m)
        tram = df[df['Date'].apply(lambda x : month(x) == mo)]
        sums = []
        for c in topcat.index:
            sums.append(tram[tram['Category'] == c]['Transaction'].sum())
        amounts.append(sums)
    
    for c in range(n):
        plt.bar([m + width * c for m in months], [amounts[x][c] for x in range(0,12)], width)
    
    ax.legend(topcat.index)    
    ax.set_title('Trends in ' + year)
    ax.set_ylabel('Amount ($)');
    ax.set_xlabel('Month');
    ax.set_xticks([m + (n/3) * width for m in months])
    ax.set_xticklabels(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'])
    
def graph_month(tra, m, y):
    tra['Withdrawal'] = tra['Transaction'].map(lambda x : abs(float(x)) if float(x) < 0 else 0)
    tra['Deposit'] = tra['Transaction'].map(lambda x : x if float(x) > 0 else 0)
    mth = tra[tra['Date'].apply(lambda x : year(x) == y and month(x) == m)]
    
    outgo = pd.DataFrame(mth[['Withdrawal', 'Category']].groupby('Category').sum())
    income = pd.DataFrame(mth[['Deposit', 'Category']].groupby('Category').sum())
    stats = pd.concat([outgo, income], axis=1)
    
    actout = stats[stats['Withdrawal'] > 0]
    actin = stats[stats['Deposit'] > 0]
    allout = actout['Withdrawal'].sum()
    allin = actin['Deposit'].sum()
    
    sns.set_palette('muted')
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16,8))
    ax1.pie(actout['Withdrawal'], autopct=lambda x : round(x/100.0 * allout, 2))
    ax2.pie(actin['Deposit'], autopct=lambda x : round(x/100.0 * allin, 2))

    ax1.set_title('Expenses ($%.2f) in %s-%s' % (allout, m, y))
    ax1.legend(labels=actout.index);
    ax2.set_title('Income ($%.2f) in %s-%s' % (allin, m, y))
    ax2.legend(labels=actin.index);
    
# Graph from https://chrisalbon.com/python/data_visualization/matplotlib_grouped_bar_plot/
def graph_budget(df, budget, m, y):
    sns.set()
    fig, ax = plt.subplots(figsize=(18,12))
    
    width = 1 / 3
    idx = list(range(len(budget)))

    mth = df[df['Date'].apply(lambda x : year(x) == y and month(x) == m)]
    mth = mth[mth['Transaction'] < 0]

    outgo = pd.DataFrame(mth[['Transaction', 'Category']].groupby('Category').sum())

    for k in budget.keys():
        if k not in outgo.index:
            outgo.loc[k] = 0

    for i in outgo.index:
        if i not in budget.keys():
            outgo.drop(i, inplace=True)

    # Must be sorted so that the 'actual' bars line up with the corresponding 'budget' bars
    outgo.sort_index(inplace=True)
    
    plt.bar([i for i in idx], [budget[k] for k in budget.keys()], width)
    plt.bar([i + width for i in idx], [-outgo.loc[i,'Transaction'] for i in outgo.index], width)
      
    ax.legend(['Budgeted', 'Spent'])
    ax.set_title('Budget in %s-%s' % (m, y))
    ax.set_ylabel('Amount ($)');
    ax.set_xlabel('Category');
    ax.set_xticks([i + 0.5 * width for i in idx])
    ax.set_xticklabels(budget.keys());