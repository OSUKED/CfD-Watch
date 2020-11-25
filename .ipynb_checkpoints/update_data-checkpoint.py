"""
Imports
"""
import json
import pandas as pd
import requests
from warnings import warn


"""
Functions
"""
def retrieve_CfD_df_for_single_round(allocation_round, page, cfd_url):
    params = {
        'agreement_type': 'All',
        'field_cfd_current_strikeprice': 'All',
        'allocation_round[]': allocation_round,
        'sort_by': 'name_1',
        'page': page
    }

    r = requests.get(cfd_url, params=params)
    tables = pd.read_html(r.text)

    df_allocation_round = tables[0]
    df_allocation_round['Allocation round'] = allocation_round

    return df_allocation_round
            
def retrieve_CfD_df(cfd_url='https://www.lowcarboncontracts.uk/cfds', 
                    allocation_rounds=['Allocation Round 1', 'Allocation Round 2', 
                                       'Allocation Round 3', 'Investment Contract', 
                                       'Other allocation', 'N/A']):

    df = pd.DataFrame()

    for allocation_round in allocation_rounds:
        page = 0
        continue_scraping_round = True

        while continue_scraping_round:
            try:
                df_allocation_round = retrieve_CfD_df_for_single_round(allocation_round, page, cfd_url)
                df = df.append(df_allocation_round)
                page += 1
            except:
                if page == 0:
                    warn(f'No data could be retrieved for allocation round: {allocation_round}')
                else:
                    pass
                
                continue_scraping_round = False

    df = df.reset_index(drop=True)
    
    return df

filter_df_for_allocation_round = lambda df, allocation_round: list(df
                                                                   [df['Allocation round']==allocation_round]
                                                                   .T
                                                                   .to_dict()
                                                                   .values()
                                                                  ) 

def format_allocation_round_strike_prices(df):
    allocation_rounds = sorted(list(df['Allocation round'].unique()))
    
    allocation_round_strike_prices = {
        allocation_round: filter_df_for_allocation_round(df, allocation_round)
        for allocation_round 
        in allocation_rounds
        if len(filter_df_for_allocation_round(df, allocation_round)) > 0
    }
    
    return allocation_round_strike_prices

def update_readme_time(readme_fp, 
                       splitter='Last updated: ', 
                       dt_format='%Y-%m-%d %H:%M'):
    
    with open(readme_fp, 'r') as readme:
        txt = readme.read()
    
    start, end = txt.split(splitter)
    old_date = end[:16]
    end = end.split(old_date)[1]
    new_date = pd.Timestamp.now().strftime(dt_format)
    
    new_txt = start + splitter + new_date + end
    
    with open(readme_fp, 'w') as readme:
        readme.write(new_txt)
        
    return


"""
Retrieval Process
"""
allocation_round_strike_prices = (retrieve_CfD_df()
                                  .pipe(format_allocation_round_strike_prices)
                                 )

with open('data/CfD_strike_prices.json', 'w') as fp:
    json.dump(allocation_round_strike_prices, fp)
    
update_readme_time('README.md')