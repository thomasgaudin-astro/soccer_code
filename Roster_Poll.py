#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 10:14:36 2023

@author: thomasgaudin
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import unidecode
import matplotlib.pylab as pl



def series_to_dict(position):
    """Take a series from dataframe and convert to new series with responses split by player."""
    
    #new dictionary
    pos = dict()
    
    for val in range(0, len(position)):
        #split response at each comma
        players = position.index[val].split(', ')
        
        #append each player to dictionary pos and count how many times they appear
        for num in range(0, len(players)):
            if players[num] not in pos:
                pos[players[num]] = position.values[val]
            else:
                pos[players[num]] += position.values[val]
    
    #convert each dictionary to series
    pos = pd.Series(pos)
            
    return pos


def sheet_to_dict(month_url):
    """Turn Google Sheets URL into Pandas Dataframe"""
    
    #replace backend of url with proper text
    url_month = month_url.replace('/edit?usp=sharing', '/export?format=csv')
    
    #read the csv, rename the columns to be 0-21
    all_resp = pd.read_csv(url_month)
    resps = all_resp.rename(columns={x:y for x,y in zip(all_resp.columns,range(0,len(all_resp.columns)))})
    
    #number of responses
    resp_nums = len(resps[0])
    
    return resps, resp_nums


def position_counts(responses, response_nums):
    """Count frequency of responses at each position and then normalize"""
    
    #count occurrence of each player at a position
    pos_counts = responses.value_counts()
    #turn the counts into a series
    pos_series = series_to_dict(pos_counts).sort_values(ascending=True)
    
    #normalize counts
    norm_pos_counts = pos_counts / len(pd.Series(responses).dropna())
    #turn into series
    norm_pos_series = series_to_dict(norm_pos_counts)
    
    #take index and values for series
    pos_index = pos_series.index
    pos_vals = pos_series.values
    
    return pos_series, norm_pos_series, pos_index, pos_vals

def position_counts_2cols(responses1, responses2, response_nums):
    """Count frequency of responses at each position and then normalize"""
    
    #count occurrence of each player at a position
    pos_counts1 = responses1.value_counts()
    pos_counts2 = responses2.value_counts()
    
    pos_counts = pos_counts1.add(pos_counts2, fill_value=0).sort_values(ascending=True)
    
    #turn the counts into a series
    pos_series1 = series_to_dict(pos_counts1)
    pos_series2 = series_to_dict(pos_counts2)
    
    #join two series
    pos_series = pos_series1.add(pos_series2, fill_value=0).sort_values(ascending=True)
    
    #normalize counts
    norm_pos_counts = pos_counts / response_nums
    #turn into series
    norm_pos_series = series_to_dict(norm_pos_counts)
    
    #take index and values for series
    pos_index = pos_series.index
    pos_vals = pos_series.values
    
    return pos_series, norm_pos_series, pos_index, pos_vals


def plot_histograms(month, gk_index, gk_vals, rb_index, rb_vals, lb_index, lb_vals,
                       cb_index, cb_vals, cdm_index, cdm_vals, cm_index, cm_vals, 
                       cam_index, cam_vals, wing_index, wing_vals, st_index, st_vals):
    """Take all position selection data and make a histogram"""
    
    
    fig, ax = plt.subplots(3, 3, figsize = (24,20), sharex = True, facecolor='mediumblue')

    ax[0][0].barh(gk_index, gk_vals, color = 'firebrick')
    ax[0][0].set_title('Goalkeepers', color='white', fontweight='heavy', fontsize=20)
    ax[0][0].tick_params(axis='both', labelcolor='white', labelsize=13)

    ax[0][1].barh(rb_index, rb_vals, color = 'firebrick')
    ax[0][1].set_title('Right Backs', color='white', fontweight='heavy', fontsize=20)
    ax[0][1].tick_params(axis='both', labelcolor='white', labelsize=13)

    ax[0][2].barh(lb_index, lb_vals, color = 'firebrick')
    ax[0][2].set_title('Left Backs', color='white', fontweight='heavy', fontsize=20)
    ax[0][2].tick_params(axis='both', labelcolor='white', labelsize=13)

    ax[1][0].barh(cb_index, cb_vals, color = 'firebrick')
    ax[1][0].set_title('Centerbacks', color='white', fontweight='heavy', fontsize=20)
    ax[1][0].tick_params(axis='both', labelcolor='white', labelsize=13)

    ax[1][1].barh(cdm_index, cdm_vals, color = 'firebrick')
    ax[1][1].set_title('Defensive Midfielders', color='white', fontweight='heavy', fontsize=20)
    ax[1][1].tick_params(axis='both', labelcolor='white', labelsize=13)

    ax[1][2].barh(cm_index, cm_vals, color = 'firebrick')
    ax[1][2].set_title('Center Midfielders', color='white', fontweight='heavy', fontsize=20)
    ax[1][2].tick_params(axis='both', labelcolor='white', labelsize=13)
    
    ax[2][0].barh(cam_index, cam_vals, color = 'firebrick')
    ax[2][0].set_title('Attacking Midfielders', color='white', fontweight='heavy', fontsize=20)
    ax[2][0].set_xlabel('Number of Votes', fontsize=15, color='white')
    ax[2][0].tick_params(axis='both', labelcolor='white', labelsize=13)

    ax[2][1].barh(wing_index, wing_vals, color = 'firebrick')
    ax[2][1].set_title('Wingers', color='white', fontweight='heavy', fontsize=20)
    ax[2][1].set_xlabel('Number of Votes', fontsize=15, color='white')
    ax[2][1].tick_params(axis='both', labelcolor='white', labelsize=13)

    ax[2][2].barh(st_index, st_vals, color = 'firebrick')
    ax[2][2].set_title('Strikers', color='white', fontweight='heavy', fontsize=20)
    ax[2][2].set_xlabel('Number of Votes', fontsize=15, color='white')
    ax[2][2].tick_params(axis='both', labelcolor='white', labelsize=13)

    fig.tight_layout(w_pad=1.3)
    plt.suptitle(f'{month} Roster Selection Frequencies', x=0.5, y=0.97, color='white', fontsize=36, fontweight='heavy')
    plt.subplots_adjust(top=0.9)
    plt.savefig(f'{month}_roster.png')
    plt.show()


