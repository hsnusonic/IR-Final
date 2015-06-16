import requests
import re
from collections import namedtuple
import time, random
import sys, getopt

from bs4 import BeautifulSoup

def nameorder(name):
  """
  change name order
  ex: Tang, Jie -> Jie Tang
  """
  names = name.split(", ")[::-1]
  return " ".join(names)

def find_author(soup):
  meta_author = soup.find("meta", {"name": "citation_authors"})
  authors = meta_author.attrs["content"].split("; ")
  return [nameorder(author) for author in authors]

def find_title(soup):
  return soup.find("strong").contents[0]

def str_between(s, first, last):
  start = s.index(first) + len(first)
  end = s.index(last, start)
  return s[start:end]

def find_abstract(s):
  abstract = str_between(s, "ABSTRACT", "AUTHORS")
  abstract = str_between(abstract, "<p>", "</p>")
  return abstract

def find_references(s):
  ref_block = str_between(s, "REFERENCES", "CITED BY")
  pattern = re.compile(ur'citation\.cfm\?id=(\d*?)&')
  refs = re.findall(pattern, ref_block)
  return refs

def find_citeby(s):
  cite_block = str_between(s, "CITED BY", "INDEX TERMS")
  pattern = re.compile(ur'citation\.cfm\?id=(\d*?)&')
  cites = re.findall(pattern, cite_block)
  return cites

def get_data(_id):
  param = {"preflayout":"flat", "id":_id}
  res = requests.get("http://dl.acm.org/citation.cfm", params = param)
  soup = BeautifulSoup(res.text, "html.parser")
  title = find_title(soup)
  authors = find_author(soup)
  abstract_str = find_abstract(res.text)
  refs = find_references(res.text)
  cites = find_citeby(res.text)
  return _id, title, authors, abstract_str, refs, cites

def update_set(paper, id_set):
  for ref in paper.refs:
    id_set.add(ref)
  for cite in paper.cites:
    id_set.add(cite)
  return None

def format_paper(paper):
  inform = ""
  inform += "<id>{}</id>".format(paper.id) + '\n'
  inform += "<title>{}</title>".format(paper.title.encode('utf-8')) + '\n'
  for author in paper.authors:
    inform += "<author>{}</author>".format(author.encode('utf-8')) + '\n'
  inform += "<abstract>{}</abstract>".format(paper.abstract) + '\n'
  for ref in paper.refs:
    inform += "<ref>{}</ref>".format(ref) + '\n'
  for cite in paper.cites:
    inform += "<citeby>{}</citeby>".format(cite) + '\n'
  return inform

def get_ids(url, begin, end, filename):
  res = requests.get(url)
  ids_block = str_between(res.text, begin, end)
  pattern = re.compile(ur'citation\.cfm\?id=(\d*?)&')
  ids = re.findall(pattern, ids_block)
  with open(filename, 'w') as f:
    f.write('\n'.join(ids))
  return ids

if __name__ == "__main__":
  # figure input option
  try:
    opts, args = getopt.getopt(sys.argv[1:], "i:o:")
  except getopt.GetoptError as err:
    print str(err)
    sys.exit(2)

  for opt, arg in opts:
    if opt == "-i":
      InputFile = arg
    elif opt == "-o":
      OutputFile = arg

  with open(InputFile, 'r') as f:
    ids = [_id.strip() for _id in list(f)]

  # data structure to store paper information
  Paper = namedtuple("Paper", ['id', 'title', 'authors', 'abstract', 'refs', 'cites'])

  id_set = set(ids)
  fails = []
  papers = []
  for _id in ids:
    try:
      paper = Paper._make(get_data(_id))
      papers.append(format_paper(paper))
      update_set(paper, id_set)
    except:
      fails.append(_id)
      time.sleep(0.5 + random.random())

  # deeper to next layer
  origin_set = set(ids)
  final_set = id_set - origin_set
  for _id in final_set:
    try:
      paper = Paper._make(get_data(_id))
      papers.append(format_paper(paper))
    except:
      fails.append(_id)
      time.sleep(0.5 + random.random())

  with open(OutputFile, 'w') as f:
    f.write(str(len(papers))+'\n')
    for paper in papers:
      f.write(paper)

  if len(fails) != 0:
    FailFile = OutputFile.split('.')[0] + "_fail"
    with open(FailFile, 'w') as f:
      for _id in fails:
        f.write(str(_id) + '\n')
