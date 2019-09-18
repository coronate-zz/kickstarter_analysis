import pandas as pd


def report_project_analysis(project_analysistype_dict, analysis_type):
    """
    """
    project_str = "\n\n\tANALYSIS TYPE: " + analysis_type + " in project pledges"
    for variable in project_analysistype_dict.keys():
        project_str += "\n\t\t" + variable + ": " + str(project_analysistype_dict[variable])
    return project_str


def report_search_analysis(analysis_dict, max_total_recolected_project, 
    max_backers_project, min_total_recolected_project, min_backers_project,
    search_analysis):
    report_str ="\n\n"+"*"*10 +"SEARCH NAME: " + search_analysis + "*"*10 +  "\n\n"

    #max_total_recolected_project
    max_total_recolected_project_str = "-"*100 +  "\nProject in search with most pledged money: {}".format(max_total_recolected_project)
    for analysis_type in analysis_dict[max_total_recolected_project].keys():
        project_str = report_project_analysis(analysis_dict[max_total_recolected_project][analysis_type], analysis_type)
        max_total_recolected_project_str += project_str
    report_str += max_total_recolected_project_str

    #min_total_recolected_project
    min_total_recolected_project_str = "\n\n" + "-"*100 +  "\nProject in search with lowest pledged money: {}".format(min_total_recolected_project)
    for analysis_type in analysis_dict[min_total_recolected_project].keys():
        project_str = report_project_analysis(analysis_dict[min_total_recolected_project][analysis_type], analysis_type)
        min_total_recolected_project_str += project_str
    report_str += min_total_recolected_project_str

    #max_backers_project
    max_backers_project_str = "\n\n" + "-"*100 +  "\nProject in search with highest number of backers: {}".format(max_backers_project)
    if max_backers_project == max_total_recolected_project:
        max_backers_project_str += "\n\t\t Is same project as Project in search with most pledge money"
    else:    
        for analysis_type in analysis_dict[max_backers_project].keys():
            project_str = report_project_analysis(analysis_dict[max_backers_project][analysis_type], analysis_type)
            max_backers_project_str += project_str
    report_str += max_backers_project_str

    #min_backers_project
    min_backers_project_str = "\n\n" + "-"*100 +  "\nProject in search with highest number of backers: {}".format(min_backers_project)
    if min_backers_project == min_total_recolected_project:
        min_backers_project_str += "\n\t\t Is same project as Project in search with lowest pledge money"
    else:    
        for analysis_type in analysis_dict[min_backers_project].keys():
            project_str = report_project_analysis(analysis_dict[min_backers_project][analysis_type], analysis_type)
            min_backers_project_str += project_str
    report_str += max_backers_project_str

    for project_name in analysis_dict.keys():
        project_str = "\n\nProject: {}".format(project_name)
        if project_name not in [max_total_recolected_project, max_backers_project, min_total_recolected_project, min_backers_project]:
            for analysis_type in analysis_dict[project_name].keys():
                project_str += report_project_analysis(analysis_dict[project_name][analysis_type], analysis_type)
            report_str += project_str
    return report_str


df_pledges_hist = pd.read_csv("../WebScrapping/DataFrames/kickstarter_pledges_hist.csv", index_col =0)
search_analysis = "todos los especieros en kickstarter mostpledged"
df_analyse  = df_pledges_hist[df_pledges_hist.search == search_analysis]
df_analyse_stats = df_analyse.describe()


backer_meanaportation_search = df_analyse_stats["pledge_amount"]["mean"]/df_analyse_stats["pledge_backers"]["mean"]
max_total_recolected_amount =0
max_total_backers_amount =0
min_total_recolected_amount =100000
min_total_backers_amount =100000000

