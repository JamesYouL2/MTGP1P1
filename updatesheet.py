import pygsheets
import pandas as pd
import requests
from lightgbm import LGBMRegressor
from sklearn.metrics import r2_score
import numpy as np

#Import reader
reader = pygsheets.authorize(service_file="secret.json")

def getrawredditsheet(url):
    #Open Google Sheet
    gsheet=reader.open_by_url(url)

    #Get WorkSheet
    df=gsheet.worksheet("title","Sheet1").get_as_df()

    Misspelling = {
        "Daysqaud Marshal": "Daysquad Marshal",
        "Majestuc Auricorn": "Majestic Auricorn",
        "Aeigis Turtle": "Aegis Turtle",
        "Bastion of rememberance": "Bastion of Remembrance",
        "Cavern Whisper": "Cavern Whisperer",
        "Hartless Act": "Heartless Act",
        "Everquill Pheonix": "Everquill Phoenix",
        "Lukka, Copper Coat Outcast": "Lukka, Coppercoat Outcast",
        "Reptillian Reflection": "Reptilian Reflection",
        "Great Sandwurm": "Greater Sandwurm",
        #"Inspired Ultimatum": "Inspired Ultimatum",
        "Kerugna, the Macrosage": "Keruga, the Macrosage",
        "Lurrus of the Dream-Den": "Lurrus of the Dream Den",
        "Yoiron, Sky Nomad": "Yorion, Sky Nomad",
        "Zidra, the Dawnwaker": "Zirda, the Dawnwaker",
        "Blossiming Sands": "Blossoming Sands",
        "Bonder's Enclave": "Bonders' Enclave",
        "Idatha Triome": "Indatha Triome",
        "Wind-Scared Crag": "Wind-Scarred Crag",
    }
    
    df=df.apply(lambda x: x.str.strip() if x.name!="CMC" else x)
    df.replace({"Card Name": Misspelling},inplace=True)

    return df

def redditsheet(url):
    graderdf = getrawredditsheet(url)

    #create list
    gradelist = ["Nizz Grade", "Deathsie", "LoL", "Mana Leek"]

    #Transform/Clean DF to get single grade
    graderdf[gradelist]=graderdf[gradelist].apply(lambda x: x.str.split("*").str[0])
    graderdf[gradelist]=graderdf[gradelist].apply(lambda x: x.str.split("/").str[0])
    graderdf[gradelist]=graderdf[gradelist].apply(lambda x: x.str.strip())
    graderdf[gradelist]=graderdf[gradelist].apply(lambda x: x.str[:2])

    #Dictionaries to apply to every grader
    NizzDict =	{
    "A": 5.0,
    "A-": (5.0 / 11) * 10,
    "B+": (5.0 / 11) * 9,
    "B": (5.0 / 11) * 8,
    "B-": (5.0 / 11) * 7,
    "C+": (5.0 / 11) * 6,
    "C": (5.0 / 11) * 5,
    "C-": (5.0 / 11) * 4,
    "D+": (5.0 / 11) * 3,
    "D": (5.0 / 11) * 2,
    "D-": (5.0 / 11) * 1,
    "F": (5.0 / 11) * 0
    }

    DeathsieDict =	{
    "S": 5.0,
    "A": (5.0 / 5) * 4,
    "B": (5.0 / 5) * 3,
    "C": (5.0 / 5) * 2,
    "D": (5.0 / 5) * 1,
    "F": (5.0 / 5) * 0
    }

    LoLDict =	{
    "A+": (5.0 / 12) * 12,
    "A": (5.0 / 12) * 11,
    "A-": (5.0 / 12) * 10,
    "B+": (5.0 / 12) * 9,
    "B": (5.0 / 12) * 8,
    "B-": (5.0 / 12) * 7,
    "C+": (5.0 / 12) * 6,
    "C": (5.0 / 12) * 5,
    "C-": (5.0 / 12) * 4,
    "D+": (5.0 / 12) * 3,
    "D": (5.0 / 12) * 2,
    "D-": (5.0 / 12) * 1,
    "SB": (5.0 / 12) * 0
    }

    ManaLeekDict =	{
    "A+": (5.0 / 12) * 12,
    "A": (5.0 / 12) * 11,
    "A-": (5.0 / 12) * 10,
    "B+": (5.0 / 12) * 9,
    "B": (5.0 / 12) * 8,
    "B-": (5.0 / 12) * 7,
    "C+": (5.0 / 12) * 6,
    "C": (5.0 / 12) * 5,
    "C-": (5.0 / 12) * 4,
    "D+": (5.0 / 12) * 3,
    "D": (5.0 / 12) * 2,
    "D-": (5.0 / 12) * 1,
    "F": (5.0 / 12) * 0,
    "-": 0
    }

    graderdf.replace({"Nizz Grade": ManaLeekDict},inplace=True)
    graderdf.replace({"Deathsie": DeathsieDict},inplace=True)
    graderdf.replace({"LoL": LoLDict},inplace=True)
    graderdf.replace({"Mana Leek": ManaLeekDict},inplace=True)

    graderdf["AverageGrade"] = graderdf[gradelist].mean(axis=1)

    return graderdf

