"""
This file contains functions that ultimately work to take in a url to a github repo and estimate the 
average number of contributors per week over the lifetime of the project.

AF(GITHUB REPO LIST) = CSV OF REPO CONTRIBUTION INFO

Steps:
1) Get urls of all the repos of interest
For a given url:
2) Select five different weekly date samples and create five request urls to parse
3) Get the number of contributors that week along with the number of lines they contributed and their username
4) Save to CSV using pandas with columns ["Repo name", "average number of contributors", "average loc changes per week", "repo link"]
"""
import random
import time
import pandas as pd
from os.path import exists
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# wait documentation at https://selenium-python.readthedocs.io/waits.html
from bs4 import BeautifulSoup
import pdb

random.seed(2022)
START_DATE = datetime.date(2015,1,1) #after sampling a number of repos, 2015 seems like a typical date contribution starts
END_DATE = datetime.date.today()
COLUMN_NAMES = ['repo','avg_num_contributors','start_date','contrib_info','date_urls']
TIME_WINDOW = datetime.timedelta(days=14) # 1 week means even for very popular repos we won't go over Github's display limit


def _create_different_date_urls(base_url, start_date, end_date, num_urls=5):
    #create num_urls different urls with date ranges to get contributor information from
    #base url should be in format https://github.com/repo-owner/repo/graphs/contributors
    request_urls = []
    for i in range(num_urls):
        date1 = start_date + datetime.timedelta(days=random.randint(0, (end_date-start_date).days))
        date2 = date1 + TIME_WINDOW
        date1_string, date2_string = date1.strftime('%Y-%m-%d'), date2.strftime('%Y-%m-%d')
        date_string = "?from={0}&to={1}&type=c".format(date1_string, date2_string)
        request_urls.append(base_url+date_string)
    
    return request_urls

def _get_initial_date_range(driver, url):
    #wait for a bit
    driver.get(url)

    time.sleep(4)
    element = WebDriverWait(driver, 30).until(
        # EC.presence_of_element_located((By.ID, "contributors")) #wait max 10s until contributors section loads
        EC.presence_of_element_located((By.CLASS_NAME, "Layout-main"))
    )
    element_html = element.get_attribute("outerHTML")
    soup = BeautifulSoup(element_html, features="html.parser")
    assert len(soup.find_all(class_="js-date-range Subhead-heading")) == 1, "Problem with date header"
    date_range = soup.find_all(class_="js-date-range Subhead-heading")[0].text
    date_list = date_range.split(" – ")
    # try:
    assert len(date_list)==2, "Problem with date splitting"
    # except:
    #     print("Problem with date splitting")
    #     pdb.set_trace()
    datetime_list = [datetime.datetime.strptime(date, '%b %d, %Y') for date in date_list]
    return datetime_list

def _get_contributor_information(driver, url):
    """
    Given a github contributor's url, returns contribution information: num_contributors, contrib_info
    contrib_info: a dictionary {username: (num_commits, loc_added, loc_removed)}
    """

    driver.get(url)

    time.sleep(2)
    element = WebDriverWait(driver, 10).until(
        # EC.presence_of_element_located((By.ID, "contributors")) #wait max 10s until contributors section loads
        EC.presence_of_element_located((By.CLASS_NAME, "Layout-main"))
    )

    element_html = element.get_attribute("outerHTML")
    
    soup = BeautifulSoup(element_html, features='html.parser') # parse into soup for easier searching
    
    # contributor_html = soup.find_all(class_="d-inline-block mr-2 float-left")
    
    left_users_elt = soup.find_all(class_="contrib-person float-left col-6 my-2 pr-2")
    right_users_elt = soup.find_all(class_="contrib-person float-left col-6 my-2 pl-2")
    users_elt = left_users_elt+right_users_elt

    contrib_info = {}
    for elt in users_elt:
        username = elt.find_all(class_="text-normal")[1].text
        loc_added = elt.find_all(class_="color-fg-success text-normal")[0].text
        loc_removed = elt.find_all(class_="color-fg-danger text-normal")[0].text
        num_commits = elt.find_all(class_="Link--secondary text-normal")[0].text

        contrib_info[username] = (num_commits, loc_added, loc_removed)
    
    num_contributors = len(users_elt)
    # usernames = [elt['href'][1:] for elt in contributor_html] #the href contains "/username" in each instance

    return num_contributors, contrib_info

