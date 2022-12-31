# Finance Automation <img align="right" alt="Python" width="30px" style="padding-right:10px;" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-plain.svg" />

After starting my first Co-op at Ameren, I decided to maintain a spreadsheet to track my earnings and stratify gross income into groups like expenses, savings, and investments. I developed this project using Python to automate recording and organizing financial data into meaningful insights.

At its core, the program should accomplish the following:
<pre>
    - Scrape my financial institutions' webpages for my personal income and spending data
    - Organize the data to be meaninfully arranged in a Google Sheet
    - Update a Google Sheet with new data
    - Collect data from the Google Sheet
    - Run in my personal Linux environment
    - Be able to be updated easily to align with changes in financial institutions and/or their websites   
</pre>
It currently uses the following tools in its implementation:
<pre>
    - Python
    - Selenium
    - Undetected Chromdriver
    - GSpread
    - Google Sheets API
</pre>
  
  ![Google Sheet](worksheet_screenshot.png)
  
The spreadsheet is broken down into four categories: Spending, Income, Investments, and Remainder.
  <pre>
Spending - Tracks any outward cash flow from my bank account. Total spending is broken down into expenses, investment, and discretionary spending. Each purchase is recorded with the date, amount, place, item (websites tend to give merely categorical data i.e. 'Restaurants' from Domino's but not 'Pizza'), type, and method.
      
Income - Tracks paychecks, displaying gross income, tax witholdings, net income, and the proportion of net income I've elected to partition into expenses, savings, investment accounts, and discretionary spending.
      
Investments - Tracks the total amount paid into each position, and the account it was purchased under. This section could evolve into a whole development of its own, but in the short term will simply show the amount invested and current value of each position.
      
Remainder - Tracks income I've allocated towards a particular category that has yet to be spent. Quickly shows exactly how much money is left in my budget for each category.
</pre>    
  

