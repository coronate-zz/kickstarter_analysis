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
from utils import currency_map


def save_infromation(df_monitor, df_pledges, project_name, html_str, pledges_str):
    """ Filesystem for scrpaing pledges and monito ongoingprojects
    """
    #Open old scrapts & Save new information  MONITOR
    try:
        df_monitor_hist = pd.read_csv("DataFrames/kickstarter_monitor_hist.csv", index_col =0)
        df_monitor_hist = df_monitor_hist.append(df_monitor)
        df_monitor_hist.to_csv("DataFrames/kickstarter_monitor_hist.csv")
    except Exception as e:
        pdb.set_trace()
        df_monitor_hist = df_monitor
        df_monitor.to_csv("DataFrames/kickstarter_monitor_hist.csv", index =True)

    #Open old scrapts & Save new information  PLEDGES
    try:
        df_pledges_hist = pd.read_csv("DataFrames/kickstarter_pledges_hist.csv", index_col =0)
        if project_name in df_pledges_hist.project_name.unique():
            print("Project already saved in pledges")
        else:
            df_pledges_hist = df_pledges_hist.append(df_pledges)
            df_pledges_hist.to_csv("DataFrames/kickstarter_pledges_hist.csv", index = True)
            #REPORT FILES
            report_txt =  html_str + pledges_str
            text_file = open("Reports/" + project_name.replace("/", "-") + "_report.txt", "w")
            text_file.write(report_txt)
            text_file.close()
    except Exception as e:
        df_pledges_hist = df_pledges
        pdb.set_trace()
        df_pledges_hist.to_csv("DataFrames/kickstarter_pledges_hist.csv", index =True)


def format_numbers(money):
    currency_found = False
    for currency_val in currency_map.keys():
        if currency_val in money:
            currency_found = currency_val
    if not currency_found:
        for currency_val_2 in currency_map.keys():
            if currency_map[currency_val_2] in money and currency_map[currency_val_2]!="$" :
                currency_found = currency_val_2
    if not currency_found:
        currency_found = "USD"

    money = money.replace(currency_found, "")    
    money = money.replace(currency_map[currency_found], "")
    money = money.replace("\n", "")
    money = money.replace("goal", "")
    money = money.replace("pledged of ", "")
    money = money.replace(" ", "")
    money = money.replace(",", "")
    money = float(money)
    return money, currency_found

def get_projec_name(bsObj):
    try:
        project_name =  bsObj.findAll("div", {"class":re.compile("col col-8 py3")})[0].findAll("h3", {"class":re.compile("normal")})[0].text
    except Exception as e:
        exception_str = "get_projec_name: 1"

    try:
        project_name = bsObj.findAll("a", {"class":re.compile("hero__link")})[0].text
        raise ValueError()
    except Exception as e:
        exception_str = "get_projec_name: 2"

    try:
        project_name =bsObj.findAll("h2", {"class":re.compile(".*project-name")})[0].text
    except Exception as e:
        exception_str = "get_projec_name: 3"

    try:
        bsObj.findAll("h2", {"class":re.compile(".*project-name")})[0].text
    except Exception as e:
        exception_str = "get_projec_name: 4"

    project_name = project_name.replace("\n", "")
    
    return project_name

