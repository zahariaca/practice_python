from lxml import html
import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event
import json
import os

with open("./properties/properties.json") as f:
    properties = json.load(f)

output_file = f'./data/content-{properties["year"]}.html'

if not os.path.exists(output_file) or os.path.getsize(output_file) > 0:
    r = requests.get(f'{properties["url"]}{properties["year"]}-dates/')
    with open(output_file, 'w', encoding="utf-8") as f:
        f.write(BeautifulSoup(r.content, 'html.parser').prettify())

# cookies issue workaround, too many requests makes the website not accept others
# html page can be copied from browser to this filelq
with open(f'./data/content-{properties["year"]}.html', 'rb') as f:
    soup = BeautifulSoup(f, 'html.parser')

tbody = soup.find_all("table", class_="publicholidays")[0].find_all("tbody")[0]
even = tbody.find_all("tr", class_="even")
odd = tbody.find_all("tr", class_="odd")

dates = []
for tr in even + odd:
    tds = tr.find_all("td")
    tree = html.fromstring(str(tds[2]))

    date = str(tds[0].text).lstrip().rstrip().strip("\n")
    event_name = str(tree.xpath("//td/*[1]")[0].text).lstrip().rstrip().strip("\n")
    print(f'Date:{date}, Event:{event_name}')

    string_day = date.split(" ")[0]
    string_month = date.split(" ")[1]
    month = properties["months"][f'{string_month}']

    dates.append([f'{string_day if int(string_day) >= 10 else "0%s" % string_day}',
                  f'{month if int(month) >= 10 else "0%s" % month}',
                  f'Government Holiday: "{event_name}"'])

print(dates)
with open('./data/dates.txt', 'wb') as f:
    for date in dates:
        f.write(str(date).encode("UTF-8"))


c = Calendar()

for el in dates:
    e = Event()
    e.name = f'{el[2]}'
    e.begin = f'{properties["year"]}{el[1]}{el[0]} 00:00:00'
    e.make_all_day()
    c.events.add(e)

with open(f'./data/zilelibere-{properties["year"]}.ics', 'w', encoding="utf-8") as f:
    f.writelines(c)