#grab specific 17 lands json  and get wins and losses
def seventeenlandssheet(magicset, drafttype):
    url= "https://www.17lands.com/card_ratings/data?expansion=" + magicset + "&format=" + drafttype
    response = requests.get(url)
    draft=pd.json_normalize(response.json())
    draft["wins"]=draft["game_count"]*draft["win_rate"]
    draft["losses"]=draft["game_count"]-draft["wins"]
    return draft[["name","rarity","wins","losses","game_count"]].round()

#get data from 17 every json for set and combine
def seventeenlands(magicset):
    #magicset = "IKO"
    traddraft =seventeenlandssheet(magicset, "TradDraft")
    premierdraft = seventeenlandssheet(magicset, "PremierDraft")
    mergedraft = traddraft.merge(premierdraft,on="name",how="outer")
    mergedraft = mergedraft.fillna(0)
    mergedraft["wins"] = mergedraft["wins_x"] + mergedraft["wins_y"]
    mergedraft["losses"] = mergedraft["losses_x"] + mergedraft["losses_y"]
    mergedraft["game_count"] = mergedraft["game_count_x"] + mergedraft["game_count_y"]
    return mergedraft[["name","wins","losses","game_count"]]

#Combines 17lands with Grader data and returns df
def regressor(magicset, url):
    gradesheet=redditsheet(url)
    df_17l=seventeenlands(magicset)

    #Feature engineering, normalize games by rarity
    df=pd.merge(gradesheet,df_17l,left_on="Card Name",right_on="name",how='outer')
    df["RarityGames"]=df.groupby("Rarity")["game_count"].apply(lambda x: x / x.mean())
    df["WinRate"]=df["wins"] / (df["wins"]+df["losses"])

    #split rarity into multiple columns
    df = pd.get_dummies(df, prefix_sep="_", columns=["Rarity"])

    #get dependent and independent variables
    X=df[["RarityGames", "WinRate", "Rarity_Common", "Rarity_Uncommon", "Rarity_Mythic"]]
    y=df["AverageGrade"]

    regressor = LGBMRegressor()  
    regressor.fit(X,y) #training the algorithm

    y_pred = regressor.predict(X)

    print(r2_score(y,y_pred))

    #Add columns to df
    df["Predicted Rating"] = pd.DataFrame(y_pred)
    df["Diff"] = df["Predicted Rating"]-df["AverageGrade"]

    return df, r2_score(y,y_pred)

def updatesheet():
    url = "https://docs.google.com/spreadsheets/d/1qLApVtJR-TnrjeMJs09sRe-fQ6w_mjoqeh--nXPp5io/"
    
    df, score = regressor("IKO", url)
    origdf = getrawredditsheet(url)

    df = df[["Card Name", "wins", "losses", "game_count", "AverageGrade", "Predicted Rating", "Diff"]]

    outputdf=origdf.merge(df)

    #open the google spreadsheet (where "PY to Gsheet Test" is the name of my sheet)
    sht = reader.open("ArenaDraft")
    worksheet = sht.worksheet("title","IKO")

    worksheet.clear()
    worksheet.set_dataframe(outputdf.sort_values("Predicted Rating", ascending=False),(1,1))
