#--------------------------------------------------------------------------------------------------------------------------------------------------------Imports
from __future__ import print_function
from datetime import datetime
from matplotlib.pyplot import get
from re import sub
from decimal import Decimal
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from selenium import webdriver

import time
import hashlib
import re
import undetected_chromedriver as uc
import gspread
import operator
#---------------------------------------------------------------------------------------------------------------------------------------------------------Global

# From Google:

# If modifying these scopes, delete the file token.json.
SCOPES = ['redacted']

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = 'redacted'
RANGE_NAME = 'Sheet1'

#--------------------------------------------------------------------------------------------------------------------------------------------------------Classes

# Class Index
# __init__() : takes keyword, typically an ID number, and the worksheet object
# get() : returns the current row number of a cell in the first column containing the keyword
class Index:

    def __init__(self, keyword, worksheet):
        self.keyword = keyword
        self.worksheet = worksheet

    # Returns current row number
    def get(self):
        return self.worksheet.find(self.keyword, in_column = 1).row

# Class Spending
# __init__() : takes date, amount, place, item, type, and method. All assumed to be strings, amount allowed to be numeric value.
# __str__() : Overrides string method to display fields
# __eq__() : Overrides comparison method to compare by object values excluding id
class Spending:

    def __init__(self, date, amount, place, item, type, method):

        # Gives each object an ID based on it's fields
        self.id = ''
        if(method == 'Discover Card'):
            self.id = generateId(date + place[0:2] + method)
        elif(method == 'Fidelity'):
            self.id = generateId(date + amount + place + item)
            
        self.date = date
        self.amount = amount
        self.place = place
        self.item = item
        self.type = type
        self.method = method

    def __str__(self):
     return self.id + ', ' + self.date + ', ' + str(self.amount) + ', ' + self.place + ', ' + self.item + ', ' + self.type + ', ' + self.method

    # Used to check for updated values
    def __eq__(self, other):
      fetcher = operator.attrgetter("date", "amount", "place", "item", "type", "method")
      try:
          return self is other or fetcher(self) == fetcher(other)
      except AttributeError:
          return False

#------------------------------------------------------------------------------------------------------------------------------------------------------Functions

# Takes any string
# Returns hashed string value
def generateId(string):
    id = hashlib.sha256(string.encode('utf-8')).hexdigest()
    return id

# Takes driver object
# Opens google and waits one second
# Helps maneuver websites' security measures
def reset_browser(driver):
  driver.get('https://google.com')
  time.sleep(1)

# Takes a date, gross amount, index object, and worksheet object
# Inserts stratified income data in new row on the worksheet
# ----------------------------------------------------------
# !!Update needed!! : tax rate is variable
def enter_income(date, gross_amount, income_index, worksheet):

    index = income_index.get()
    data = [
                generateId(date+gross_amount),
                date,
                gross_amount,
                '=0.127*C' + str(index), # Taxes
                '=0.873*C' + str(index), # Net Income
                '=0.17*E' + str(index), # Expenses
                '=0.44*E' + str(index), # Savings
                '=0.34*E' + str(index), # Investments
                '=0.85*H' + str(index), # Retirement
                '=0.15*H' + str(index), # Other
                '=0.05*E' + str(index) # Discretionary
            ]

    worksheet.insert_row(data, index = index, value_input_option = 'USER_ENTERED')

# Takes an updated Spending object and the worksheet object
# Finds proper entry based on object id and updates values
def update_spending(s, worksheet):

    index = str(Index(s.id, worksheet).get())
    data = [s.id, s.date, s.amount, s.place, s.item, s.type, s.method]
    
    for i in range(len(data)):
      worksheet.update_cell(index, i+1, data[i])

# Takes a Spending object and the worksheet object
# Enters spending data in new row, and investment data if the spending object is of type investment
def enter_spending(s, worksheet):

    index = Index('spending_header', worksheet).get() + 1
    data = [s.id, s.date, s.amount, s.place, s.item, s.type, s.method]

    worksheet.insert_row(data, index = index, value_input_option = 'USER_ENTERED')

    if(type == 'Investment'):
        enter_investment(s.item, worksheet)

