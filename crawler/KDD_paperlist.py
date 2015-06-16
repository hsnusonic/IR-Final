import KDD_crawler

if __name__ == "__main__":
  url = "http://dl.acm.org/citation.cfm?id=2020408&preflayout=flat"
  ids = KDD_crawler.get_ids(url, "Poster session", "Powered by", "KDD2011_ids_1")
