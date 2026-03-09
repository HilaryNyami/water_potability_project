import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
import os

import warnings
warnings.filterwarnings("ignore") #pour eviter les avertissemnts

st.set_page_config(page_title="WATER POTABILITY", page_icon=":bar_chart:", layout="wide")
#title pour le titre de l'onglet
#page icon: icon de l'onglet
#layout pour l'affichge de la page wide:toute la page ou center: au centre

st.title(" :bar_chart: WATER POTABILITY") # titre de la page
st.markdown('<style>div.block-container{paddind-top:1rem;}</style>', unsafe_allow_html=True)#padding-top pour gérer la position du titre par rapport au haut de page

fl = st.file_uploader(":file_folder: Upload a file", type=(["csv","txt","xlsx","xls"]))
#:file_opload: pour afficher licon de téléchargement, cette ligne permet à l'user de charger un autre fichier que celui qui est par defaut
if fl is not None:
    filename = fl.name
    st.write(filename)
    df = pd.read_excel(filename)
else:
    os.chdir(r"C:\Users\murie\Documents\hilary\certif\data")
    df = pd.read_csv("water_potability.csv")


# creation du formulaire
with st.form("formulaire"):
    ph = st.number_input("pH", step = 0.2)
    hardness = st.number_input("Hardness", step = 0.2)
    solids = st.number_input("Solids", step = 0.2)
    chloramines = st.number_input("Chloramines", step = 0.2)
    sulfate = st.number_input("Sulfate", step = 0.2)
    conductivity = st.number_input("Conductivity", step = 0.2)
    organic_carbon = st.number_input("Organic_carbon", step = 0.2)
    trihalomethanes = st.number_input("Trihalomethanes", step = 0.2)
    turbidity = st.number_input("Turbidity", step = 0.2)
    submitted = st.form_submit_button("Send")




 
col1, col2 = st.columns((2)) # pour avoir deux graphes différentes sur la meme ligne
df["Order Date"] = pd.to_datetime(df["Order Date"]) #coneversion de la date en datetime, de base c'est le type objet

#Getting the min and max date
startdate = pd.to_datetime(df["Order Date"]).min() # la plus petite date qui couvre le dataset
enddate = pd.to_datetime(df["Order Date"]).max() # la plus grande date qui couvre le dataset

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startdate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date", enddate))

df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy()

st.sidebar.header("Choose your filter: ") #pour afficher la barre vertical
# Filter for ph
pHs = st.sidebar.multiselect("Pick pH(s)", df["ph"].unique())
# contient la liste des regions selectionnes

if not region:
    df2 = df.copy() #si on n'a selectionne aucune region alors on fait une copie du ds
else:
    df2 = df[df["Region"].isin(region)] # si on a des regions alors on fait une cp du ds en fxn des regions choisis

# Filter for state
state = st.sidebar.multiselect("Pick the state", df2["State"].unique())
#multiselect permet de faire plusiurs choix

if not state:
    df3 = df2.copy()
else:
    df3 = df2[df2["State"].isin(state)]

# Filter for city
city = st.sidebar.multiselect("Pick a city", df3["City"].unique())

# data filtered based on Region, State and City

if not region and not state and not city:
    filtered_df = df.copy()
elif not state and not city:
    filtered_df = df[df["Region"].isin(region)]
elif not region and not city:
    filtered_df = df[df["State"].isin(state)]
elif not region and not state:
    filtered_df = df3[df3["City"].isin(city)]
elif state and city:
    filtered_df = df3[df3["State"].isin(state) & df3["City"].isin(city)]
elif region and city:
    filtered_df = df3[df3["Region"].isin(region) & df3["City"].isin(city)]
elif region and state:
    filtered_df = df3[df3["Region"].isin(region) & df3["State"].isin(state)]
else:
    filtered_df = df3[df3["Region"].isin(region) & df3["State"].isin(state) & df3["City"].isin(city)]

category_df = filtered_df.groupby(by = ["Category"], as_index=False)["Sales"].sum()