def norm_pos(pos_dict):
    """Combines monthly roster data for a position and normalizes the data"""
    
    #join all months data together
    concat_pos = pd.concat(pos_dict, axis=1)
    
    #fill NaNs with zeros
    norm_pos = concat_pos.fillna(0)
    
    return norm_pos


def plot_time_series(norm_keepers, len_nk, norm_right_backs, len_nrb, norm_left_backs,
                    len_nlb, norm_centerbacks, len_ncb, norm_def_mids, len_ndm,
                    norm_cent_mids, len_ncm, norm_atk_mids, len_nam, 
                    norm_wingers, len_nw, norm_strikers, len_ns):
    """Take normalized month-by-month selection frequency and create a line chart to show selection 
    changes over time"""
    
    fig, axes = plt.subplots(5, 2, figsize = (24,24), sharex = True)

    norm_keepers.T.plot.line(ax=axes[0,0], 
                             color = pl.cm.gist_rainbow(np.random.rand(len_nk,)), 
                             style = 'o-', lw=4)
    axes[0][0].legend(ncol=2, fontsize=12, bbox_to_anchor=(1.0, 1.0))
    axes[0][0].set_title('Goalkeepers', fontweight='heavy', fontsize=30)
    axes[0][0].set_facecolor('darkgray')

    norm_right_backs.T.plot.line(ax=axes[0,1], 
                             color = pl.cm.gist_rainbow(np.random.rand(len_nrb,)), 
                             style = 'o-', lw=4)
    axes[0][1].legend(ncol=2, fontsize=12, bbox_to_anchor=(1.0, 1.0))
    axes[0][1].set_title('Right Backs', fontweight='heavy', fontsize=30)
    axes[0][1].set_facecolor('darkgray')

    norm_left_backs.T.plot.line(ax=axes[1,0], 
                             color = pl.cm.gist_rainbow(np.random.rand(len_nlb,)), 
                             style = 'o-', lw=4)
    axes[1][0].legend(ncol=2, fontsize=12, bbox_to_anchor=(1.0, 1.0))
    axes[1][0].set_title('Left Backs', fontweight='heavy', fontsize=30)
    axes[1][0].set_facecolor('darkgray')

    norm_centerbacks.T.plot.line(ax=axes[1,1], 
                             color = pl.cm.gist_rainbow(np.random.rand(len_ncb,)), 
                             style = 'o-', lw=4)
    axes[1][1].legend(ncol=2, fontsize=12, bbox_to_anchor=(1.0, 1.0))
    axes[1][1].set_title('Centerbacks', fontweight='heavy', fontsize=30)
    axes[1][1].set_facecolor('darkgray')

    norm_def_mids.T.plot.line(ax=axes[2,0], 
                             color = pl.cm.gist_rainbow(np.random.rand(len_ndm,)), 
                             style = 'o-', lw=4)
    axes[2][0].legend(ncol=2, fontsize=12, bbox_to_anchor=(1.0, 1.0))
    axes[2][0].set_title('Defensive Midfielders', fontweight='heavy', fontsize=30)
    axes[2][0].set_facecolor('darkgray')

    norm_cent_mids.T.plot.line(ax=axes[2,1], 
                             color = pl.cm.gist_rainbow(np.random.rand(len_ncm,)), 
                             style = 'o-', lw=4)
    axes[2][1].legend(ncol=2, fontsize=12, bbox_to_anchor=(1.0, 1.0))
    axes[2][1].set_title('Central Midfielders', fontweight='heavy', fontsize=30)
    axes[2][1].set_facecolor('darkgray')
    
    norm_atk_mids.T.plot.line(ax=axes[3,0], 
                             color = pl.cm.gist_rainbow(np.random.rand(len_nam,)), 
                             style = 'o-', lw=4)
    axes[3][0].legend(ncol=2, fontsize=12, bbox_to_anchor=(1.0, 1.0))
    axes[3][0].set_title('Attacking Midfielders', fontweight='heavy', fontsize=30)
    axes[3][0].set_facecolor('darkgray')

    norm_wingers.T.plot.line(ax=axes[3,1], 
                             color = pl.cm.gist_rainbow(np.random.rand(len_nw,)), 
                             style = 'o-', lw=4)
    axes[3][1].legend(ncol=2, fontsize=12, bbox_to_anchor=(1.0, 1.0))
    axes[3][1].set_title('Wingers', fontweight='heavy', fontsize=30)
    #axes[3][0].set_xticks(fontsize=14)
    axes[3][1].set_facecolor('darkgray')

    norm_strikers.T.plot.line(ax=axes[4,0], 
                             color = pl.cm.gist_rainbow(np.random.rand(len_ns,)), 
                             style = 'o-', lw=4)
    axes[4][0].legend(ncol=2, fontsize=12, bbox_to_anchor=(1.0, 1.0))
    axes[4][0].set_title('Strikers', fontweight='heavy', fontsize=30)
    #axes[3][1].set_xticks(fontsize=14)
    axes[4][0].set_facecolor('darkgray')
    
    axes[4][1].axis('off')

    fig.tight_layout(w_pad=1.8)
    plt.suptitle('Roster Selection Percentages Over Time', y=0.97, fontsize=40, fontweight='heavy')
    plt.subplots_adjust(top=0.9)
    plt.savefig('roster_trends.png')
    plt.show()


