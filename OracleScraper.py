import time

import requests
import pandas as pd
from bs4 import BeautifulSoup

# Define a dictionary to map quarter codes to month strings
quarter_to_month = {
    # "Q1": "jan",
    # "Q2": "apr",
    # "Q3": "jul",
    "Q4": "oct"
}

# Define start and end years for the script to loop through
start_year = 2022
end_year = 2023

# Loop through each year and quarter from the start year to end year
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}
for year in range(start_year, end_year):
    for quarter in quarter_to_month.keys():
        print(f"Processing {quarter} {year}...")
        month = quarter_to_month[quarter]
        url = f"https://www.oracle.com/security-alerts/cpu{month}{year}.html"

        # Make a GET request to the webpage
        time.sleep(3)
        response = requests.get(url, headers=headers)

        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(response.content, "html.parser")

        tables = soup.find_all("table",class_='otable-w2')
        filtered_tables = [table for table in tables if table.find('tr').text.find('CVE')!=-1]

        for table in filtered_tables:
            if year==2018:
                heading = 'h3'
            elif year==2019 and quarter!='Q4':
                heading = 'h3'
            else:
                heading = 'h4'
            title = table.parent.parent.find_previous_sibling(heading).text
            title = title.replace(' ','_').replace('/','_').replace(':','_').replace('(','_').replace(')','_').replace(',','_').replace('__','_')
            columns = []
            if table.find('thead') is None or table.find('tbody') is None:
                continue
            for th in table.find('thead').find_all('th'):
                if not('otable-col-center' in th.get_attribute_list('class') or None in th.get_attribute_list('class')):
                    columns.append(th.text.replace('\n','').replace('-',''))
            columns = columns[:5] + columns[7:] + columns[5:7]
            # removing the unwanted characters from the column names
            for index, col in enumerate(columns):
                # discarding the characters in the column name if it is not an alphabet or number
                columns[index] = ''.join(e for e in col if e.isalnum())
            body = table.find('tbody')
            data = []
            for row in body.find_all('tr'):
                children = row.findChildren()
                # if any of the children is br tag drop it
                for index,child in enumerate(children):
                    if child.name == 'br':
                        children.pop(index)
                if len(children) == len(columns):
                    print(f"Adding data in {title}...")
                    data.append([td.text.replace('\n','').replace('\xa0','') for td in children])
                else:
                    # print(len(children), len(columns))
                    # # print(children, '\n',columns)
                    # for x,y in zip(columns, children):
                    #     print(x,y)
                    # break
                    print(f'Table {title} has no data in it.')
                #print(data)


            df = pd.DataFrame(columns=columns)
            for d in data:
                df.loc[len(df)] = d
            # taking transpose of dataframe preserving the index and columns
            print(quarter, year, title)
            df.columns = columns
            # dropping column Notes
            df = df.drop(['Notes'], axis=1)
            df.columns = [''] * len(df.columns)
            if df.size:
                df.to_csv(f'{quarter}{year}{title}.csv',index=False, header=False)
            # clearing the dataframe
            df = df.iloc[0:0]
