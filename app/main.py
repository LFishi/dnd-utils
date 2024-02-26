import streamlit as st
import pandas as pd
import numpy as np
import openpyxl
from random import randint
import re
from core.Treasure import TreasureHoard

st.set_page_config(page_title="DnD Utils", layout="wide")
excelFileName = "local/TreasureHoardTables.xlsm"

@st.cache_data
def load_xls_files() -> dict[pd.DataFrame]:
    dfs = {}
    wb = openpyxl.load_workbook(excelFileName) 

    for sheet in wb.sheetnames:
        df = pd.read_excel(excelFileName, sheet).replace(np.nan, None)
        df.name = sheet
        dfs[sheet] = df

    return dfs

def renderMagicItems(items, title=None):
    itemList = [f"- {items.loc[name]['Amount']}x [{name}]({items.loc[name]['URL']})" for name in items.index]
    
    if title:
        st.header(title)
    st.markdown("\n".join(itemList))

st.sidebar.title("Treasure Hoard Generator")

dfs = load_xls_files()
hoard0_4 = "Hoard CR 0-4"

rarities = ["common", "uncommon", "rare", "very rare", "very rare or legendary", "legendary", "artifact", "rarity by figurine"]
itemTypes = ["Armor", "Weapon", "Wondrous item", "Ring", "Staff", "Rod", "Wand", "Scroll", "Potion"]
color_uncommon = "#1fc219"
color_rare = "#4990e2"
color_veryRare = "#9810e0"
color_legendary = "#fea227"
color_artifact = "#be8972"
treasureHoardTable : pd.DataFrame = dfs[hoard0_4]

# if 'shopList' not in st.session_state:
#     st.session_state.shopList = pd.DataFrame(columns=["Amount", "URL"])
#     st.session_state.shopList.index.name = "Name"

st.sidebar.header("Settings")
iterations = st.sidebar.number_input("Iterations", value=10, min_value=1, max_value=50)

if st.sidebar.button('Generate'):
    st.session_state.shopList = pd.DataFrame(columns=["Amount", "URL"])
    st.session_state.shopList.index.name = "Name"

    for i in range(iterations):
        # select random hoard
        random_roll = randint(1,100)
        treasureHoard = TreasureHoard(**treasureHoardTable[treasureHoardTable["d100"] >= random_roll].iloc[0].to_dict())

        # if treasureHoard.gemsOrArtObjects_value:
        #     # get the corresponding table 
        #     df : pd.DataFrame = dfs[f"{treasureHoard.gemsOrArtObjects_value} {treasureHoard.gemsOrArtObjects_type}"]
            
        #     # roll the amount of rolls
        #     amountRolls = 0
        #     for _ in range(treasureHoard.gemsOrArtObjects_dice.amount):
        #         amountRolls += randint(1, treasureHoard.gemsOrArtObjects_dice.type)


        #     # pick valuables
        #     gemsOrArtObjects : pd.DataFrame = df.sample(amountRolls, replace=True).groupby("Name").size().sort_values().rename("Amount")
            
        #     # build total sum of gps
        #     gp_total = amountRolls * sum([int(value) for value in re.findall(r"\d+", treasureHoard.gemsOrArtObjects_value)])

        #     # render valuables
        #     st.header(f"{gp_total} gp ({amountRolls}x {treasureHoard.gemsOrArtObjects_value})")
        #     objectList = [f"- {gemsOrArtObjects[name]}x {name}" for name in gemsOrArtObjects.index]
        #     st.markdown("\n".join(objectList))

        if treasureHoard.magicItems_table:
            # get the corresponding table
            df : pd.DataFrame = dfs[f"Items {treasureHoard.magicItems_table}"].set_index("Name")
            
            # roll the amount of rolls
            amountRolls = 0
            for _ in range(treasureHoard.magicItems_dice.amount):
                amountRolls += randint(1, treasureHoard.magicItems_dice.type)

            # pick items
            namePicks = []
            for _ in range(amountRolls):
                roll = randint(1,100)
                namePicks.append((df['d100'] - roll).apply(lambda x: x if x > 0 else float('inf')).idxmin())

            magicItemPicks = df.loc[namePicks].groupby(["Name"]).agg({"URL": ["count", lambda x: x.iloc[0]]})
            magicItemPicks.columns = ["Amount", "URL"]

            st.session_state.shopList = pd.concat([st.session_state.shopList, magicItemPicks])
            st.session_state.shopList = st.session_state.shopList.groupby(["Name"]).agg({"Amount": "sum", "URL": lambda x: x.iloc[0]})

    if not st.session_state.shopList.empty:
        st.session_state.shopList = st.session_state.shopList[["Amount", "URL"]]
        originalIndex = st.session_state.shopList.index.copy()
        st.session_state.shopList.index = st.session_state.shopList.index.str.lower()

        allItems = dfs["All by rarity"].set_index("Name")
        allItems.index = allItems.index.str.lower()

        st.session_state.shopList = pd.merge(st.session_state.shopList, allItems, how="left", on="Name")
        st.session_state.shopList.index = originalIndex

st.sidebar.header("Filter")
selectedRarities = st.sidebar.multiselect("Rarities", rarities, ["common", "uncommon"])

st.header("Shop") 
if "shopList" in st.session_state:
    table_to_render = st.session_state.shopList.copy()
    table_to_render.index = [f"[{index_name}]({url})" for index_name, url in zip(table_to_render.index, table_to_render['URL'])]
    table_to_render = table_to_render.drop("URL", axis=1)
    table_to_render["Rarity"] = pd.Categorical(table_to_render["Rarity"], categories=rarities, ordered=True)
    table_to_render["Type"] = pd.Categorical(table_to_render["Type"], categories=itemTypes, ordered=True)
    table_to_render = table_to_render[table_to_render["Rarity"].isin(selectedRarities)]
    table_to_render = table_to_render.sort_values(by=["Type", "Rarity", "Amount"], ascending=[True, True, False])
    table_to_render["Rarity"] = table_to_render["Rarity"].astype(str)
    table_to_render.loc[table_to_render["Rarity"] == "uncommon", "Rarity"] = table_to_render.loc[table_to_render["Rarity"] == "uncommon", "Rarity"].map(lambda rarity: f"<span style='color:{color_uncommon}'>{rarity}</span>")
    table_to_render.loc[table_to_render["Rarity"] == "rare", "Rarity"] = table_to_render.loc[table_to_render["Rarity"] == "rare", "Rarity"].map(lambda rarity: f"<span style='color:{color_rare}'>{rarity}</span>")
    table_to_render.loc[table_to_render["Rarity"] == "very rare", "Rarity"] = table_to_render.loc[table_to_render["Rarity"] == "very rare", "Rarity"].map(lambda rarity: f"<span style='color:{color_veryRare}'>{rarity}</span>")
    table_to_render.loc[table_to_render["Rarity"] == "legendary", "Rarity"] = table_to_render.loc[table_to_render["Rarity"] == "legendary", "Rarity"].map(lambda rarity: f"<span style='color:{color_legendary}'>{rarity}</span>")
    table_to_render.loc[table_to_render["Rarity"] == "artifact", "Rarity"] = table_to_render.loc[table_to_render["Rarity"] == "artifact", "Rarity"].map(lambda rarity: f"<span style='color:{color_artifact}'>{rarity}</span>")
    table_to_render["Rarity"] = table_to_render["Rarity"].map(lambda rarity: f"**{rarity}**")


    st.markdown(table_to_render.to_markdown(), unsafe_allow_html=True)