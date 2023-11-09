#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 25 18:46:57 2023

@author: thomasgaudin
"""

import csv, random
import numpy as np
import pandas as pd
import re
import requests

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup
from time import sleep
from copy import deepcopy
from collections import defaultdict

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

from pandas.plotting import table

from tabulate import tabulate

from matplotlib.offsetbox import OffsetImage, AnnotationBbox

#############################
# Functions for Running the Tom Model for any tournament
#############################

def getImage(path):
    
    return OffsetImage(plt.imread(path), zoom=.1)

#webscraping function

def get_Elo_ranks():
    """Scrapes Elo Ratings to pull most current ratings values.
       Returns a Pandas dataframe of Elo ranks for all nations."""
    
    #define webdriver. For me on Mac, this is Safari. Could be different for others.
    driver = webdriver.Safari()
    wait = WebDriverWait(driver, 60)
    
    #Using this website for ratings
    url = "https://www.eloratings.net"
    
    driver.get(url)
    wait.until(EC.visibility_of_all_elements_located((By.ID, "maindiv")))
    
    #Rewrite the html as lxml
    soup = BeautifulSoup(driver.page_source, 'lxml')
    
    #Find all cells of the table containing a country
    countries = soup.find_all("div",{"class":"slick-cell l1 r1 team-cell narrow-layout"})
    
    nations = []
    
    #Pull all country names and append to nations list
    for nation in countries:
        country = re.findall("handleLink\(\'([a-zA-Z\_\-]+)\'\)", str(nation))
        nations.append(country[0])
    
    #Find all cells of the table containing an Elo ranking value
    rankings = soup.find_all("div",{"class":"slick-cell l2 r2 rating-cell narrow-layout"})
    
    ranks = []
    
    #Pull all rating values and append to rankings list
    for rank in rankings:
        ranking = re.findall('">(\d*)</div>', str(rank))
        ranks.append(ranking[0])
    
    #create a dictionary out of the zipped lists and turn it into a pandas dataframe
    elo = dict()
    
    for nation, rank in zip(nations, ranks):
        elo[nation] = rank
        
    elos = pd.DataFrame(elo.items(), 
                   index = np.arange(1, len(nations)+1),
                   columns = ['Team', 'Points'])
    
    return elos




def need_new_elo(group_table):   
    """
    Checks to see if new set of Elo  ratings is needed before running web 
    scraping code
    """
    
    
    new_elo = input("Use Current Elos (Y/N)? ")

    if new_elo == "Y":

        elo_rank = get_Elo_ranks()
        elo_rank = elo_rank.set_index('Team')

        if len(elo_rank.index) > 0:
            teams = True

        else:
            teams = False

        while teams == False:

            elo_rank = get_Elo_ranks()
            elo_rank = elo_rank.set_index('Team')

            if len(elo_rank.index) > 0:
                teams = True

            else:
                teams = False

        for team in group_table.index:
            group_table.loc[team, "Elo"] = elo_rank.loc[team, "Points"]

    elif new_elo == "N":
        pass

    else:
        print("Pick a Valid Option.")
        
    return group_table

#Elo Calculation functions

def calculate_We(Ro, opponent_Ro, location):
    """ Calculate the We from the formula given by ELO.
        Inputs:
            Ro - Elo rating of team (int)
            opponent_Ro - Elo rating of opponent (int)
            location - either the string 'home' or 'away' 
        Returns:
            Win Expectancy, type: float
    """
    
    #if the team is at home, calcuate difference in Elo with home boost
    if location == 'home':
        dr = (Ro + 100) - opponent_Ro
        
    #if the team is on the road, calculate difference in Elo, boost for oppoent
    elif location == 'away':
        dr = Ro - (opponent_Ro + 100)
        
    #formula from eloratings.net
    We = 1 / ( (10 ** (-dr / 400)) + 1)

    return We

def calculate_neutral_We(Ro, opponent_Ro):
    """ Calculate the We from the formula given by ELO assuming neutral site.
        Inputs:
            Ro - Elo rating of team (int)
            opponent_Ro - Elo rating of opponent (int)
        Returns:
            Win Expectancy, type: float
    """
    
    #calculate difference in Elo
    dr = Ro - opponent_Ro
    
    #formula from eloratings.net
    We = 1 / ( (10 ** (-dr / 400)) + 1)

    return We

def calculate_FIFA_We(Ro, opponent_Ro):
    """ Calculate the We from the formula given by ELO.
        Inputs:
            Ro - Elo rating of team (int)
            opponent_Ro - Elo rating of opponent (int)
            location - either the string 'home' or 'away' 
        Returns:
            Win Expectancy, type: float
    """

    dr = Ro - opponent_Ro
        
    #formula from eloratings.net
    We = 1 / ( (10 ** (-dr / 600)) + 1)

    return We

def davidson_home_wp(home_We, away_We, theta=1.7):
    """ Calculates the probability of a win for any team given the win expectancy
        calculated from the difference in Elo for each team. Formula given by 
        Davidson (1970).
        Inputs:
            home_We - win expectancy for home team (float)
            away_We - win expectancy for away team (float)
            theta - float fudge factor to make equations work, I have found 
                    that 1.7 gives realistic results
        Returns:
            Win Probability, type: float
    """
    
    hwp = home_We / (home_We + (theta * away_We) )
    
    return hwp

def davidson_away_wp(home_We, away_We, theta):
    """ Calculates the probability of a loss for any team given the win expectancy
        calculated from the difference in Elo for each team. Formula given by 
        Davidson (1970).
        Inputs:
            home_We - win expectancy for home team (float)
            away_We - win expectancy for away team (float)
            theta - float fudge factor to make equations work, I have found 
                    that 1.7 gives realistic results
        Returns:
            Loss Probability, type: float
    """
    
    awp = away_We / ( (theta * home_We) + away_We)
    
    return awp

def davidson_tie_prob(home_We, away_We, theta):
    """ Calculates the probability of a draw for any match given the win expectancy
        calculated from the difference in Elo for each team. Formula given by 
        Davidson (1970).
        Inputs:
            home_We - win expectancy for home team (float)
            away_We - win expectancy for away team (float)
            theta - float fudge factor to make equations work, I have found 
                    that 1.7 gives realistic results
        Returns:
            Draw Probability, type: float
    """
    
    tie = ( (theta**2 - 1) * home_We * away_We ) / ((home_We + (theta * away_We) ) * ( (theta * home_We) + away_We))
    
    return tie

def calculate_home_win_probability(home_Ro, away_Ro):
    """ Win probability formula from Elo ratings website. 
        Can be used, but doesn't work well."""

    wp = min((1 / (1 + 10**((away_Ro - home_Ro)/400)))**1.75 + 0.1, 1)

    return wp

