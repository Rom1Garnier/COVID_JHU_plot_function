# COVID-19 figure with JHU data

This repository describes a function I use to makes figures of the cases and deaths due to COVID-19 in the United States, based on the data from the COVID-19 Data Repository by the Center for Systems Science and Engineering (CSSE) at Johns Hopkins University (https://github.com/CSSEGISandData/COVID-19). 

It is capable of figures at three spatial scales: entire country (US), state (by state name), and counties (by county fips). Any number of geographical location can be plotted on the same figure at the same time. 

Three types of plots can be produced: 

- cumulative cases

- new cases

- trend (based on a Prophet fit of the new cases time series data). 
