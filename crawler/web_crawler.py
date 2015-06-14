import requests
import time
import re
from bs4 import BeautifulSoup

f = open('SIGIR2014', 'w')

papers = 83
papers_list = {}

def addPaper(key,value):
    if  papers_list.has_key(key):
        return True
    else:
        papers_list[key] = value
        return False

def findFlag(flag):
    if  flag is 1 or flag is 35 or flag is 55:
        return True
    else:
        return False

def trade_spider(max_pages):
    page = 1
    while page <= max_pages:
        url = "http://dl.acm.org/citation.cfm?id=2600428&picked=prox&cfid=476019635&cftoken=34988697&preflayout=flat"
        source_code = requests.get(url)
        plain_text = source_code.text
        soup = BeautifulSoup(plain_text)
        count = 0
        num_of_paper = 0 
        for link in soup.find_all('table',{'class':'text12'}):
            count += 1
            if count < 2: continue
            soup1 = BeautifulSoup(str(link))
            flag = 0
            for link1 in soup1.find_all('a'):
                href = link1.get('href')
                if  href is None or 'citation.cfm?id' not in href:
                    continue
                flag += 1
                if findFlag(flag):
                    continue
                p_id = href[16:23].split('&')[0]
                if  addPaper(p_id,href):
                    continue
                s = '<id>' + p_id + '</id>\n'
                f.write(s.encode('utf8'))
                print(flag)
                #print(href)
                item_url = "http://dl.acm.org/" + href + "&preflayout=flat"
                findRef(item_url,0)
                num_of_paper += 1
                if num_of_paper == 2:
                    break
        page += 1

def findRef(url,rec):
    source_code = requests.get(url)
    plain_text = source_code.text
    soup = BeautifulSoup(plain_text)
    title(soup)
    other(soup,rec)


def title(soup):
    for link in soup.find_all('strong'):
        s = '<title>' + link.text + '</title>\n'
        print(s)
        f.write(s)
        break


def other(soup,rec):
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

    papers_name = {}
    num_of_ref = 0
    num_of_cit = 0
    count = 0
    for link in soup.find_all('div', {'class':'flatbody'}):
        count += 1
        if count is 1:
            soup1 = BeautifulSoup(str(link))
            for abstract in soup1.findAll('div',{'style':'display:inline'}):
                s = '<abstract>' + abstract.text + '</abstract>\n'
                print(s)
                f.write(s.encode('utf8'))
                break
        if count is 3 or count is 4:
            soup1 = BeautifulSoup(str(link))
            for item_ref in soup1.findAll('a'):
                count1 = 0
                count1 += 1
                flag = False
                href = item_ref.get('href')
                if  href is None or 'citation.cfm?id' not in href:
                    continue
                p_id = href[16:23].split('&')[0]
                papers_name[str(p_id)] = str(href)
                #print(papers_name[str(p_id)])
                if count is 3:
                    num_of_ref += 1
                    s = '<ref>' + p_id + '</ref>\n'
                else:
                    num_of_cit += 1
                    s = '<citeby>' + p_id + '</citeby>\n'
                #print(s)
                f.write(s.encode('utf8'))
        if count is 4:
            break
    print(num_of_ref)
    print(num_of_cit)

    if  rec > 0:
        for key in papers_name:
            url = 'http://dl.acm.org/' + papers_name[key] + '&preflayout=flat'
            p_id = '<id>' + key + '</id>\n'
            print(p_id)
            if  addPaper(p_id,papers_name[key]):
                continue
            f.write(p_id)
            findRef(url,rec-1)
            time.sleep(40)
        papers_name.clear()

    f.write(u'\n\n\n\n\n')


trade_spider(1)
print(papers_list)

f.close()