def calculate_away_win_probability(home_Ro, away_Ro):
    """ Loss probability formula from Elo ratings website. 
        Can be used, but doesn't work well."""

    wp = max((1 / (1 + 10**((home_Ro - away_Ro)/400)))**1.75 - 0.1, 0)

    return wp

def calculate_elo(Ro, We, WLD, Km, GD=1):
    """ ELO formula used for calculation of new Elo after a match.
        Can calculate real Elo if your code simulates goals scored.
        Inputs:
            Ro - pre-match Elo (int)
            We - team win expectancy for match (float)
            WDL - Determined by the outcome generater function
                  1.0 for win, 0.5 for draw, 0.0 for loss (float)
            GD - Goal Difference of match, defaults to 1 (int)
            Km - tournament weight constant from eloratings.net (int)
        Returns:
            Post-match Elo, type: float
    """
    
    #Adjust weight constant based on match GD
    if GD < 2:
        GDM = Km

    elif GD == 2:
        GDM = (1.5 * Km)

    elif GD == 3:
        GDM = (1.75 * Km)

    elif GD >= 4:
        GDM = (Km * (1.75 + (GD - 3) / 8 ))
        
    #calculate new Elo
    Rn = Ro + (GDM * (WLD - We))

    return Rn

def calculate_FIFA(Ro, We, WLD, Km):
    """ ELO formula used for calculation of new Elo after a match.
        Can calculate real Elo if your code simulates goals scored.
        Inputs:
            Ro - pre-match Elo (int)
            We - team win expectancy for match (float)
            WDL - Determined by the outcome generater function
                  1.0 for win, 0.5 for draw, 0.0 for loss (float)
            GD - Goal Difference of match, defaults to 1 (int)
            Km - tournament weight constant from eloratings.net (int)
        Returns:
            Post-match Elo, type: float
    """

        
    #calculate new Elo
    Rn = Ro + (Km * (WLD - We))

    return Rn


