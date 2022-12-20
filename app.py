#import required libraries
import sqlite3
import pandas as pd
import dash
from dash import Input, Output
import dash_core_components as dcc
import dash_html_components as html
from flask import Flask
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from bs4 import BeautifulSoup

#read hr database using sqlite3
conn = sqlite3.connect("hr")


#initialize app
server = Flask(__name__)
app = dash.Dash(__name__, server = server, external_stylesheets = [dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP])
server = app.server


#answer for question2
# jobNumbers = pd.read_sql_query("select job_id, COUNT(*) from employees group by job_id", conn)
jobNumbers = pd.read_sql_query("SELECT employees.first_name, jobs.job_title " +"FROM employees " +
                                "INNER JOIN jobs ON employees.job_id " + "= jobs.job_id", conn)
jobNumbers.rename(columns = {'COUNT(*)':'count'}, inplace = True)
#fig1 = px.bar(jobNumbers, x='job_id', y='COUNT(*)')


#answer for question 3
#salaryDiff = pd.read_sql_query("select max(salary)-min(salary) DIFFERENCE from employees", conn)
jobs=pd.read_sql_query("select * from jobs;",conn)
jobs = jobs.iloc[1: , :]
jobs["difference"]=jobs['max_salary']-jobs['min_salary']
job=jobs[['job_title','difference']]
max_salary=job['difference'].max()

@app.callback(
    Output('output3', 'figure'),
    Input('input3', 'value')
)
def update_output(value):
    minimum=value[0]
    maximum=value[-1]
    figure2 = go.Figure()
    figure2["layout"]["xaxis"]["title"] = "Job"
    figure2["layout"]["yaxis"]["title"] = "Max - Min"
    t = job[job["difference"]>=minimum][job["difference"]<=maximum]
    figure2.add_trace(go.Bar(x=t['job_title'], y=t['difference'],
    name='Job differences', marker = {'color' : '#C45AEC'}))
    return figure2





#all the components
header = html.H1("Dashboard For Final Exam", style = {'color': 'white', 'textAlign': 'center',
                                                  'backgroundColor':'#aeb6bf', 'height': '100px',
                                                  'padding': '13px', 'font-weight': 'bold'})

#figure1
# figure1 = go.Figure()
# figure1.add_trace(go.Bar(x=jobNumbers.job_id, marker = {'color' : '#C45AEC'}))
figure1 = px.bar(jobNumbers, x='job_title', color  = "job_title")

#question 4
URL = "https://www.itjobswatch.co.uk/jobs/uk/sqlite.do"
r = requests.get(URL)
soup = BeautifulSoup(r.content, 'html5lib')
table = soup.find('table', attrs = {'class':'summary'})
table.find('form').decompose()
table_data = table.tbody.find_all("tr")
table = []
for i in table_data:
    row = []
    rrr = i.find_all("td")
    if len(rrr) == 0:
        rrr = i.find_all("th")
    for j in rrr:
        row.append(j.text)
    table.append(row)

hd = table[1]
hd[0] = "index"

df = pd.DataFrame(table)
df.drop(index=[0,1,2,3,4,5,6,7,10,11,14,15],axis=0,inplace=True)
df.columns = hd
df.set_index("index",inplace=True)
df.reset_index(inplace=True)
df['Same period 2021'] = df['Same period 2021'].str.replace('£','')
df['Same period 2021'] = df['Same period 2021'].str.replace(',','')
df['Same period 2021'] = df['Same period 2021'].str.replace('-','0').astype(float)
df['6 months to20 Dec 2022'] = df['6 months to20 Dec 2022'].str.replace('£','')
df['6 months to20 Dec 2022'] = df['6 months to20 Dec 2022'].str.replace(',','').astype(float)
df['Same period 2020'] = df['Same period 2020'].str.replace('£','')
df['Same period 2020'] = df['Same period 2020'].str.replace(',','').astype(float)

conn = sqlite3.connect("hr")
employees = pd.read_sql_query("select * from employees;", conn)
jobs = pd.read_sql_query("select * from jobs;", conn)



job_titles = jobs['job_title']
job_counts = [len(employees[employees['job_id'] == i]) for i in jobs['job_id']]

percentiles = df
avg_salary = employees['salary'].mean()
percentile = ['10th Percentile', '20th Percentile', '75th Percentile', '90th Percentile']

figure3 = go.Figure()

figure3.add_trace(go.Scatter(x=percentile, y=[
                  avg_salary for i in percentile], name='Average Salary', line=dict(color="#000000")))
for i in percentiles:
        figure3.add_trace(go.Scatter(
            x=percentile, y=percentiles[i], name=f'{i}th Percentile', line=dict(color="#30f216")))



#layout
app.layout = html.Div([
    dbc.Row([
         header
    ]),
    dbc.Row([
        dbc.Col([dcc.Graph(figure = figure1)])
    ]),
    dbc.Row([
        dbc.Col([
            dcc.RangeSlider(0, max_salary, 1000, value=[0, max_salary],id="input3"),
            dcc.Graph(id="output3")
        ])
    ]),
    dbc.Row([
        dbc.Col([dcc.Graph(figure=figure3)])
    ])
])

#run app
app.run_server()