# Takes a string stock ticker and the worksheet object
# Updates total invested under a particular ticker or adds a new row if needed
def enter_investment(ticker, worksheet):

    index = Index('investment_index').get()
    stocks = worksheet.get('B9:B' + str(index-1))
    stocks = [x for y in stocks for x in y]

    if(ticker not in stocks):
        data = ['_' + str(index), ticker, '=SUMIF(E24:E,B' + str(index) + ',C24:C)', 'Individual']
        worksheet.insert_row(data, index = index, value_input_option = 'USER_ENTERED')


# Takes the worksheet object
# Returns a list of spending transactions from the worksheet
def get_worksheet_spending(worksheet):

    data = worksheet.batch_get(['A' + str(Index('spending_header', worksheet).get()+1) + ':G' + str(Index('spending_index', worksheet).get()-1)])[0]
    
    transactions = []

    for i in data:
        temp = Spending(i[1], re.sub('[$]', '', i[2]), i[3], i[4], i[5], i[6])
        temp.id = i[0]
        transactions.append(temp)

    return transactions

# Takes the webdriver object
# Logs into Discover with provided credentials and scrapes data
# Returns list of five most recent transactions as Spending objects 
def scrape_discover(driver):

    # Credentials
    url = "https://discover.com/"
    username = 'redacted'
    password = 'redacted'

    # Open windows and maximize
    driver.get(url)
    driver.maximize_window()

    # Adding all this time seems long, and it is, but it is necessary to deal with load times
    # and to be treated as a regular user by the website
    time.sleep(5)

    # Login
    driver.find_element_by_xpath("//input[@id='userid-content']").send_keys(username)
    time.sleep(2)
    driver.find_element_by_xpath("//input[@id='password-content']").send_keys(password)
    time.sleep(2)
    driver.find_element_by_xpath("//input[@id='log-in-button' and @class='btn-primary log-in-button right']").click()
    time.sleep(5)

    # Grab the data
    discover_data_raw = driver.find_elements_by_xpath('//*[@id="main-content-rwd"]/div[2]/div[2]/div/div[1]')

    # Start cleaning data
    discover_data_raw_list = [i.text.split('\n') for i in discover_data_raw]
    discover_data_raw_list = discover_data_raw_list[0]

    # Remove elements we do not want
    keywords = ['Recent Activity', 'Sort by','Go to Previous Statement','All Activity & Statements',
                'Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    blacklist = re.compile('|'.join([re.escape(word) for word in keywords]))
    discover_data = [i for i in discover_data_raw_list if not blacklist.search(i)]
    del discover_data[5-1::5]
    
    # Sort into Spending objects and add to list of transactions
    transactions = []

    while(discover_data and len(transactions) < 5):

        temp = Spending(str((datetime.strptime(discover_data[0], '%b %d, %Y')).strftime('%m/%d/%Y')), "{:.2f}".format(float(sub(r'[^\d\-.]', '', discover_data[2]))), discover_data[1], discover_data[3], 'Expenses' if discover_data[3] == 'Gasoline' else 'Discretionary', 'Discover Card')

        transactions.append(temp)
        del discover_data[0:4]

    return transactions

def scrape_fidelity(driver):

    # Credentials
    url = "https://fidelity.com/"
    username = 'redacted'
    password = 'redacted'

    # Open windows and maximize
    driver.get(url)
    driver.maximize_window()
    time.sleep(5)

    # Login
    driver.find_element_by_xpath('//*[@id="userId-input"]').send_keys(username)
    time.sleep(2)
    driver.find_element_by_xpath('//*[@id="password"]').send_keys(password)
    time.sleep(2)
    driver.find_element_by_xpath('//*[@id="fs-login-button"]').click()
    time.sleep(8)
    driver.find_element_by_xpath('//*[@id="tab-4"]').click()
    time.sleep(5)

    # Grab the data
    fidelity_data_raw = driver.find_elements_by_xpath('//*[@id="AccountActivityTabHistory"]/div/div/div/div[4]/div[1]/table')

    # Start cleaning data
    fidelity_data = [i.text.split('\n') for i in fidelity_data_raw]

    del fidelity_data[0:4]
    
    # Sort into Spending objects and add to list of transactions
    transactions = [] # Output list

    # Fidelity displays entries for funds transferred to an account and funds that is actually invested in a particular stock
    # For example, you may transfer $500 into Fidelity but only be able to invest $499.37 into a particular stock,
    # leaving an unnaccounted $0.63 in the spreadsheet
    # On the spreadsheet, funds remaining should reflect the amount transferred, but only actual investments should show up as transactions
    # To resolve this, we only enter actual investments as transactions on the sheet
    # Then, we add one additional transaction using the difference between transferred and invested funds as the value
    money_transferred = 0 
    money_invested = 0
    transfer_date = ''

    while(fidelity_data):

        temp = Spending(fidelity_data[0].split()[0], fidelity_data[1].split(' (Cash) ')[1].replace('-', ''), fidelity_data[0].split(' ', 1)[1], fidelity_data[1][fidelity_data[1].find("(")+1:fidelity_data[1].find(")")], 'Investment', 'Fidelity')

        if(temp.item == 'Cash'):
            money_transferred += Decimal(sub(r'[^\d.]', '', temp.amount))
            transfer_date = temp.date
        else:
            money_invested += Decimal(sub(r'[^\d.]', '', temp.amount))
            transactions.append(temp)

        del fidelity_data[0:2]

    transactions.append(Spending(transfer_date, str(money_transferred - money_invested), 'Fidelity', 'Uninvested', 'Investment', 'Fidelity'))

    return transactions

#-----------------------------------------------------------------------------------------------------------------------------------------------------------Main

def main():

    # Set up google sheets
    credentials = {
            "type": 'redacted',
            "project_id": 'redacted',
            "private_key_id": 'redacted',
            "private_key": 'redacted',
            "client_email": 'redacted',
            "client_id": 'redacted',
            "auth_uri": 'redacted',
            "token_uri": 'redacted',
            "auth_provider_x509_cert_url": 'redacted',
            "client_x509_cert_url": 'redacted'
        }
    gc = gspread.service_account_from_dict(credentials)
    spreadsheet = gc.open_by_key('redacted')
    # Could use sheet by title -> spreadsheet.get_worksheet('Sheet1')
    worksheet = spreadsheet.get_worksheet(0)


    # Setup chromedriver
    options = webdriver.ChromeOptions()
    options.headless = True
    options.add_argument("--incognito")
    driver = uc.Chrome(options=options)


    #-------------------------------------------------------------------Actually do things

    # Scrape pages for data
    # ---------------------
    # Need to add several more pages like Venmo and etc
    worksheet_spending = get_worksheet_spending(worksheet)
    recent_transactions_discover = scrape_discover(driver)
    recent_transactions_fidelity = scrape_fidelity(driver)

    #print('Worksheet: ')
    #for i in worksheet_spending:
    #  print(i)
    #print('Fidelity: ')
    #for i in recent_transactions_fidelity:
    #  print(i)
    #print('Discover: ')
    #for i in reversed(recent_transactions_discover):
    #  print(i)

    # Add recent Fidelity transactions to the worksheet
    for i in recent_transactions_fidelity:
      if(worksheet.find(i.id, in_column = 1) == False):
        enter_spending(i, worksheet)

    # Add recent Discover transactions to the worksheet
    # -------------------------------------------------
    # Discover transactions are typically pending for a few days,
    # gas for example, is usually listed as $1.00 for several days before being updated
    # to the correct amount
    # To account for this, we have to check if a transaction's id is already in the 
    # sheet, and if so simply update the entry instead of adding a new one
    for i in reversed(recent_transactions_discover):
      found = False;
      for j in worksheet_spending:
        if(i.id == j.id):
          found = True
          if(i != j):
            update_spending(i, worksheet)
          break;
      if found == False:
        enter_spending(i, worksheet)
 
#------------------------------------------------------------------------------------------------------------------------------------------------------Main Call
    
if __name__ == '__main__':
    main()