def print_probabilities(matches, elo_rank):
    """ Prints the pre-tournament win probability for every match in a tournament 
        given pre-tournament Elo ratings.
        Inputs:
            matches - List of lists for every match in the tournament
                      home team is listed first in each sub-list
            elo_rank - Dataframe of all team Elo ratings
            host - Name of the host nation for neutral tournament
        Returns:
            Nothing
    """
    
    for match in matches:

        #initialize home team and ELO
        home_team = match[0]
        home_elo = elo_rank[home_team]

        #initialize away team and ELO
        away_team = match[1]
        away_elo = elo_rank[away_team]

        #calculate We for new ELO calc
        home_we = calculate_We(home_elo, away_elo, 'home')
        away_we = calculate_We(away_elo, home_elo, 'away')

        #Determine win probability for each team
        home_wp = davidson_home_wp(home_we, away_we)
        away_wp = davidson_away_wp(home_we, away_we)
        draw_wp = davidson_tie_prob(home_we, away_we)

        print(f'{home_team} / draw / {away_team}')
        print(f'{round(home_wp,2)} / {round(draw_wp,2)} / {round(away_wp,2)}')

def print_neutral_probabilities(matches, elo_rank, host):
    """ Prints the pre-tournament win probability for every match in a neutral 
        site tournament given pre-tournament Elo ratings.
        Inputs:
            matches - List of lists for every match in the tournament
            elo_rank - Dataframe of all team Elo ratings
            host - Name of the host nation for neutral tournament
        Returns:
            Nothing
    """
    
    for match in matches:
        
        if host in match:
            
            #initialize home team and ELO
            home_team = host
            home_elo = int(elo_rank.loc[home_team]['Points'])
            
            #initialize away team and ELO
            if match[0] == host:
                away_team = match[1]
                
            elif match[1] == host:
                away_team = match[0]
                
            else:
                continue
                
            away_elo = int(elo_rank.loc[away_team]['Points'])
            
            #calculate We for new ELO calc using neutral site
            home_we = calculate_We(home_elo, away_elo, 'home')
            away_we = calculate_We(away_elo, home_elo, 'away')
            
        else:
            
            #initialize home team and ELO
            home_team = match[0]
            home_elo = int(elo_rank.loc[home_team]['Points'])

            #initialize away team and ELO
            away_team = match[1]
            away_elo = int(elo_rank.loc[away_team]['Points'])

            #calculate We for new ELO calc using neutral site
            home_we = calculate_neutral_We(home_elo, away_elo)
            away_we = calculate_neutral_We(away_elo, home_elo)

        #Determine win probability for each team
        home_wp = davidson_home_wp(home_we, away_we)
        away_wp = davidson_away_wp(home_we, away_we)
        draw_wp = davidson_tie_prob(home_we, away_we)

        print(f'{home_team} / draw / {away_team}')
        print(f'{round(home_we,2)} /    / {round(away_we,2)}')
        print(f'{round(home_wp,2)} / {round(draw_wp,2)} / {round(away_wp,2)}')
        
def outcome_generator(home_wp, away_wp, draw_wp=0):
    """ Code that simulates each game. Chooses outcome of win/draw/loss based
        on weighted random nnumber generator. Weights come from win probability
        calculations.
        Inputs:
            home_wp - Win Probability for home team (float)
            away_wp - Win Probability for away team (float)
            draw_wp - Probaility of a draw (float)
        Returns:
            outcome - either 1.0 for home win, 0.5 for draw, 0.0 for home loss
                      Type: float
    """
    
    #sort weights, outcomes dict: win = 1, draw = 0.5, loss = 0.0
    weights = {1.0: home_wp, 0.5: draw_wp, 0.0: away_wp}
    sorted_weights = {k: v for k, v in sorted(weights.items(), key=lambda item: item[1])}

    #print(sorted_weights)

    weights_list = []

    outcomes = []
    probabilities = []

    for weight in sorted_weights.keys():
        weights_list.append((weight, sorted_weights[weight]))

    for outcome in weights_list:
        outcomes.append(outcome[0])

    for probability in weights_list:
        probabilities.append(probability[1])

    #choose a random outcome 
    outcome = random.choices(outcomes, weights=probabilities, k=1)

    #print(outcomes)
    #print(probabilities)
    #print(outcome)
    
    return outcome[0]

def calc_neutral_match_We(match_table, match_num, group_table, host):
    
    teams = [match_table.loc[match_num, 'Home'], match_table.loc[match_num, 'Away']]

    if host in teams:

        #initialize home team and ELO
        home_team = host
        home_elo = int(group_table.loc[home_team, 'Elo'])

        #initialize away team and ELO
        if match_table.loc[match_num, 'Home'] == host:
            away_team = match_table.loc[match_num, 'Away']

        elif match_table.loc[match_num, 'Away'] == host:
            away_team = match_table.loc[match_num, 'Home']

        away_elo = int(group_table.loc[away_team, 'Elo'])

        #calculate We for new ELO calc
        home_we = calculate_We(home_elo, away_elo, 'home')
        away_we = calculate_We(away_elo, home_elo, 'away')

    else:

        #initialize home team and ELO
        home_team = match_table.loc[match_num, 'Home']
        home_elo = int(group_table.loc[home_team, 'Elo'])

        #initialize away team and ELO
        away_team = match_table.loc[match_num, 'Away']
        away_elo = int(group_table.loc[away_team, 'Elo'])

        #calculate We for new ELO calc
        home_we = calculate_neutral_We(home_elo, away_elo)
        away_we = calculate_neutral_We(away_elo, home_elo)
    
    
    return home_team, home_we, home_elo, away_team, away_we, away_elo

