from lxml import html
import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event
import json

with open("./properties/months.json") as f:
    months_dict = json.load(f)

# with open('./data/content.html', 'r') as f:
#     if not f:
        # r = requests.get('https://publicholidays.ro/ro/2019-dates/')
        # with open('./content.html', 'w') as f:
        #     f.write(r.content)

# cookies issue workaround, too many requests makes the website not accept others
# html page can be copied from browser to this file
with open('./data/html.xml', 'rb') as f:
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
    month = months_dict[f'{string_month}']

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
    e.begin = f'2019{el[1]}{el[0]} 00:00:00'
    e.make_all_day()
    c.events.add(e)

c.events

with open('./data/zilelibere.ics', 'w', encoding="utf-8") as f:
    f.writelines(c)