def get_founded_characteristics(bsObj):
    html_str=""
    try:
        founded_characteristics = bsObj.findAll("div", {"class":re.compile("grid-col-12 grid-col-4-md hide block-lg")})[0]
        total_recolected = founded_characteristics.findAll("span", {"class":re.compile("ksr-green-700")})[0].text
        total_recolected, currency = format_numbers(total_recolected)
        goal = founded_characteristics.findAll("span", {"class":re.compile("money")})[0].text  
        goal, crr = format_numbers(goal)
        total_backers = founded_characteristics.findAll("div", {"class":re.compile("block type-16 type-24-md medium soft-black")})[0].text 
        total_backers, crr = format_numbers(total_backers)

        html_str += "\ngeneral_chracteristics:\n\tproject_name: {}\n\tproject_welove: {}\n\tproject_location: {} \n\tproject_category: {}  \
        \n\nfounded_characteristics: \n\ttotal_recolected: {}\n\tgoal: {} \n\ttotal_backers: {}".format(project_name, \
            project_welove, project_location, project_category, total_recolected, goal, total_backers)

    except Exception as e:
        exception_str = "get_general_characteristics: 1"
        print(e)

    try:
        founded_characteristics = bsObj.findAll("div", {"class":re.compile("col-right col-4 py3 border-left spotlight-project-video-archive")})[0]
        total_recolected = founded_characteristics.findAll("span", {"class":re.compile("money")})[0].text
        total_recolected, currency = format_numbers(total_recolected)
        goal = founded_characteristics.findAll("div", {"class":re.compile("type-12.*")})[0].text  
        goal, crr = format_numbers(goal)
        total_backers = founded_characteristics.findAll("h3", {"class":re.compile("mb0*")})[1].text 
        total_backers, crr = format_numbers(total_backers)

        html_str += "\ngeneral_chracteristics:\n\tproject_name: {}\n\tproject_welove: {}\n\tproject_location: {} \n\tproject_category: {}  \
        \n\nfounded_characteristics: \n\ttotal_recolected: {}\n\tgoal: {} \n\ttotal_backers: {}".format(project_name, \
            project_welove, project_location, project_category, total_recolected, goal, total_backers)
    except Exception as e:
        exception_str = "get_general_characteristics: 2"
        print(e)
    
    project_name =  get_projec_name(bsObj)
    general_chracteristics = get_general_characteristics(bsObj)
    if general_chracteristics[0].text.replace("\n", "") == "Project We Love":
        project_welove =  True
        project_category = general_chracteristics[1].text.replace("\n", "")
        project_location = general_chracteristics[2].text.replace("\n", "")
    else:
        project_welove =  False
        project_category = general_chracteristics[0].text.replace("\n", "")
        project_location = general_chracteristics[1].text.replace("\n", "")

    html_dict=dict()
    html_dict["date"] = str(datetime.now())
    html_dict["project_name"] = project_name
    html_dict["total_recolected"] = total_recolected
    html_dict["goal"] = goal
    html_dict["total_backers"] = total_backers
    html_dict["project_welove"] = project_welove
    html_dict["project_location"] = project_location
    html_dict["project_category"] = project_category
    html_dict["url"] = scrap_url
    html_dict["currency"] = currency
    html_dict["search"] = search
    return html_dict, html_str

def get_general_characteristics(bsObj):

    try:
        general_chracteristics = bsObj.findAll("div", {"class":re.compile("col col-8 py3")})[0]
        general_chracteristics = general_chracteristics.findAll("a", {"class":re.compile("grey-dark.*")})
    except Exception as e:
        exception_str = "get_general_characteristics: 1"

    try:
        general_chracteristics = bsObj.findAll("div", {"class":re.compile("py2 py3-lg flex items-center auto-scroll-x")})[0]
        general_chracteristics = general_chracteristics.findAll("a")
    except Exception as e:
        exception_str = "get_general_characteristics: 2"

    return general_chracteristics