def calc_match_We(match_table, match_num, group_table):

    #initialize home team and ELO
    home_team = match_table.loc[match_num, 'Home']
    home_elo = int(group_table.loc[home_team, 'Elo'])

    #initialize away team and ELO
    away_team = match_table.loc[match_num, 'Away']
    away_elo = int(group_table.loc[away_team, 'Elo'])

    #calculate We for new ELO calc
    home_we = calculate_We(home_elo, away_elo, 'home')
    away_we = calculate_We(away_elo, home_elo, 'away')
    
    
    return home_team, home_we, home_elo, away_team, away_we, away_elo

def calc_match_We_w_FIFA(match_table, match_num, group_table):

    #initialize home team and ELO
    home_team = match_table.loc[match_num, 'Home']
    home_elo = int(group_table.loc[home_team, 'Elo'])
    home_FIFA = int(group_table.loc[home_team, 'FIFA'])

    #initialize away team and ELO
    away_team = match_table.loc[match_num, 'Away']
    away_elo = int(group_table.loc[away_team, 'Elo'])
    away_FIFA = int(group_table.loc[away_team, 'FIFA'])
    
    #calculate We for new ELO calc
    home_we = calculate_We(home_elo, away_elo, 'home')
    away_we = calculate_We(away_elo, home_elo, 'away')
    
    #calculate FIFA We for FIFA rankings
    home_FIFA_we = calculate_FIFA_We(home_FIFA, away_FIFA)
    away_FIFA_we = calculate_FIFA_We(away_FIFA, home_FIFA)
    
    
    return home_team, home_we, home_elo, away_team, away_we, away_elo, home_FIFA, away_FIFA, home_FIFA_we, away_FIFA_we



def play_gs_match_neutral(group_table, home_team, home_we, home_elo, home_wp, 
                          away_team, away_we, away_elo, away_wp, draw_wp):
    
    #randomly determine match outcome using weighted probabilities
    outcome = outcome_generator(home_wp, away_wp, draw_wp)

    #home win
    if outcome == 1:

        #update table
        group_table.loc[home_team, 'Points'] += 3
        group_table.loc[away_team, 'Points'] += 0

        #new home elo
        new_home_elo = calculate_elo(home_elo, home_we, outcome, 1, 50)

        group_table.loc[home_team, 'Elo'] = new_home_elo

        #new away elo
        new_away_elo = calculate_elo(away_elo, away_we, 0, 1, 50)

        group_table.loc[away_team, 'Elo'] = new_away_elo

    elif outcome == 0.5:

        #update table
        group_table.loc[home_team, 'Points'] += 1
        group_table.loc[away_team, 'Points'] += 1

        #new home elo
        new_home_elo = calculate_elo(home_elo, home_we, outcome, 0, 50)

        group_table.loc[home_team, 'Elo'] = new_home_elo

        #new away elo
        new_away_elo = calculate_elo(away_elo, away_we, outcome, 0, 50)

        group_table.loc[away_team, 'Elo'] = new_away_elo

    #away win
    else:

        #update table
        group_table.loc[home_team, 'Points'] += 0
        group_table.loc[away_team, 'Points'] += 3

        #new home elo
        new_home_elo = calculate_elo(home_elo, home_we, 0, 1, 50)

        group_table.loc[home_team, 'Elo'] = new_home_elo

        #new away elo
        new_away_elo = calculate_elo(away_elo, away_we, outcome, 1, 50)

        group_table.loc[away_team, 'Elo'] = new_away_elo
        
    
    return group_table


