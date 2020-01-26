from selenium import webdriver
from bs4 import BeautifulSoup as bs
from bs4 import SoupStrainer
import pandas as pd
import time
        

# def get_links():
#     game_links = list()
#     # next_page = driver.find_element_by_xpath('/html/body/main/div[2]/div/div/div[3]/div/div/div/nba-stat-table/div[3]/div/div/a[2]')
#     # while next_page:
#     count = 0
#     while count < total_table_pages:
#         if count >= 1:
#             search_tabele = call_selenium_bs4(True)
#         else:
#             search_tabele = call_selenium_bs4()
            
#         for col1 in search_tabele.findAll('td',{'class':'lineup'}):
#             for link in col1.findAll('a',href=True):
#                 game_links.append([link['href'],link.getText()])
#         count += 1
    
#     return game_links
                    
def call_selenium_bs4(next = False):
    '''
    description : Function generates a new driver function every time called.
    returns : returns a BS4 object which has the table location for the NBA team
    '''
    if next == True:
        # logic for iterating in tables
        next_page = driver.find_element_by_xpath('/html/body/main/div[2]/div/div/div[3]/div/div/div/nba-stat-table/div[3]/div/div/a[2]')
        next_page.click()
    html = driver.execute_script("return document.documentElement.outerHTML")
    sauce = bs(html,'html.parser')
    div = sauce.findAll('div',{'class':'nba-stat-table'})[0]
    table = div.find('table')
    return table


def create_team_stats_table():
    '''
    description : functions main purpose is to generate team_stats table.
                  It also calls the player_stats function for every link it finds in the main table.
    returns : A csv format team_sats table and player_stats table
    '''
    player_data_frame = pd.DataFrame()
    headers = list()
    game_links = list() 
    for h in call_selenium_bs4().findAll("th"):   #method returns bs4 object - table
        headers.append(h.getText())

    data_col = list()
    data_row = [data_col]
    
    count = 0
    # next_page = call_selenium_bs4('driver').find_element_by_xpath('/html/body/main/div[2]/div/div/div[3]/div/div/div/nba-stat-table/div[3]/div/div/a[2]')
    while count < total_table_pages:
        if count >= 1:
            search_table = call_selenium_bs4(True)
        else:
            search_table = call_selenium_bs4()
        for i in search_table.findAll('tr')[1:]:
            for j in i.findAll('td'):
                temp = j.getText()
                if '\n' in temp:
                    temp = temp.replace('\n',' ')
                    data_col.append(temp.strip())
                else:
                    data_col.append(temp)
            data_row.append(data_col)
            data_col = []
        
        # loop to get all data from that match, calls create_player_stats table
        for col1 in search_table.findAll('td',{'class':'lineup'}):
            for link in col1.findAll('a',href=True):
                player_table = create_player_stats_table([link['href'],link.getText()])
                player_data_frame = player_data_frame.append(player_table)
            
        count += 1
     
    
    team_stats = pd.DataFrame(data_row, columns = headers)
    team_stats = team_stats.drop(team_stats.index[:1])
    team_stats.to_csv(r'D:\vs_code_workspace\DS 5010\team_stats_v2.csv',index=None, header=True)
    player_data_frame.to_csv(r'D:\vs_code_workspace\DS 5010\player_stats_v2.csv',index=None, header=True)
    return

def create_player_stats_table(game_link_and_name):
    '''
    description : extracts per match info.
    input : link and name of the match
    returns: a data frame containing the player_stats for that match
    '''
    # [1 x 2 ] dimension of game_link_and_name
    i = game_link_and_name
    match_against = i[1] 
    # path of chrome driver, so that the program knows where to find it
    chromeDriver = "D:\\software setups\\coding\\chromedriver.exe"
    new_driver = webdriver.Chrome(chromeDriver)
    # appending the link
    new_driver.get("https://stats.nba.com"+str(i[0]))
    time.sleep(5)
    # script to extract all HTML data from the page using selenium
    html = new_driver.execute_script("return document.documentElement.outerHTML")
    sauce2 = bs(html,'html.parser')
    # home vs away , table location are placed differnetly
    
    # NBA has positioned the tables in such a way that if the match is Away then celtics table will be on top
    # else celtics table will be on the botton
    # logic to find celtics table
    time.sleep(2)
    if '@' in i[1]:
        div = sauce2.find('div',{'class':'nba-stat-table'})
    else:
        div = sauce2.findAll('div',{'class':'nba-stat-table'})[1]
    
    
    # bs4 objects for table head and table body
    player_head = div.find('thead')
    player_body = div.find('tbody')
    
    player_data_col = list()
    # list of list, following a table structure
    player_data_row = [player_data_col]
    headers = list()
        
    for h in player_head.findAll("th"):
        headers.append(h.getText())
    # appending our matchup variable
    headers.append("MATCHUP")
    
    # extracting data row by row
    for tr in player_body.findAll('tr'):
        for td in tr.findAll('td'):
            temp = td.getText()
            if '\n' in temp:
                # replacing \n with nothing
                temp = temp.replace('\n',' ')
                # stripping the data for white spaces 
                player_data_col.append(temp.strip())
            else:
                player_data_col.append(temp)
        # appending the data
        player_data_col.append(match_against)
        player_data_row.append(player_data_col)
        # resetting it to nothing
        player_data_col = []


    player_stats = pd.DataFrame(player_data_row,columns=headers)
    # player_data_frame = player_data_frame.append(player_stats)
    
    new_driver.close()
    return player_stats
    
        
    

if __name__ == "__main__":
    
    
    total_table_pages = 2
    chromeDriver = "D:\\software setups\\coding\\chromedriver.exe"
    driver = webdriver.Chrome(chromeDriver)
    # driver.get("https://stats.nba.com/team/1610612738/boxscores/?sort=MATCHUP&dir=-1")
    driver.get("https://stats.nba.com/team/1610612738/boxscores/?Season=2018-19&SeasonType=Regular%20Season")
    time.sleep(2)
    create_team_stats_table()