def gk_starter_counts(gk_starts, gk_counts, player_mistakes): 
    """Translate raw gk starter data into a pandas series of counts"""
    
    for starter, count in zip(gk_starts.index, gk_starts.values):
        starter = unidecode.unidecode(starter.strip())
        if set(starter.split()).issubset(player_mistakes['Matt Turner']):
            gk_counts['Matt Turner'] += count
        elif set(starter.split()).issubset(player_mistakes['Ethan Horvath']):
            gk_counts['Ethan Horvath'] += count
        elif set(starter.split()).issubset(player_mistakes['Zack Steffen']):
            gk_counts['Zack Steffen'] += count   
        elif set(starter.split()).issubset(player_mistakes['Gabriel Slonina']):
            gk_counts['Gabriel Slonina'] += count
        elif set(starter.split()).issubset(player_mistakes['Roman Celentano']):
            gk_counts['Roman Celentano'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Unknown'])):
            gk_counts['Unknown'] += count
            
        
    gk_counts = pd.Series(gk_counts)
    gk_counts = gk_counts[gk_counts!=0]
    
    return gk_counts


def rb_starter_counts(rb_starts, rb_counts, player_mistakes): 
    """Translate raw rb starter data into a pandas series of counts"""    
    
    for starter, count in zip(rb_starts.index, rb_starts.values):
        starter = unidecode.unidecode(starter.strip())
        if set(starter.split()).issubset(set(player_mistakes['Sergino Dest'])):
            rb_counts['Sergino Dest'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Reggie Cannon'])):
            rb_counts['Reggie Cannon'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Joe Scally'])):
            rb_counts['Joe Scally'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Bryan Reynolds'])):
            rb_counts['Bryan Reynolds'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Tim Weah'])):
            rb_counts['Tim Weah'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Unknown'])):
            rb_counts['Unknown'] += count
        
    rb_counts = pd.Series(rb_counts)
    rb_counts = rb_counts[rb_counts!=0]
    
    return rb_counts


def lb_starter_counts(lb_starts, lb_counts, player_mistakes): 
    """Translate raw lb starter data into a pandas series of counts"""
    
    for starter, count in zip(lb_starts.index, lb_starts.values):
        starter = unidecode.unidecode(starter.strip())
        if set(starter.split()).issubset(set(player_mistakes['Antonee Robinson'])):
            lb_counts['Antonee Robinson'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Kevin Paredes'])):
            lb_counts['Kevin Paredes'] += count
        elif set(starter.split()).issubset(set(player_mistakes['John Tolkin'])):
            lb_counts['John Tolkin'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Caleb Wiley'])):
            lb_counts['Caleb Wiley'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Sergino Dest'])):
            lb_counts['Sergino Dest'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Joe Scally'])):
            lb_counts['Joe Scally'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Tim Weah'])):
            lb_counts['Tim Weah'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Jonathan Gomez'])):
            lb_counts['Jonathan Gomez'] += count
        elif set(starter.split()).issubset(set(player_mistakes['George Bello'])):
            lb_counts['George Bello'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Unknown'])):
            lb_counts['Unknown'] += count

    lb_counts = pd.Series(lb_counts)
    lb_counts = lb_counts[lb_counts!=0]
    
    return lb_counts


def cb_starter_counts(cb_starts, cb_counts, player_mistakes): 
    """Translate raw cb starter data into a pandas series of counts"""    
    
    for starter, count in zip(cb_starts.index, cb_starts.values):
        if set(starter.split()).issubset(set(player_mistakes['Chris Richards'])):
            cb_counts['Chris Richards'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Walker Zimmerman'])):
            cb_counts['Walker Zimmerman'] += count
        elif set(starter.split()).issubset(set(player_mistakes['John Brooks'])):
            cb_counts['John Brooks'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Cameron Carter-Vickers'])):
            cb_counts['Cameron Carter-Vickers'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Tyler Adams'])):
            cb_counts['Tyler Adams'] += count    
        elif set(starter.split()).issubset(set(player_mistakes['Tim Ream'])):
            cb_counts['Tim Ream'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Miles Robinson'])):
            cb_counts['Miles Robinson'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Mark McKenzie'])):
            cb_counts['Mark McKenzie'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Matt Miazga'])):
            cb_counts['Matt Miazga'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Justin Che'])):
            cb_counts['Justin Che'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Auston Trusty'])):
            cb_counts['Auston Trusty'] += count
        elif set(starter.split()).issubset(set(player_mistakes['James Sands'])):
            cb_counts['James Sands'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Erik Palmer-Brown'])):
            cb_counts['Erik Palmer-Brown'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Jalen Neal'])):
            cb_counts['Jalen Neal'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Reggie Cannon'])):
            cb_counts['Reggie Cannon'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Joshua Wynder'])):
            cb_counts['Joshua Wynder'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Aaron Long'])):
            cb_counts['Aaron Long'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Antonee Robinson'])):
            cb_counts['Antonee Robinson'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Unknown'])):
            cb_counts['Unknown'] += count
            
    cb_counts = pd.Series(cb_counts)
    cb_counts = cb_counts[cb_counts!=0]
    
    return cb_counts


def cdm_starter_counts(cdm_starts, cdm_counts, player_mistakes): 
    """Translate raw cdm starter data into a pandas series of counts"""    

    for starter, count in zip(cdm_starts.index, cdm_starts.values):
        if set(starter.split()).issubset(set(player_mistakes['Tyler Adams'])):
            cdm_counts['Tyler Adams'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Weston McKennie'])):
            cdm_counts['Weston McKennie'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Obed Vargas'])):
            cdm_counts['Obed Vargas'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Kellyn Acosta'])):
            cdm_counts['Kellyn Acosta'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Johnny Cardoso'])):
            cdm_counts['Johnny Cardoso'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Tanner Tessman'])):
            cdm_counts['Tanner Tessman'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Yunus Musah'])):
            cdm_counts['Yunus Musah'] += count
        
    cdm_counts = pd.Series(cdm_counts)
    cdm_counts = cdm_counts[cdm_counts!=0]
    
    return cdm_counts

def cam_starter_counts(cam_starts, cam_counts, player_mistakes): 
    """Translate raw cdm starter data into a pandas series of counts"""    

    for starter, count in zip(cam_starts.index, cam_starts.values):
        if set(starter.split()).issubset(set(player_mistakes['Gio Reyna'])):
            cam_counts['Gio Reyna'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Brendan Aaronson'])):
            cam_counts['Brendan Aaronson'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Malik Tillman'])):
            cam_counts['Malik Tillman'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Tyler Adams'])):
            cam_counts['Tyler Adams'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Unknown'])):
            cam_counts['Unknown'] += count
    cam_counts = pd.Series(cam_counts)
    cam_counts = cam_counts[cam_counts!=0]
    
    return cam_counts

def cm_starter_counts(cm_starts, cm_counts, player_mistakes): 
    """Translate raw cm starter data into a pandas series of counts"""    
    
    for starter, count in zip(cm_starts.index, cm_starts.values):
        if set(starter.split()).issubset(set(player_mistakes['Weston McKennie'])):
            cm_counts['Weston McKennie'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Yunus Musah'])):
            cm_counts['Yunus Musah'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Gio Reyna'])):
            cm_counts['Gio Reyna'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Brendan Aaronson'])):
            cm_counts['Brendan Aaronson'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Alejandro Zendejas'])):
            cm_counts['Alejandro Zendejas'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Luca de la Torre'])):
            cm_counts['Luca de la Torre'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Paxten Aaronson'])):
            cm_counts['Paxten Aaronson'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Alex Mendez'])):
            cm_counts['Alex Mendez'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Taylor Booth'])):
            cm_counts['Taylor Booth'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Keaton Parks'])):
            cm_counts['Keaton Parks'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Richie Ledezma'])):
            cm_counts['Richie Ledezma'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Malik Tillman'])):
            cm_counts['Malik Tillman'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Tyler Adams'])):
            cm_counts['Tyler Adams'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Djordje Mihailovic'])):
            cm_counts['Djordje Mihailovic'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Tim Tillman'])):
            cm_counts['Tim Tillman'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Unknown'])):
            cm_counts['Unknown'] += count

    cm_counts = pd.Series(cm_counts)
    cm_counts = cm_counts[cm_counts!=0]
    
    return cm_counts


def wing_starter_counts(wing_starts, wing_counts, player_mistakes):
    """Translate raw wing starter data into a pandas series of counts"""    

    for starter, count in zip(wing_starts.index, wing_starts.values):
        if set(starter.split()).issubset(set(player_mistakes['Christian Pulisic'])):
            wing_counts['Christian Pulisic'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Tim Weah'])):
            wing_counts['Tim Weah'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Gio Reyna'])):
            wing_counts['Gio Reyna'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Brendan Aaronson'])):
            wing_counts['Brendan Aaronson'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Alejandro Zendejas'])):
            wing_counts['Alejandro Zendejas'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Taylor Booth'])):
            wing_counts['Taylor Booth'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Kevin Paredes'])):
            wing_counts['Kevin Paredes'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Malik Tillman'])):
            wing_counts['Malik Tillman'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Matthew Hoppe'])):
            wing_counts['Matthew Hoppe'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Quinn Sullivan'])):
            wing_counts['Quinn Sullivan'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Paul Arriola'])):
            wing_counts['Paul Arriola'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Caden Clark'])):
            wing_counts['Caden Clark'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Sergino Dest'])):
            wing_counts['Sergino Dest'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Josh Sargent'])):
            wing_counts['Josh Sargent'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Unknown'])):
            wing_counts['Unknown'] += count

    wing_counts = pd.Series(wing_counts)
    wing_counts = wing_counts[wing_counts!=0]
    
    return wing_counts


def st_starter_counts(st_starts, st_counts, player_mistakes):
    """Translate raw st starter data into a pandas series of counts""" 

    for starter, count in zip(st_starts.index, st_starts.values):
        starter = unidecode.unidecode(starter.strip())
        if set(starter.split()).issubset(set(player_mistakes['Jesus Ferreira'])):
            st_counts['Jesus Ferreira'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Gio Reyna'])):
            st_counts['Gio Reyna'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Ricardo Pepi'])):
            st_counts['Ricardo Pepi'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Jordan Pefok'])):
            st_counts['Jordan Pefok'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Daryl Dike'])):
            st_counts['Daryl Dike'] += count 
        elif set(starter.split()).issubset(set(player_mistakes['Josh Sargent'])):
            st_counts['Josh Sargent'] += count 
        elif set(starter.split()).issubset(set(player_mistakes['Brandon Vazquez'])):
            st_counts['Brandon Vazquez'] += count 
        elif set(starter.split()).issubset(set(player_mistakes['Folarin Balogun'])):
            st_counts['Folarin Balogun'] += count 
        elif set(starter.split()).issubset(set(player_mistakes['Cade Cowell'])):
            st_counts['Cade Cowell'] += count 
        elif set(starter.split()).issubset(set(player_mistakes['Gyasi Zardes'])):
            st_counts['Gyasi Zardes'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Malik Tillman'])):
            st_counts['Malik Tillman'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Tim Weah'])):
            st_counts['Tim Weah'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Matthew Hoppe'])):
            st_counts['Matthew Hoppe'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Unknown'])):
            st_counts['Unknown'] += count

    st_counts = pd.Series(st_counts)
    st_counts = st_counts[st_counts!=0]
    
    return st_counts

def my_autopct(pct):
    return ('%.2f' % pct) if pct > 3.0 else ''


def plot_starter_pies(month, gk_count, rb_count, lb_count, lcb_count,
                     rcb_count, cdm_count, lcm_count, rcm_count, cam_count,
                     lw_count, rw_count, st_count):
    "Plots pie charts representing the percentage of selections starting a player"
    
    circle1 = plt.Circle((0,0),0.65,color='grey', fc='white', linewidth=1.00)
    circle2 = plt.Circle((0,0),0.65,color='grey', fc='white', linewidth=1.00)
    circle3 = plt.Circle((0,0),0.65,color='grey', fc='white', linewidth=1.00)
    circle4 = plt.Circle((0,0),0.65,color='grey', fc='white', linewidth=1.00)
    circle5 = plt.Circle((0,0),0.65,color='grey', fc='white', linewidth=1.00)
    circle6 = plt.Circle((0,0),0.65,color='grey', fc='white', linewidth=1.00)
    circle7 = plt.Circle((0,0),0.65,color='grey', fc='white', linewidth=1.00)
    circle8 = plt.Circle((0,0),0.65,color='grey', fc='white', linewidth=1.00)
    circle9 = plt.Circle((0,0),0.65,color='grey', fc='white', linewidth=1.00)
    circle10 = plt.Circle((0,0),0.65,color='grey', fc='white', linewidth=1.00)
    circle11 = plt.Circle((0,0),0.65,color='grey', fc='white', linewidth=1.00)
    circle12 = plt.Circle((0,0),0.65,color='grey', fc='white', linewidth=1.00)

    fig, ax = plt.subplots(6, 2, figsize = (14, 20))

    ax[0][0].pie(gk_count.values, 
             colors = pl.cm.jet(np.linspace(0, 1, len(gk_count))),
             autopct=my_autopct,
             pctdistance=1.34,
             textprops = {'fontsize':12, 'color':'black'}, 
             wedgeprops={'linewidth': 3.0, 'edgecolor': 'white'},
             rotatelabels=False)
    ax[0][0].add_patch(circle1)
    ax[0][0].legend(gk_count.index, bbox_to_anchor=(1.0, 1.0), fontsize=12)
    ax[0][0].set_title('Goalkeeper', fontweight='heavy', fontsize=20)


    ax[0][1].pie(rb_count.values, 
             colors = pl.cm.jet(np.linspace(0, 1, len(rb_count))), 
             autopct=my_autopct,
             pctdistance=1.31,
             startangle=20,
             textprops = {'fontsize':12, 'color':'black'},
             wedgeprops={'linewidth': 3.0, 'edgecolor': 'white'})
    ax[0][1].add_patch(circle2)
    ax[0][1].legend(rb_count.index, bbox_to_anchor=(1.1, 1.0), fontsize=12)
    ax[0][1].set_title('Right Back', fontweight='heavy', fontsize=20)

    ax[1][0].pie(lb_count.values,  
             colors = pl.cm.jet(np.linspace(0, 1, len(lb_count))), 
             autopct=my_autopct,
             pctdistance=1.31,
             startangle=-10,
             textprops = {'fontsize':12, 'color':'black'},
             wedgeprops={'linewidth': 3.0, 'edgecolor': 'white'})
    ax[1][0].add_patch(circle3)
    ax[1][0].legend(lb_count.index, bbox_to_anchor=(1.0, 1.0), fontsize=12)
    ax[1][0].set_title('Left Back', fontweight='heavy', fontsize=20)

    ax[1][1].pie(lcb_count.values,
             colors = pl.cm.jet(np.linspace(0, 1, len(lcb_count))), 
             autopct=my_autopct,
             pctdistance=1.27,
             startangle=70,
             textprops = {'fontsize':12, 'color':'black'},
             wedgeprops={'linewidth': 3.0, 'edgecolor': 'white'})
    ax[1][1].add_patch(circle4)
    ax[1][1].legend(lcb_count.index, bbox_to_anchor=(1.1, 1.0), fontsize=12)
    ax[1][1].set_title('Left Centerback', fontweight='heavy', fontsize=20)

    ax[2][0].pie(rcb_count.values,
             colors = pl.cm.jet(np.linspace(0, 1, len(rcb_count))),
             autopct=my_autopct,
             pctdistance=1.24,
             startangle=-5,
             textprops = {'fontsize':12, 'color':'black'},
             wedgeprops={'linewidth': 3.0, 'edgecolor': 'white'})
    ax[2][0].add_patch(circle5)
    ax[2][0].legend(rcb_count.index, bbox_to_anchor=(1.0, 1.0), fontsize=12)
    ax[2][0].set_title('Right Centerback', fontweight='heavy', fontsize=20)

    ax[2][1].pie(cdm_count.values,
             colors = pl.cm.jet(np.linspace(0, 1, len(cdm_count))), 
             autopct=my_autopct,
             pctdistance=1.31,
             textprops = {'fontsize':12, 'color':'black'},
             wedgeprops={'linewidth': 3.0, 'edgecolor': 'white'})
    ax[2][1].add_patch(circle6)
    ax[2][1].legend(cdm_count.index, bbox_to_anchor=(1.1, 1.0), fontsize=12)
    ax[2][1].set_title('Defensive Midfielder', fontweight='heavy', fontsize=20)

    ax[3][0].pie(lcm_count.values,
             colors = pl.cm.jet(np.linspace(0, 1, len(lcm_count))), 
             autopct=my_autopct,
             pctdistance=1.31,
             startangle=-20,
             textprops = {'fontsize':12, 'color':'black'},
             wedgeprops={'linewidth': 3.0, 'edgecolor': 'white'})
    ax[3][0].add_patch(circle7)
    ax[3][0].legend(lcm_count.index, bbox_to_anchor=(1.0, 1.0), fontsize=12)
    ax[3][0].set_title('Left Center Mid', fontweight='heavy', fontsize=20)

    ax[3][1].pie(rcm_count.values,
             colors = pl.cm.jet(np.linspace(0, 1, len(rcm_count))), 
             autopct=my_autopct,
             pctdistance=1.31,
             startangle=-40,
             textprops = {'fontsize':12, 'color':'black'},
             wedgeprops={'linewidth': 3.0, 'edgecolor': 'white'})
    ax[3][1].add_patch(circle8)
    ax[3][1].legend(rcm_count.index, bbox_to_anchor=(1.1, 1.0), fontsize=12)
    ax[3][1].set_title('Right Center Mid', fontweight='heavy', fontsize=20)
    
    ax[4][0].pie(cam_count.values,
             colors = pl.cm.jet(np.linspace(0, 1, len(cam_count))), 
             autopct=my_autopct,
             pctdistance=1.31,
             textprops = {'fontsize':12, 'color':'black'},
             wedgeprops={'linewidth': 3.0, 'edgecolor': 'white'})
    ax[4][0].add_patch(circle9)
    ax[4][0].legend(cam_count.index, bbox_to_anchor=(1.1, 1.0), fontsize=12)
    ax[4][0].set_title('Attacking Midfielder', fontweight='heavy', fontsize=20)

    ax[4][1].pie(lw_count.values, 
             colors = pl.cm.jet(np.linspace(0, 1, len(lw_count))),
             autopct=my_autopct,
             pctdistance=1.31,
             textprops = {'fontsize':12, 'color':'black'},
             wedgeprops={'linewidth': 3.0, 'edgecolor': 'white'})
    ax[4][1].add_patch(circle10)
    ax[4][1].legend(lw_count.index, bbox_to_anchor=(1.0, 1.0), fontsize=12)
    ax[4][1].set_title('Left Wing', fontweight='heavy', fontsize=20)

    ax[5][0].pie(rw_count.values,
             colors = pl.cm.jet(np.linspace(0, 1, len(rw_count))), 
             autopct=my_autopct,
             pctdistance=1.31,
             startangle=40,
             textprops = {'fontsize':12, 'color':'black'},
             wedgeprops={'linewidth': 3.0, 'edgecolor': 'white'})
    ax[5][0].add_patch(circle11)
    ax[5][0].legend(rw_count.index, bbox_to_anchor=(1.1, 1.0), fontsize=12)
    ax[5][0].set_title('Right Wing', fontweight='heavy', fontsize=20)

    ax[5][1].pie(st_count.values, 
             colors = pl.cm.jet(np.linspace(0, 1, len(st_count))), 
             autopct=my_autopct,
             pctdistance=1.31,
             startangle=90,
             textprops = {'fontsize':12, 'color':'black'},
             wedgeprops={'linewidth': 3.0, 'edgecolor': 'white'})
    ax[5][1].add_patch(circle12)
    ax[5][1].legend(st_count.index, bbox_to_anchor=(1.0, 1.0), fontsize=12)
    ax[5][1].set_title('Striker', fontweight='heavy', fontsize=20)


    fig.tight_layout(w_pad=5)
    plt.suptitle(f'{month} Frequency Started', x=0.53, y=0.97, fontsize=30, fontweight='heavy')
    plt.subplots_adjust(top=0.9)
    plt.savefig('starters.png')
    plt.show()
    

def last_3_filler(player_mistakes, last_man, last_3_in):
    "Fills Last 3 In dictionary based on form responses"
    
    for starter, count in zip(last_man.index, last_man.values):
        starter = unidecode.unidecode(starter.strip())
        if set(starter.split()).issubset(set(player_mistakes['Jesus Ferreira'])):
            last_3_in['Jesus Ferreira'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Haji Wright'])):
            last_3_in['Haji Wright'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Ricardo Pepi'])):
            last_3_in['Ricardo Pepi'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Jordan Pefok'])):
            last_3_in['Jordan Pefok'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Malik Tillman'])):
            last_3_in['Malik Tillman'] += count 
        elif set(starter.split()).issubset(set(player_mistakes['Josh Sargent'])):
            last_3_in['Josh Sargent'] += count 
        elif set(starter.split()).issubset(set(player_mistakes['Brandon Vazquez'])):
            last_3_in['Brandon Vazquez'] += count
        elif set(starter.split()).issubset(set(player_mistakes['DeAndre Yedlin'])):
            last_3_in['DeAndre Yedlin'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Djordje Mihailovic'])):
            last_3_in['Djordje Mihailovic'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Tim Ream'])):
            last_3_in['Tim Ream'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Christian Roldan'])):
            last_3_in['Christian Roldan'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Reggie Cannon'])):
            last_3_in['Reggie Cannon'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Gianluca Busio'])):
            last_3_in['Gianluca Busio'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Luca de la Torre'])):
            last_3_in['Luca de la Torre'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Brendan Aaronson'])):
            last_3_in['Brendan Aaronson'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Mark McKenzie'])):
            last_3_in['Mark McKenzie'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Aaron Long'])):
            last_3_in['Aaron Long'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Joe Scally'])):
            last_3_in['Joe Scally'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Kellyn Acosta'])):
            last_3_in['Kellyn Acosta'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Paul Arriola'])):
            last_3_in['Paul Arriola'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Sam Vines'])):
            last_3_in['Sam Vines'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Cameron Carter-Vickers'])):
            last_3_in['Cameron Carter-Vickers'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Diego Luna'])):
            last_3_in['Diego Luna'] += count
        elif set(starter.split()).issubset(set(player_mistakes['James Sands'])):
            last_3_in['James Sands'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Erik Palmer-Brown'])):
            last_3_in['Erik Palmer-Brown'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Folarin Balogun'])):
            last_3_in['Folarin Balogun'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Auston Trusty'])):
            last_3_in['Auston Trusty'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Daryl Dike'])):
            last_3_in['Daryl Dike'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Paxten Aaronson'])):
            last_3_in['Paxten Aaronson'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Alex Mendez'])):
            last_3_in['Alex Mendez'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Walker Zimmerman'])):
            last_3_in['Walker Zimmerman'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Alejandro Zendejas'])):
            last_3_in['Alejandro Zendejas'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Thomas Gaudin'])):
            last_3_in['Thomas Gaudin'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Justin Che'])):
            last_3_in['Justin Che'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Alejandro Alvarado Jr.'])):
            last_3_in['Alejandro Alvarado Jr.'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Taylor Booth'])):
            last_3_in['Taylor Booth'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Niko Tsakiris'])):
            last_3_in['Niko Tsakiris'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Richie Ledezma'])):
            last_3_in['Richie Ledezma'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Matthew Hoppe'])):
            last_3_in['Matthew Hoppe'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Cade Cowell'])):
            last_3_in['Cade Cowell'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Quinn Sullivan'])):
            last_3_in['Quinn Sullivan'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Alan Sonora'])):
            last_3_in['Alan Sonora'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Jonathan Gomez'])):
            last_3_in['Jonathan Gomez'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Obed Vargas'])):
            last_3_in['Obed Vargas'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Mauricio Cuevas'])):
            last_3_in['Mauricio Cuevas'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Brandon Craig'])):
            last_3_in['Brandon Craig'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Keaton Parks'])):
            last_3_in['Keaton Parks'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Kevin Paredes'])):
            last_3_in['Kevin Paredes'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Unknown'])):
            last_3_in['Unknown'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Joshua Wynder'])):
            last_3_in['Joshua Wynder'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Cruz Medina'])):
            last_3_in['Cruz Medina'] += count
        elif set(starter.split()).issubset(set(player_mistakes['John Tolkin'])):
            last_3_in['John Tolkin'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Sergino Dest'])):
            last_3_in['Sergino Dest'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Bryan Reynolds'])):
            last_3_in['Bryan Reynolds'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Johnny Cardoso'])):
            last_3_in['Johnny Cardoso'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Jack McGlynn'])):
            last_3_in['Jack McGlynn'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Daniel Edelman'])):
            last_3_in['Daniel Edelman'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Gio Reyna'])):
            last_3_in['Gio Reyna'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Weston McKennie'])):
            last_3_in['Weston McKennie'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Julian Gressel'])):
            last_3_in['Julian Gressel'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Cavan Sullivan'])):
            last_3_in['Cavan Sullivan'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Maximo Carrizo'])):
            last_3_in['Maximo Carrizo'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Keyrol Figueroa'])):
            last_3_in['Keyrol Figueroa'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Malick Sanogo'])):
            last_3_in['Malick Sanogo'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Jaheim Headley'])):
            last_3_in['Jaheim Headley'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Rokas Pukstas'])):
            last_3_in['Rokas Pukstas'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Tim Weah'])):
            last_3_in['Tim Weah'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Tanner Tessman'])):
            last_3_in['Tanner Tessman'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Eryk Williamson'])):
            last_3_in['Eryk Williamson'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Caleb Wiley'])):
            last_3_in['Caleb Wiley'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Cole Bassett'])):
            last_3_in['Cole Bassett'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Matt Miazga'])):
            last_3_in['Matt Miazga'] += count
        elif set(starter.split()).issubset(set(player_mistakes['John Brooks'])):
            last_3_in['John Brooks'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Jordan Morris'])):
            last_3_in['Jordan Morris'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Miles Robinson'])):
            last_3_in['Miles Robinson'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Paxton Pomykal'])):
            last_3_in['Paxton Pomykal'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Chris Richards'])):
            last_3_in['Chris Richards'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Brian Gutierrez'])):
            last_3_in['Brian Gutierrez'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Tim Tillman'])):
            last_3_in['Tim Tillman'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Aidan Morris'])):
            last_3_in['Aidan Morris'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Andrew Carleton'])):
            last_3_in['Andrew Carleton'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Clint Dempsey'])):
            last_3_in['Clint Dempsey'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Landon Donovan'])):
            last_3_in['Landon Donovan'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Luca Koleosho'])):
            last_3_in['Luca Koleosho'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Miles Robinson'])):
            last_3_in['Miles Robinson'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Shaq Moore'])):
            last_3_in['Shaq Moore'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Nicholas Gioacchini'])):
            last_3_in['Nicholas Gioacchini'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Reed Baker-Whiting'])):
            last_3_in['Reed Baker-Whiting'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Mauricio Isais'])):
            last_3_in['Mauricio Isais'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Henry Kessler'])):
            last_3_in['Henry Kessler'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Pedro Soma'])):
            last_3_in['Pedro Soma'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Jalen Neal'])):
            last_3_in['Jalen Neal'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Darren Yapi'])):
            last_3_in['Darren Yapi'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Noel Buck'])):
            last_3_in['Noel Buck'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Konrad de la Fuente'])):
            last_3_in['Konrad de la Fuente'] += count
        elif set(starter.split()).issubset(set(player_mistakes['Tyler Adams'])):
            last_3_in['Tyler Adams'] += count
            
            
            