analysis_dict = dict()
for project_name in df_analyse.project_name.unique():
    print(project_name)
    analysis_dict[project_name] = dict()
    df_analyse_project = df_analyse[df_analyse.project_name == project_name]
    total_recolected = df_analyse_project.total_recolected.values[0]
    total_backers = df_analyse_project.total_backers.values[0]
    
    #MAX PROJECTS
    if total_recolected> max_total_recolected_amount:
        max_total_recolected_amount = total_recolected
        max_total_recolected_project = project_name

    if total_backers> max_total_backers_amount:
        max_total_backers_amount = total_backers
        max_backers_project = project_name

    #MIN PROJECTS
    if total_recolected< min_total_recolected_amount:
        min_total_recolected_amount = total_recolected
        min_total_recolected_project = project_name

    if total_backers< min_total_backers_amount:
        min_total_backers_amount = total_backers
        min_backers_project = project_name


    backer_meanaportation_project = df_analyse_project.pledge_amount.sum() / df_analyse_project.pledge_backers.sum()
    
    #MAX Backers pledge:
    max_backer_per_pledge =df_analyse_project.pledge_backers.max()
    df_analyse_project_maxbackers =df_analyse_project[df_analyse_project.pledge_backers == max_backer_per_pledge].groupby("project_name").first().reset_index()
    analysis_dict[project_name]["max_backers"] = dict()
    analysis_dict[project_name]["max_backers"]["pledge_amount"] = df_analyse_project_maxbackers["pledge_amount"].values[0]
    analysis_dict[project_name]["max_backers"]["number_of_backers"]= df_analyse_project_maxbackers["pledge_backers"].values[0]
    if analysis_dict[project_name]["max_backers"]["number_of_backers"] >0:
        analysis_dict[project_name]["max_backers"]["total_pledged"] = analysis_dict[project_name]["max_backers"]["pledge_amount"]* analysis_dict[project_name]["max_backers"]["number_of_backers"]
    else:
        analysis_dict[project_name]["max_backers"]["total_pledge"] =0
    analysis_dict[project_name]["max_backers"]["description"] = df_analyse_project_maxbackers.pledge_description.values[0]
    analysis_dict[project_name]["max_backers"]["title"] = df_analyse_project_maxbackers.pledge_title.values[0]
    analysis_dict[project_name]["max_backers"]["aditional1"] = df_analyse_project_maxbackers.pledge_aditional_description_1.values[0]
    analysis_dict[project_name]["max_backers"]["aditional2"] = df_analyse_project_maxbackers.pledge_aditional_description_2.values[0]

    #MIN Backers pledge:
    min_backer_per_pledge =df_analyse_project.pledge_backers.min()
    df_analyse_project_minbackers =df_analyse_project[df_analyse_project.pledge_backers == min_backer_per_pledge].groupby("project_name").first().reset_index()
    analysis_dict[project_name]["min_backers"] = dict()
    analysis_dict[project_name]["min_backers"]["pledge_amount"] = df_analyse_project_minbackers["pledge_amount"].values[0]
    analysis_dict[project_name]["min_backers"]["number_of_backers"]= df_analyse_project_minbackers["pledge_backers"].values[0]
    analysis_dict[project_name]["min_backers"]["total_pledge"] = analysis_dict[project_name]["min_backers"]["pledge_amount"]*analysis_dict[project_name]["min_backers"]["number_of_backers"]
    analysis_dict[project_name]["min_backers"]["title"] = df_analyse_project_minbackers.pledge_title.values[0]
    analysis_dict[project_name]["min_backers"]["aditional1"] = df_analyse_project_minbackers.pledge_aditional_description_1.values[0]
    analysis_dict[project_name]["min_backers"]["aditional2"] = df_analyse_project_minbackers.pledge_aditional_description_2.values[0]


    #MAX PLEDGE pledge:
    max_amount_per_pledge =df_analyse_project.pledge_amount.max()
    df_analyse_project_maxpledge =df_analyse_project[df_analyse_project.pledge_amount == max_amount_per_pledge].groupby("project_name").first().reset_index()
    analysis_dict[project_name]["max_pledge"] = dict()
    analysis_dict[project_name]["max_pledge"]["pledge_amount"] = df_analyse_project_maxpledge["pledge_amount"].values[0]
    analysis_dict[project_name]["max_pledge"]["number_of_backers"]= df_analyse_project_maxpledge["pledge_backers"].values[0]
    analysis_dict[project_name]["max_pledge"]["total_pledge"] = analysis_dict[project_name]["max_pledge"]["pledge_amount"]*analysis_dict[project_name]["max_pledge"]["number_of_backers"]
    analysis_dict[project_name]["max_pledge"]["description"] = df_analyse_project_maxpledge.pledge_description.values[0]
    analysis_dict[project_name]["max_pledge"]["title"] = df_analyse_project_maxpledge.pledge_title.values[0]
    analysis_dict[project_name]["max_pledge"]["aditional1"] = df_analyse_project_maxpledge.pledge_aditional_description_1.values[0]
    analysis_dict[project_name]["max_pledge"]["aditional2"] = df_analyse_project_maxpledge.pledge_aditional_description_2.values[0]

    #MIN PLEDGE pledge:
    min_amount_per_pledge =df_analyse_project.pledge_amount.min()
    df_analyse_project_minpledge =df_analyse_project[df_analyse_project.pledge_amount == min_amount_per_pledge].groupby("project_name").first().reset_index()
    analysis_dict[project_name]["min_pledge"] = dict()
    analysis_dict[project_name]["min_pledge"]["pledge_amount"] = df_analyse_project_minpledge["pledge_amount"].values[0]
    analysis_dict[project_name]["min_pledge"]["number_of_backers"]= df_analyse_project_minpledge["pledge_backers"].values[0]
    analysis_dict[project_name]["min_pledge"]["total_pledge"] = analysis_dict[project_name]["min_pledge"]["pledge_amount"]*analysis_dict[project_name]["min_pledge"]["number_of_backers"]
    analysis_dict[project_name]["min_pledge"]["title"] = df_analyse_project_minpledge.pledge_title.values[0]
    analysis_dict[project_name]["min_pledge"]["aditional1"] = df_analyse_project_minpledge.pledge_aditional_description_1.values[0]
    analysis_dict[project_name]["min_pledge"]["aditional2"] = df_analyse_project_minpledge.pledge_aditional_description_2.values[0]


    #AVG Backers pledge:
    analysis_dict[project_name]["avg_pledge"] = dict()
    analysis_dict[project_name]["avg_pledge"]["pledge_amount"] = df_analyse_project["pledge_amount"].mean()
    analysis_dict[project_name]["avg_pledge"]["number_of_backers"] = df_analyse_project["pledge_backers"].mean()
    analysis_dict[project_name]["avg_pledge"]["total_pledge"] = analysis_dict[project_name]["avg_pledge"]["pledge_amount"]*analysis_dict[project_name]["avg_pledge"]["number_of_backers"]

report_str =report_search_analysis(analysis_dict, max_total_recolected_project, max_backers_project, min_total_recolected_project, min_backers_project, search_analysis)

text_file = open("SearchReports/" + search_analysis.replace("/", "-") + "_report.txt", "w")
text_file.write(report_str)
