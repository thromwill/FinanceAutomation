  
  When I started my first internship at Ameren, I wanted to maintain a spreadsheet that tracks each paycheck and stratifies gross income into different categories so that I would know exactly how much money to put towards expenses, savings, investments, etc. However, manually entering each time I get a paycheck or spend money somewhere is tedious and time consuming, so I am building this tool to automate the process.
  
  This project is currently just getting started. Basic functionality has been implemented, but much more critical functionality and features have yet to be added. The end goal is simple. Any time I receive a check or make a purchase, I can click a button on my phone that will communicate with my home Linux server, run this program, and update the spreadsheet with current financial data. I chose this route mostly to learn how to utilize a home Linux server and communicate outside of the home network, but its also an easier way for me to have the most up to date information than leaving the program to run every 24 hours or a few times a day even when no transactions occur.
<pre>
  At its core, this program should accomplish the following once it is complete:
    - Update Google Sheet with new data
    - Get data from the Google Sheet
    - Scrape my financial institutions' webpages for my personal income/spending data
    - Run in my home Linux environment
    - Be able to be updated easily to align with changes in financial institutions and/or their websites
</pre>
    
  The tools used for this are fairly simple, including Selenium for webscraping,  and Gspread/Google's Sheets API to communicate with the spreadsheet.
  
  ![Google Sheet](worksheet_screenshot.png)
  
  Everything starts with the spreadsheet, which is broken down into four categories: Income, Spending, Investments, and Remainder.
  
      Income - Tracks paychecks, displaying gross income, tax witholdings, net income, and the proportion of net income I've elected to partition into expenses,                      savings, investment accounts, and discretionary spending. Will accomodate for any non-paycheck income in the future.
      
      Spending - Tracks any outward cash flow from my bank account. Total spending is broken down into expenses, investment, and discretionary spending. Each purchase                  is recorded with the date, amount, place, item (websites tend to give merely categorical data i.e. 'Restaurants' from Domino's but not 'Pizza'), type,                  and method.
      
      Investments - Tracks the total amount paid into each position, and the account it was purchased under. This section could evolve into a whole development of its                     own, but in the short term I will simply be adding the current values for each position in the future.
      
      Remainder - Tracks income I've alloted to a particular category that has yet to be spent. Quickly shows exactly how much money is left in my budget for each                       category.
      
  Google Sheet's functions and formulas allow the input to be fairly simple. One challenge, however, was entering and updating data in the right places. To deal with this each line is given an ID in the first column, with the text color set to match the background so that they become invisible. Any time a line needs to be entered or updated, the program looks in the first column for a particular keyword or hashed ID value so it knows where to update or add a new line. 

![Google Sheet ID's](worksheet_ids_screenshot.png)