def play_ko_match_neutral(group_table, match_table, match_num,
                          home_team, home_we, home_elo, home_wp, 
                          away_team, away_we, away_elo, away_wp, draw_wp):    
    
    #randomly determine match outcome using weighted probabilities
    outcome = outcome_generator(home_wp, away_wp, draw_wp)

    #home win
    if outcome == 1:

        #append win
        match_table.loc[match_num, 'Winner'] = home_team

        #new home elo
        new_home_elo = calculate_elo(home_elo, home_we, 1, 1, 50)

        group_table.loc[home_team, 'Elo'] = new_home_elo

        #new away elo
        new_away_elo = calculate_elo(away_elo, away_we, 0, 1, 50)

        group_table.loc[away_team, 'Elo'] = new_away_elo
            

    elif outcome == 0.5:

        #Choose a random winner
        win = random.choice([home_team, away_team])

        #append win
        match_table.loc[match_num, 'Winner'] = win

        #new home elo
        new_home_elo = calculate_elo(home_elo, home_we, 0.5, 0, 50)

        group_table.loc[home_team, 'Elo'] = new_home_elo

        #new away elo
        new_away_elo = calculate_elo(away_elo, away_we, 0.5, 0, 50)

        group_table.loc[away_team, 'Elo'] = new_away_elo

    #away win
    else:

        #update table
        match_table.loc[match_num, 'Winner'] = away_team

        #new home elo
        new_home_elo = calculate_elo(home_elo, home_we, 0, 1, 50)

        group_table.loc[home_team, 'Elo'] = new_home_elo

        #new away elo
        new_away_elo = calculate_elo(away_elo, away_we, 1, 1, 50)

        group_table.loc[away_team, 'Elo'] = new_away_elo
        
    return group_table, match_table

def play_ko_match_w_FIFA(group_table, match_table, match_num,
                          home_team, home_we, home_elo, home_wp, home_FIFA_we,
                          home_FIFA, away_team, away_we, away_elo, away_wp, 
                          away_FIFA_we, away_FIFA, draw_wp, FIFA_KM=25, 
                          Elo_KM = 50):    
    
    #randomly determine match outcome using weighted probabilities
    outcome = outcome_generator(home_wp, away_wp, draw_wp)

    #home win
    if outcome == 1:

        #append win
        match_table.loc[match_num, 'Winner'] = home_team

        #new home elo
        new_home_elo = calculate_elo(home_elo, home_we, 1, 1, Elo_KM)

        group_table.loc[home_team, 'Elo'] = new_home_elo
        
        #new home FIFA ranking
        
        new_home_FIFA = calculate_FIFA(home_FIFA, home_FIFA_we, 1, FIFA_KM)

        group_table.loc[home_team, 'FIFA'] = new_home_FIFA

        #new away elo
        new_away_elo = calculate_elo(away_elo, away_we, 0, 1, Elo_KM)

        group_table.loc[away_team, 'Elo'] = new_away_elo
        
        #new away FIFA ranking
        
        new_away_FIFA = calculate_FIFA(away_FIFA, away_FIFA_we, 0, FIFA_KM)

        group_table.loc[away_team, 'FIFA'] = new_away_FIFA
            

    elif outcome == 0.5:

        #Choose a random winner
        win = random.choice([home_team, away_team])

        #append win
        match_table.loc[match_num, 'Winner'] = win

        #new home elo
        new_home_elo = calculate_elo(home_elo, home_we, 0.5, 0, Elo_KM)

        group_table.loc[home_team, 'Elo'] = new_home_elo
        
        #new home FIFA ranking
        
        new_home_FIFA = calculate_FIFA(home_FIFA, home_FIFA_we, 0.5, FIFA_KM)

        group_table.loc[home_team, 'FIFA'] = new_home_FIFA

        #new away elo
        new_away_elo = calculate_elo(away_elo, away_we, 0.5, 0, Elo_KM)

        group_table.loc[away_team, 'Elo'] = new_away_elo
        
        #new away FIFA ranking
        
        new_away_FIFA = calculate_FIFA(away_FIFA, away_FIFA_we, 0.5, FIFA_KM)

        group_table.loc[away_team, 'FIFA'] = new_away_FIFA

    #away win
    else:

        #update table
        match_table.loc[match_num, 'Winner'] = away_team

        #new home elo
        new_home_elo = calculate_elo(home_elo, home_we, 0, 1, Elo_KM)

        group_table.loc[home_team, 'Elo'] = new_home_elo
        
        #new home FIFA ranking
        
        new_home_FIFA = calculate_FIFA(home_FIFA, home_FIFA_we, 0, FIFA_KM)

        group_table.loc[home_team, 'FIFA'] = new_home_FIFA

        #new away elo
        new_away_elo = calculate_elo(away_elo, away_we, 1, 1, Elo_KM)

        group_table.loc[away_team, 'Elo'] = new_away_elo
        
        new_away_FIFA = calculate_FIFA(away_FIFA, away_FIFA_we, 1, FIFA_KM)

        group_table.loc[away_team, 'FIFA'] = new_away_FIFA
        
    return group_table, match_table