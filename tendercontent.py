import requests
from bs4 import BeautifulSoup
import csv

url= r"https://www.irctc.com/active-tender.php"

response = requests.get(url)
html_page = response.text

soup = BeautifulSoup(html_page, 'html.parser')
#find <table>
tables = soup.find_all("table")
print(f"Total {len(tables)} Table(s)Found on page {url}")

for index, table in enumerate(tables):
    print(f"\n-----------------------Table{index+1}-----------------------------------------\n")
    
    #find <tr>
    table_rows = table.find_all("tr")

    #open csv file in write mode
    with open(f"Table{index+1}.csv", "w", newline="") as file:

        #initialize csv writer object
        writer = csv.writer(file)

        for row in table_rows:
            row_data= []

            #<th> data
            if row.find_all("th"):
                table_headings = row.find_all("th")
                for th in table_headings:
                    row_data.append(th.text.strip())
            #<td> data
            else:
                table_data = row.find_all("td")
                for td in table_data:
                    row_data.append(td.text.strip())
            #write data in csv file
            writer.writerow(row_data)

            print(",".join(row_data))
    print("--------------------------------------------------------\n")