import pandas as pd
import numpy as np

def new_cases_from_cumul(df):
    '''
    Takes cumulative values (cases or deaths) times series and returns daily new values (cases or deaths)
    This function is to be used with the "COVID_plots" function.
    '''

    new_cases = [df['val'][i] - df['val'][i-1] for i in range(1, len(df))] #Cases or deaths data are in the 'val' column of df
    dates = [df.index[i] for i in range(1, len(df))] #dates are in the index of df

    df_new = pd.DataFrame({'date' : dates, 'new_val' : new_cases}).set_index('date') #Format these as a pandas dataframe and return it

    return df_new
