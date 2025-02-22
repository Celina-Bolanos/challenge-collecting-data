# challenge-collecting-data

#### Description

Fictional real state company "Immo Eliza" wants to create a machine learning model to make price predictions on real state properties in Belgium. <br>

To accomplish this, the immo_eliza project will be developed in four stages: <br>
1. Data Collection
2. Data Analysis
3. Machine Learning model development
4. Deployment

This repository corresponds to the first stage of that project: data collection <br>

#### Learning objectives:

- Be able to scrape a website.
- Be able to build a dataset from scratch.
- Be able to implement a strategy to collect as much data as possible.

#### Mission:
Gather information about at least 10.000 properties all over Belgium. <br>

This dataset should be a `csv` file with the following columns:

- Locality (city/commune)
- Type of property (House or apartment)
- Subtype of property (Bungalow, Chalet, Mansion, ...)
- Price
- Type of sale (Exclusion of life sales)
- Number of rooms
- Living Area
- Fully equipped kitchen (Yes/No)
- Furnished (Yes/No)
- Open fire (Yes/No)
- Terrace (Yes/No)
  - If yes: Area
- Garden (Yes/No)
  - If yes: Area
- Surface of the land
- Surface area of the plot of land
- Number of facades
- Swimming pool (Yes/No)
- State of the building (New, to be renovated, ...)

Must-have features

- Data all over Belgium.
- Minimum 10 000 inputs without duplicates
- No empty rows. Missing information should be to `None`.
- The dataset must be clean. Record numerical values when possible.