def load_repo_from_csv(repo_csv):
    #use pandas
    df = pd.read_csv(repo_csv) 
    df = df[['Name','Github']].dropna() #get repo name and links to repo and drop those without links
    repo_dict = {}
    for index, row in df.iterrows():
        repo_url = "{0}/graphs/contributors".format(row['Github'])
        repo_dict[row['Name']] = {'repo_url':repo_url}
    return repo_dict

def create_contributor_sample_dict(webdriver, url_list):
    """
    Returns avg_num_contributors, contrib_sample_dict
    contrib_sample_dict = {url: {user: (num_commits, loc_added, loc_removed)}}
    """
    total_contributors = 0 
    contrib_sample_dict = {}
    for i, link in enumerate(date_urls):
        num_contributors, contrib_info = _get_contributor_information(webdriver, link)
        contrib_sample_dict[link] = contrib_info
        total_contributors += num_contributors
    avg_num_contributors = total_contributors/len(date_urls)

    return avg_num_contributors, contrib_sample_dict


if __name__ == "__main__":

    # repo_csv = "" #add local pathname
    # repo_url_dict = load_repo_from_csv(repo_csv) #returns dict with e.g. {repo name:{'repo_url':repo_url}}
    # add start and end date to url dict, then add the date links {repo name:{'repo_url':repo_url,'date_links':[url1,url2]}}
    # then get contrib info, including the average num contribs: 
    # {repo name:{'repo_url':repo_url,'date_links':[url1,url2], 'avg_contributors':avg,'contrib_info':(user,commits,added,deleteddate:)}
    webdriver = webdriver.Safari()
    repo_link_file = "Copy of List of tools for MLOps_v4 - Tools.csv"
    result_filename = "scraped_contributor_information_for_repos.csv"
    prior_df = pd.read_csv(result_filename)
    scraped_repos = prior_df['repo'].tolist() 
    #get the repos already in the result df. This is especially useful because often there are failed runs so script needs to be rerun
    
    #"/Users/maxlangenkamp/Downloads/Copy of List of tools for MLOps_v4 - Tools.csv"
    # test_url = "https://github.com/pytorch/pytorch/graphs/contributors"

    repo_link_dict = load_repo_from_csv(repo_link_file) # {repo name:{'repo_url':repo_url}}

    #get the date urls
    
    not_scraped = set()

    num_repos = 0
    for repo_name, repo_info in repo_link_dict.items():
        if repo_name in scraped_repos:
            continue
        # if repo_name not in not_scraped:
        #     continue
        num_repos += 1
        url = repo_info['repo_url']
        if num_repos % 14 == 0:
            print("{0} out of {1} repos complete".format(num_repos,len(repo_link_dict)))
        try: #this is a hacky way to 
            start_date, end_date = _get_initial_date_range(webdriver, url)
        except:
            # print(repo_name, "did not get added to the final sheet first time around")
            not_scraped.add(repo_name)
            continue 
        date_urls = _create_different_date_urls(url, start_date, end_date)
        # add start and end dates and date urls to dict
        start_date_string = start_date.strftime('%b %d, %Y')

        # get repo information for each date
        avg_num_contributors, contrib_sample_dict = create_contributor_sample_dict(webdriver, date_urls)
        repo_link_dict[repo_name]['avg_num_contributors'] = avg_num_contributors
        repo_link_dict[repo_name]['start_date'] =  start_date_string
        repo_link_dict[repo_name]['contrib_info'] = contrib_sample_dict
        repo_link_dict[repo_name]['date_urls'] = date_urls

    if num_repos > 0:
        print("{0} repos did not get added. The repos were: {1}".format(len(not_scraped), not_scraped))
        final_df = pd.DataFrame.from_dict(repo_link_dict).T #to make sure the repos are the rows
        final_df.reset_index(inplace=True)
        final_df.rename(columns={'index':'repo'}, inplace=True)
        final_df = final_df[['repo','repo_url','avg_num_contributors','start_date','contrib_info','date_urls']] #order columns    
        final_df = final_df.dropna()

        final_df = pd.concat([prior_df,final_df])
        # note there is sometimes a problem with an extra index column being added to the left of the dataframe
        final_df.to_csv(result_filename)
    else:
        print("No repos added")

    webdriver.quit()
