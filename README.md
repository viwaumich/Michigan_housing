﻿# Michigan_housing

## How to run the visualization code

### Step 1. Download the code

### Step 2. Install needed packages.

You can run the following line in your (local) terminal:

```
pip install shiny
pip install shinywidgets
pip install ipyleaflet
pip install uvicorn
```

### Step 3. Set up shiny app server

Change line 12 of app.py

Launch your terminal in the folder that contains app.py, then run the following code in your terminal

```
uvicorn app:app --host 0.0.0.0 --port 54321
```

You can change the port number to the one you like

### Step 4: Check the visualization in your browser

In your browser url tab, type http://localhost:54321/

The visualization should appear.

## How to update data file

### To update LARA file

Please update the Longitude and Latitude column for every new entry. These coordinates can be found via Google search. Only entries with coordinates will be visualized.

# To upload your own data or update the LARA and MHvillage data

1. Add new LARA file to data folder and add new MHvillage file to data folder (use MHVillagesites.py to scrape)
2. Add new districts (House and Senate) geoJSON file to data folder
3. Run add_clean_address.py to add gps coordinates to both files, update INPUT section as necessary
4. Run add_districts.py to add legislative districts
