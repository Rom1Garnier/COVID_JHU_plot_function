import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from fbprophet import Prophet
from COVID_new_cases import new_cases_from_cumul #import a function to get new cases from cumulative cases

#This is necessary to be able to use pandas plot functions
pd.plotting.register_matplotlib_converters()

def COVID_plots(locations, data_type, fig_type, legend = True, lw = 2, ls = 'solid', legend_fs = 18, colors = plt.rcParams['axes.prop_cycle'].by_key()['color'], ax = None):
    '''
    A function to plot the cases or deaths, and either the raw case counts, the daily new cases, or the trend.
    Accepts "deaths" or "cases" as data types.
    Relies on the COVID-19 Data Repository by the Center for Systems Science and Engineering (CSSE) at Johns Hopkins University (https://github.com/CSSEGISandData/COVID-19).

    Parameters:
    - locations: a list of locations. A single location does not need to be passed as a list.
    - data_type: cases or deaths
    - fig_type: one of 'cumulative', 'new' (for new cases), or 'trend' for the Prophet fitted trend
    - legend: whether to add a legend or not
    - lw: linewidth, integer.
    - ls: linestyle, standard matplotlib values.
    - legend_fs: fontsize for the labels of the legend
    - colors: list of colors to use for the plot; if none specified, standard matplotlib cycle. If less colors provided than locations, cycles through colors.
    - ax: can be used to specify an ax to plot to. Used to make panelled figures with matplotlib.
     '''
    #Set the legend fontsize to legend_fs globally
    plt.rcParams['legend.fontsize'] = legend_fs

    #Check that 'locations' is a list or make it one
    #This happens with one location
    if type(locations) != list:
        locations = [locations]

    #Make sure that colors is a list
    #This happens when only one colors is specified without brackets
    if type(colors) != list:
        colors = [colors]

    #Initiate a location counter - used for colors
    loc_n = 0

    #Loop through the locations
    for location in locations:
        #First import the data based on data type
        data_type = data_type.lower()
        if data_type == 'cases':
            df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv')
            df = df.drop(['UID', 'iso2', 'iso3', 'code3', 'Admin2', 'Country_Region', 'Lat', 'Long_', 'Combined_Key'], axis = 1)
            df = df[df['FIPS'] < 80000].copy() #Remove the "out of state" and "unassigned"

            all_vars = df.columns
            value_vars = all_vars.drop(['Province_State', 'FIPS'])
            id_vars = ['Province_State', 'FIPS']
            df_clean = df.melt(id_vars = id_vars, value_vars = value_vars, var_name = 'date', value_name = 'cases')
            df_clean['date'] = pd.to_datetime(df_clean['date'])
            df_clean = df_clean.rename(columns = {'cases' : 'val'})
            df_clean['Province_State'] = df_clean['Province_State'].str.lower()

        elif data_type == 'deaths':
            df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv')
            df = df.drop(['Population', 'UID', 'iso2', 'iso3', 'code3', 'Admin2', 'Country_Region', 'Lat', 'Long_', 'Combined_Key'], axis = 1)
            df = df[df['FIPS'] < 80000].copy() #Remove the "out of state" and "unassigned"

            all_vars = df.columns
            value_vars = all_vars.drop(['Province_State', 'FIPS'])
            id_vars = ['Province_State', 'FIPS']
            df_clean = df.melt(id_vars = id_vars, value_vars = value_vars, var_name = 'date', value_name = 'deaths')
            df_clean['date'] = pd.to_datetime(df_clean['date'])
            df_clean = df_clean.rename(columns = {'deaths' : 'val'})
            df_clean['Province_State'] = df_clean['Province_State'].str.lower()

        else:
            return print('Plot aborted. Please provide one of "cases" or "deaths" as data type.')


        #Figure if the location is the entire country, a state, or the county.
        #Get the data formatted accordingly
        if type(location) == str:
            location = location.lower()

            if (location == 'us') | (location == 'usa') | (location == 'america'):
                df_location = df_clean.groupby('date').sum().reset_index().sort_values('date')

            elif location in df_clean['Province_State'].unique():
                df_location = df_clean[df_clean['Province_State'] == location].copy().groupby(['Province_State', 'date']).sum().reset_index().sort_values('date')

            else:
                return print('''
                Plot aborted. Please check the location provided. The function accepts the following:
                - US or USA
                - a state name
                - a county FIPS
                ''')

        elif (type(location) == int) & (location in df_clean['FIPS'].unique()):
            df_location = df_clean[df_clean['FIPS'] == location].copy().sort_values('date')

        else:
            return print('''
            Plot aborted. Please check the location provided. The function accepts the following:
            - US or USA
            - a state name
            - a county FIPS
            ''')

        #Now get the data for the plot based on the type of plot required
        #Three types of plots are supported
        #1/ Cumulative cases
        #2/ New cases
        #3/ Trends - based on fbprophet fit
        fig_type = fig_type.lower()

        if fig_type == 'cumulative':
            df_for_plot = df_location.set_index('date')
            df_for_plot['val'].plot(ax = ax, legend = legend, label = location.capitalize(), linewidth = lw, linestyle = ls, color = colors[loc_n % len(colors)])

        elif fig_type == 'new':
            df_for_plot = new_cases_from_cumul(df_location.set_index('date'))
            df_for_plot['new_val'].plot(ax = ax, legend = legend, label = location.capitalize(), linewidth = lw, linestyle = ls, color = colors[loc_n % len(colors)])

        elif fig_type == 'trend':
            df_new = new_cases_from_cumul(df_location.set_index('date')).reset_index() #Get time series of new cases
            series =df_new[['date', 'new_val']].copy() #Only keep the relevant columns
            series.rename(columns = {'date' : 'ds', 'new_val' : 'y'}, inplace = True) #Rename columns to match Prophet syntax

            #Initiate prophet model
            #Model is made to be very flexible, with one possible changepoint for each date
            prophet_mod = Prophet(changepoint_prior_scale=0.5,
                                  changepoint_range = 1,
                                  changepoints = [date for date in series['ds']],
                                  yearly_seasonality = False,
                                  daily_seasonality = False,
                                  weekly_seasonality = True)
            #Fit the Prophet model
            prophet_fit = prophet_mod.fit(series)
            #Use the model to "forecast" values and get the trend
            #Here this is only used to get the fit of the model
            future = prophet_mod.make_future_dataframe(periods= 0, freq='D')
            forecast = prophet_mod.predict(future).set_index('ds')

            forecast['trend'].plot(ax = ax, legend = legend, label = location.capitalize(), linewidth = lw, linestyle = ls, color = colors[loc_n % len(colors)])

        else:
            return print('''
            Plot aborted. Please check the type of plot requested. The function accepts:
            - "cumulative" for cumulative cases plot
            - "new" for daily new cases plot
            - "trend" for trend plots''')

        #Add 1 to the location counter
        loc_n += 1