def webscrap_project(scrap_url, search):

    df_pledges = pd.DataFrame()
    df_monitor = pd.DataFrame()
    date = str(datetime.now())

    html_str = ""
    html_dict = dict()
    html_url = urlopen(scrap_url)
    #html_url = urlopen("https://www.kickstarter.com/projects/lynnemthomas/uncanny-magazine-year-6-raise-the-roof-raise-the-rates?ref=section-homepage-view-more-discovery-p1")

    bsObj =  BeautifulSoup(html_url)
    html_dict, html_str =get_founded_characteristics(bsObj)

    pledges_str =""
    pledges =  bsObj.findAll("div", {"class":re.compile("pledge__info")})
    pledge_cont = 0
    for pledge in pledges:
        pledge_dict = dict()
        #PLEDGE NO REWARD
        if pledge.text.replace("\n", "") == "Make a pledge without a reward":
            pledge_str = "\nPledge {}:".format(pledge_cont)
            pledge_title = "Make a pledge without a reward"
            description = ""
            aditional_description = ""
            aditional_description_2 =""
            pledge_amount = 0.0
            pledge_backers= 0.0
            content_list =[]
            content_list_str =""
        else:
            pledge_str = "\nPledge {}:".format(pledge_cont)
            #pledge_title
            pledge_title = pledge.findAll("h3", {"class":re.compile("pledge__title")})
            if len(pledge_title) >0:
                pledge_title = pledge_title[0].text
                pledge_title = pledge_title.replace("\n", "")
            else:
                pledge_title = "No title"

            #PLEDGE DESCRIPTION    
            pledge_description = pledge.findAll("div", {"class":re.compile("pledge__reward.*")})
            pledge_description = pledge_description[0]
            description = pledge_description.findAll("p")[0].text
            try:
                aditional_description = pledge_description.findAll("p")[1].text
            except Exception as e:
                #print("No aditional_description")
                aditional_description = ""
            try:
                aditional_description_2 = pledge_description.findAll("p")[2].text
            except Exception as e:
                #print("No aditional_description_2")
                aditional_description_2 = ""

            #MONEY
            money = pledge.findAll("span", {"class":re.compile("money.*")})
            pledge_amount = money[0].text
            pledge_amount, crr = format_numbers(pledge_amount)
            #pledge_backers
            pledge_backers = pledge.findAll("span", {"class":re.compile("pledge__backer-count")})[0].text
            pledge_backers = pledge_backers.replace("\n", "")
            pledge_backers = pledge_backers.replace(" pledge_backers","")
            pledge_backers = pledge_backers.replace("backers","")
            pledge_backers = pledge_backers.replace("backer","")
            pledge_backers = pledge_backers.replace(",","")
            pledge_backers = pledge_backers.replace(" ","")
            pledge_backers = float(pledge_backers)

            #PlEDGE CONTENT
            content = pledge.findAll("li", {"class":re.compile("list-disc")})
            content_list = []
            content_list_str = " \n\tTier content:"
            for element in content:
                element = element.text
                element = element.replace("\n", "") 
                #print(element)
                content_list.append(element)
                content_list_str += "\t\t{}".format(element)

            #ESTIMATED DELIVERY
            delivery_time = pledge.findAll("time", {"class":re.compile("invisible-if-js js-adjust-time")})
            if len(delivery_time)>0:
                delivery_time = delivery_time[0].text
            else:
                delivery_time = np.nan

        pledge_str += "\n\ttitle: {}\n\tpledge_description: {}\n\taditional_description: \
        {}\n\tdelivery_descripton: {}\n\tpledge_amount: {}\n\tbackers: {}\n\t{}"\
        .format(pledge_title, description, aditional_description, aditional_description_2, pledge_amount, pledge_backers, content_list_str)

        pledge_dict["pledge_count"] = pledge_cont
        pledge_dict["pledge_title"] = pledge_title
        pledge_dict["pledge_amount"] = pledge_amount
        pledge_dict["pledge_backers"] = pledge_backers
        pledge_dict["pledge_description"] = description
        pledge_dict["pledge_aditional_description_1"] = aditional_description
        pledge_dict["pledge_aditional_description_2"] = aditional_description_2
        if len(content_list) ==0:
            pledge_dict["content_list"] = np.nan
        else:
            pledge_dict["content_list"] = set(content_list)


        pledges_str += pledge_str
        pledge_cont +=1

        pandas_row = {**html_dict, **pledge_dict}
        pandas_row = pd.DataFrame(pandas_row, index =[pledge_cont])

        #SAVE INFO with whole information of pledges (one observation per pledge per project)
        if len(df_pledges) ==0:
            df_pledges = pandas_row
        else:
            df_pledges = df_pledges.append(pandas_row)

    #SAVE INFO with whole information of pledges (one observation per pledge per project)
    df_monitor = pd.DataFrame({**html_dict, **pledge_dict}, index =[date + "__" + html_dict["project_name"]])
    save_infromation(df_monitor, df_pledges, html_dict["project_name"],html_str, pledges_str)
    return pledges_str



mode = "JustPledges"
df_urls = pd.read_csv("Input/webscrapping_urls.csv")
df_urls = df_urls.drop_duplicates()
df_urls = df_urls.reset_index()
for row_cont in tqdm(range(len(df_urls))):
    scrap_url = df_urls.loc[row_cont, "url"]
    print("\n\nscrap_url",scrap_url)
    search = df_urls.loc[row_cont, "search"]
    if mode == "JustPledges":
        #JustPledges mode only iterates if url have never been scraped.
        try: #If df_pledges_hist not saved
            df_pledges_hist = pd.read_csv("DataFrames/kickstarter_pledges_hist.csv", index_col =0)
        except Exception as e:
            print(e)
            webscrap_project(scrap_url, search)
            df_pledges_hist = pd.read_csv("DataFrames/kickstarter_pledges_hist.csv", index_col =0)

        if scrap_url in df_pledges_hist.url.unique():
            print("project found in DataFrames/kickstarter_pledges_hist.csv")
            continue
        else:
            webscrap_project(scrap_url, search)
    else:
        webscrap_project(scrap_url, search)


