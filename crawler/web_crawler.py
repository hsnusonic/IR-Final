import requests
import time
import re
from bs4 import BeautifulSoup

f = open('SIGIR2014', 'w')

def trade_spider(max_pages):
    page = 1
    while page <= max_pages:
        url = "http://dl.acm.org/citation.cfm?id=2600428&picked=prox&cfid=476019635&cftoken=34988697&preflayout=flat"
        source_code = requests.get(url)
        plain_text = source_code.text
        soup = BeautifulSoup(plain_text)
        count = 0
        num_of_paper = 0 
        for link in soup.find_all('a'):
            href = link.get('href')
            if  href is None or 'citation.cfm?id' not in href:
                continue
            count += 1
            if count < 5:
                continue
            title = '<title>' + link.string + '</title>\n'
            print(count)
            print(title)
            f.write(title.encode('utf8'))
            print(href)
            item_url = "http://dl.acm.org/" + href + "&preflayout=flat"
            findRef(item_url)
            num_of_paper += 1
            if num_of_paper > 4: break
            print('sleep')
            time.sleep(40)
            print('wakeup')
            if count is 88:
                break
        page += 1

def findRef(url):
    source_code = requests.get(url)
    plain_text = source_code.text
    soup = BeautifulSoup(plain_text)

    for table in soup.findAll('div',{'id': 'divmain'}):
        line = str(table)
        soup1 = BeautifulSoup(line)
        for item_name in soup1.findAll('tr'):
            line1 = str(item_name)
            soup2 = BeautifulSoup(line1)
            for link in soup2.findAll('a', {'title':'Author Profile Page'}):
                s = link.string
                s = '<author>' + s + '</author>\n'
                print(s)
                f.write(s.encode('utf8'))
            break
        break

    count = 0
    num_of_ref = 0
    num_of_cit = 0
    for link in soup.find_all('div', {'class':'flatbody'}):
        count += 1
        if count is 1:
            soup1 = BeautifulSoup(str(link))
            for abstrack in soup1.find_all('p'):
                s = '<abstract>' + abstrack.string + '</abstract>\n'
                print(s)
                f.write(s.encode('utf8'))
                break
        if count is 3 or count is 4:
            soup1 = BeautifulSoup(str(link))
            for item_ref in soup1.findAll('tr',{'valign':'top'}):
                soup2 = BeautifulSoup(str(item_ref))
                count1 = 0
                for ref in soup2.findAll('div'):
                    count1 += 1
                    if count1 is 1 and count is 3: 
                        continue
                    if ref.string is None:
                        soup3 = BeautifulSoup(str(ref))
                        for aref in soup3.findAll('a'):
                            s = aref.text
                            break
                        if count is 3:
                            s = s[11:len(s)-1]
                        else:
                            s = s[8:len(s)-1]
                    else:
                        s = ref.text
                        s = s[12:len(s)-20]

                    if count is 3:
                        num_of_ref += 1
                        s = '<ref>' + s + '</ref>\n'
                    else:
                        num_of_cit += 1
                        s = '<citeby>' + s[0:len(s)-7] + '</citeby>\n'
                    print(s)
                    f.write(s.encode('utf8'))
                    break
        if count is 4:
            break
    print(num_of_ref)
    print(num_of_cit)
    f.write(u'\n\n\n\n\n')


trade_spider(1)
