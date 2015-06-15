import requests
import re
from collections import namedtuple
import time, random

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
  abstract = str_between(s, "ABSTRACT", "SOURCE MATERIALS")
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
  return _id[0], title, authors, abstract_str, refs, cites

def format_paper(paper):
  inform = []
  inform.append("<id>{}</id>".format(paper.id))
  inform.append("<title>{}</title>".format(paper.title))
  for author in paper.authors:
    inform.append("<author>{}</author>".format(author))
  inform.append("<abstract>{}</abstract>".format(paper.abstract))
  for ref in paper.refs:
    inform.append("<ref>{}</ref>".format(ref))
  for cite in paper.cites:
    inform.append("<citeby>{}</citeby>".format(cite))
  return '\n'.join(inform)

def get_ids(url):
  res = requests.get(url)
  ids_block = str_between(res.text, "Research session 1: location-based services",\
      "Industry &#38; government invited talks")
  pattern = re.compile(ur'citation\.cfm\?id=(\d*?)&')
  ids = re.findall(pattern, ids_block)
  return ids

if __name__ == "__main__":
  url = "http://dl.acm.org/citation.cfm?id=2623628&preflayout=flat"
  ids = get_ids(url)
  Paper = namedtuple("Paper", ['id', 'title', 'authors', 'abstract', 'refs', 'cites'])
  paper = Paper._make(get_data(ids[0]))
  print format_paper(paper)