with col1:
    st.subheader("Category wise Sales")
    fig = px.bar(category_df, x="Category", y="Sales", text=['${:,.2f}'.format(x) for x in category_df["Sales"]],
                 template="seaborn")
    st.plotly_chart(fig, use_container_width=True, height = 200)
    # c'est le format d'affichage
    #avec plotly le graphe est dynamiq en fxn des valeurs il s'adapte

with col2:
    st.subheader("Region wise Sales")
    fig = px.pie(filtered_df, values="Sales", names="Region", hole=0.5)
    fig.update_traces(text = filtered_df["Region"], textposition = "outside")
    st.plotly_chart(fig, use_container_width=True )
    # value: c'est pour afficher les valeurs au survol, names: c'est pour donner le nom de chaque partie, chaq tranche du camembert
    #update_traces: c'est pour le style du dessin, pour le disq creux au lieu de plein avec la légende

cl1, cl2 = st.columns((2))
with cl1:
    with st.expander("Category_ViewData"): #regarder les données en fxn des categories
        st.write(category_df.style.background_gradient(cmap="Blues")) # affiche le ds avec un fond dégradé, plus la couleur est foncé plus la valeur est elevée
        csv = category_df.to_csv(index=False).encode('utf-8')#convertir les données ndarray(type obtenu apres groupby)sous format de fichier csv
        st.download_button("Download Data", data = csv, file_name = "Category.csv", mime="text/csv", #file_name: le nom du fichier après tlchargement mime: ce sont les possibilités de tlchargemnt du fichier
                           help='Click here to download the data as a csv file') # c'est pour afficher le btn de tlchargement, permettre à l'user de télécharger le ds en fxn de ce niveau de granularité|d'abstraction
                         

with cl2:
    with st.expander("Region_ViewData"):
        region = filtered_df.groupby(by = "Region", as_index = False)["Sales"]
        region = pd.DataFrame(region)
        st.write(region.style.background_gradient(cmap="Oranges"))
        csv = region.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "Region.csv", mime="text/csv", 
                           help='Click here to download the data as a csv file')
        
filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")#pour changer l'affichage des mois sous la forme  en Jan...
st.subheader('Time Series Analysis')
linechart = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["Sales"].sum()).reset_index()
fig2 = px.line(linechart, x = "month_year", y="Sales", labels = {"Sales": "Amount"},height=500, width = 1000,template="gridon")
st.plotly_chart(fig2,use_container_width=True)
#linechart est la var qui va contenir le table à 2 dim, %Y c'est pour l'annee %b mois

with st.expander("View Data of TimeSeries"):
    st.write(linechart.T.style.background_gradient(cmap="Blues")) #T c'est pour faie la transposé au lieu de l'afficher sous forme de vecteur colonne
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button('Download Data', data = csv, file_name="TimeSeries.csv",mime="text/csv",
                       help="Click here to doawnload the data as a csv file")
    
# Create a treem based on Region, category, sub-Category
st.subheader("Hierarchical view of Sales using TreeMap")
fig3 = px.treemap(filtered_df, path = ["Region","Category","Sub-Category"], values = "Sales",hover_data = ["Sales"],
                  color = "Sub-Category")
fig3.update_layout(width = 800, height = 650)
st.plotly_chart(fig3, use_container_width=True)
#treemap c'est la representation de l'architecture des données en fxn des différents niveaux d'abstraction
#path:  liste des différents niveaux d'abstarction à utiliser, hover_data: la valeur des ventes à afficher au survol
#lorsqu'on augmente la granularité|abstraction on perd en précision et visibilité

chart1, chart2 = st.columns((2))
with chart1:
    st.subheader('Segment wise Sales') #affichage des ventes en fxn du type de la clientele
    fig = px.pie(filtered_df, values = "Sales", names = "Segment", template = "plotly_dark")
    fig.update_traces(text = filtered_df["Segment"], textposition = "inside")
    st.plotly_chart(fig,use_container_width=True)

with chart2:
    st.subheader('Category wise Sales')
    fig = px.pie(filtered_df, values = "Sales", names = "Category", template = "gridon")
    fig.update_traces(text = filtered_df["Category"], textposition = "inside")
    st.plotly_chart(fig,use_container_width=True)