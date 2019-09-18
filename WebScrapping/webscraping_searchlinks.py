from lxml import html
import requests
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
from datetime import datetime
import pandas as pd
import numpy as np
import pdb
from tqdm import tqdm 

scrap_url = "https://www.kickstarter.com/discover/advanced?term=spice+rack&sort=popularity&seed=2606607&page=2"
search = "todos los especieros en kickstarter mostpledged"

scrap_url = "https://www.kickstarter.com/discover/advanced?category_id=7&sort=most_funded&seed=2606748&page=1"
search = "Design mostpledged 10 pages"


def webscrap_links_from_discoverpage(scrap_url, n_scrap_pages):
	"""
	Iterates through all the kickstarter discover pages and save the link of the projects in
	webscrapping_urls.csv for future processing
	"""
	try:
		df_urls = pd.read_csv("Input/webscrapping_urls.csv")
	except Exception as e:
		df_urls = pd.DataFrame()
	scrap_url = scrap_url.replace(re.search(r"&page.*", scrap_url).group(), "") 
	page_cont = 0
	while True:
		scrap_url_page = scrap_url +"&page=" + str(page_cont)
		html_url = urlopen(scrap_url_page)
		print("\n\n scrap_url_page: " + scrap_url_page)
		bsObj = BeautifulSoup(html_url)
		category = bsObj.findAll("span", {"id":re.compile("category_filter")})[0].findAll("span")[0].text 
		project_data = bsObj.findAll("div", {"data-project":re.compile(".*")})    

		if len(project_data) == 0 or page_cont >n_scrap_pages:
			df_urls.to_csv("Input/webscrapping_urls.csv", index = False)
			return df_urls
		for project in project_data:
			project = str(project)
			project = project.replace("&quot;", "\"") 
			next_string_id = False
			for data_string in str(project).split("="):
				if "data-pid" in data_string:
					next_string_id = True
				else:
					if next_string_id:
						url_project = re.search(r'"project":"(.*)"\,"rewards"', project, re.M|re.I).group(1) 
						print(url_project)
						break
			pandas_row = pd.DataFrame({"url":url_project, "category":category, "search":search, "search_url": scrap_url}, index =[0])
			df_urls = df_urls.append(pandas_row)
		page_cont +=1
	df_urls.to_csv("Input/webscrapping_urls.csv", index = False)
	return df_urls

df_urls = webscrap_links_from_discoverpage(scrap_url, 10)