import requests
import os
import itertools
import base64
import pandas as pd
import numpy as np
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc/Users/alexandra.stevens/Documents/GitHub/jnj-ooc-dashboard/index.py
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_daq as daq
import dash_table as dt
import plotly.graph_objects as go
import datetime
import plotly.express as px
import pathlib
import dash_auth
from google.oauth2 import service_account
from pandas.io import gbq
import pandas_gbq
from datetime import date

user_password_pairs = {'drew.shives@hellommc.com' : 'PASamuelson06171989#', 'alexandra.stevens@hellommc.com' : '240803', 'jomalley@hellommc.com' : 'MMC_830!',
'AlexGorsky01' : 'OOC2021!'}

app = dash.Dash(__name__, title = 'J&J OOC Dashboard', external_stylesheets=[dbc.themes.MATERIA], suppress_callback_exceptions=True,
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}]
                )
server = app.server

auth = dash_auth.BasicAuth(app, user_password_pairs)

credentials = service_account.Credentials.from_service_account_file('jnj-ooc-fbdbb13463ac.json')
project_id = 'jnj-ooc'

df_chng_fav = pd.read_excel('chng_fav.xlsx')
df_fav_ceo = pd.read_excel('fav_ceo.xlsx')
df_resp_ceo = pd.read_excel('resp_ceo.xlsx')
df_linkedin = pd.read_excel('Alex Gorsky - LinkedIn.xlsx', skiprows = 1, skipfooter = 1)
df_engagements = pd.read_excel('alex_activity_may.xlsx')
df_blogs = pd.read_excel('Alex Blog Data and Metrics.xlsx')

df_linkedin['Date'] = pd.to_datetime(df_linkedin['Date'])
df_engagements['Date'] = pd.to_datetime(df_engagements['Date'])
df_blogs['Date of Posting'] = pd.to_datetime(df_blogs['Date of Posting'])

exec_dict = {'Alex Gorsky (J&J)':['Alex Gorsky'], 
             'Tim Cook (Apple)':['Tim Cook', 'tim_cook'], 
             'Albert Bourla (Pfizer)':['Albert Bourla', 'AlbertBourla'],
             'Stephen Hoge (Moderna)':['Stephen Hoge', 'stephen-hoge'],
             'Pascal Soriot (AstraZeneca)':['Pascal Soriot'],
             'Vasant Narasimhan (Novartis)':['Vasant Narasimhan', 'VasNarasimhan', 'vasmarasimhan'],
             'Sundar Pichai (Alphabet)':['Sundar Pichai', 'sundarpichai', 'sundar-pichai'],
             'Marc Benioff (Salesforce)':['Marc Benioff', 'Benioff', 'marcbenioff'],
             'Satya Nadella (Microsoft)':['Satya Nadella', 'satyanadella'],
             'Ramon Laguarta (PepsiCo)':['Ramon Laguarta', 'ramonlaguarta', 'RLaguarta'],
             'David Taylor (P&G)':['David Taylor', 'davidtaylorpg'],
             'Bob Chapek (Disney)':['Bob Chapek'],
             'Mary Barra (GM)':['Mary Barra', 'mtbarra', 'mary-barra'],
             'Jamie Dimon (JP Morgan)':['Jamie Dimon', 'jamie-dimon'],
             'Doug McMillon (Walmart)':['Doug McMillon', 'dougmcmillon']}

colors = {"Tim Cook (Apple)": "#00008B",
          "Albert Bourla (Pfizer)": "#FF00FF", 
          "Alex Gorsky (J&J)": "#ff0000",
          'Steph Hoge (Moderna)':'#1dcccf',
          'Pascal Soriot (AstraZeneca)':'#ff8800',
          'Vasant Narasimhan (Novartis)':'#8600c9',
          'Sundar Pichai (Alphabet)':'#16d0f5',
          'Marc Benioff (Salesforce)':'#026605',
          'Satya Nadella (Microsoft)':'#ff47dd',
          'Ramon Laguarta (PepsiCo)':'#ff6f00',
          'David Taylor (P&G)':'#00ff3c',
          'Bob Chapek (Disney)':'#ff9999',
          'Mary Barra (GM)':'#fff799',
          'Jamin Dimon (JP Morgan)':'#00ffe5',
          'Doug McMillon (Walmart)':'#d2fcb1'}

app.layout = html.Div(
    [
        dcc.Store(id='aggregate_data'),
        html.Div(
            [
                html.Div(
                    [
                        html.Div([
		       html.Img(
		           src = app.get_asset_url("logo.jpeg"),
		               style = {'width':'50%', 'height':'50%'}
		       )], style = {'textAlign':'left'}),
                        html.H4(
                            'Office of the Chair Monthly Performance and CEO Landscape Dashboard test', style = {'fontSize':40, 'fontFamily':'Arial'}
                        )
                    ],

                    className='eight_columns'
                ),
                html.Img(
                    src="",
                    className='two_columns',
                ),
            ],
            id="header",
            className='row',
        ),
        html.Div(
            [
                html.Div([
                    dbc.Row([
                        html.Div([
                            html.P(
                                'Filter by Date'
                            ),
                            dcc.DatePickerRange(
                                id = 'date_picker',
                                min_date_allowed= date(2021, 5, 1),
                                max_date_allowed= date(2021, 6, 30),
                                initial_visible_month = date(2021, 5, 1),
                                start_date = date(2021, 6, 1),
                                end_date = date(2021, 6, 30)
                            )],
                            style = {
                                'fontFamily':'Arial',
                                     'padding':'2em'
                            }
                        ),
                        html.Div([html.P(
                            'Filter by Executive:'
                        ),
                        dcc.Dropdown(
                            id='exec_dropdown',
                            options = [{'label': i, 'value': i} for i in exec_dict.keys()],
                            multi=True,
                            value=[i for i in exec_dict.keys()]
                        )], style = {'width':'50%',
                                    'margin-left':'15px',
                                    'fontFamily':'Arial',
                                    'padding':'2em'}),
                    html.Div([
                        html.P(
                        'Filter Comms Pillar Coverage Only'
                        ),
                        daq.BooleanSwitch(
                            id = 'comms_pillar_toggle',
                            on = False
                        )], style = {'padding':'2em'})])                    
            ]
        )]),
        html.Br(),
        html.Br(),
        html.Div([
                html.Div([
                    html.Div([
                    html.H3('Key Alex Gorsky Perception Metrics', style = {'fontSize':35, 'fontFamily':'Arial'}),
                        html.H4('Source: Morning Consult May 2021', style = {'fontSize':15, 'fontFamily':'Arial'})
                    ]),
                                html.Br(),
                                html.Br(),
                                html.Div([dbc.Row([
                                    dbc.Col([
                                        dbc.Card([
                                            html.Div(id = 'fav_card',
                                                     children = '{:.0%}'.format(.55)),
                                            html.P('Favorability', style={'fontSize': 15, 'fontFamily':'Arial'})
                                        ], color = 'light', outline = True, style={'fontSize':25, 'padding': 5, 'fontFamily':'Arial'})]),
                                    dbc.Col([
                                    dbc.Card([
                                            html.Div(id = 'chng_card',
                                                     children = '{:.0%}'.format(.62)),
                                            html.P('Trust to Do the Right Thing', style={ 'fontSize': 15, 'fontFamily':'Arial'})
                                        ], color = 'light', outline = True, style={'fontSize':25, 'padding': 5, 'fontFamily':'Arial'})]),
                                    dbc.Col([
                                    dbc.Card([
                                            html.Div(id = 'reb_fav_card',
                                                     children = '{:.0%}'.format(.64)),
                                            html.P('Care About Contributing To Society', style={ 'fontSize': 15, 'fontFamily':'Arial'})
                                        ], color = 'light', outline = True, style={'fontSize':25, 'padding': 5, 'fontFamily':'Arial'})]),
                                    dbc.Col([
                                    dbc.Card([
                                            html.Div(id = 'trust_card',
                                                     children = '{:.0%}'.format(.42)),
                                            html.P('Recall Seeing Content', style={ 'fontSize': 15, 'fontFamily':'Arial'})
                                        ], color = 'light', outline = True, style={'fontSize':25, 'padding': 5, 'fontFamily':'Arial'})]),
                                    dbc.Col([
                                    dbc.Card([
                                            html.Div(id = 'impact_card',
                                                     children = '{:.0%}'.format(.87)),
                                            html.P('Positive-Neutral Recall', style={ 'fontSize': 15, 'fontFamily':'Arial'})
                                        ], color = 'light', outline = True, style={'fontSize':25, 'padding': 5, 'fontFamily':'Arial'})]),
                                    ])], style = {'textAlign':'center'})])], style = {'textAlign': 'center'}),
                html.Br(),
                html.Br(),
        html.Div([
            html.Div([html.H4('Key Alex Gorsky Visibility Metrics', style = {'fontSize':35, 'fontFamily':'Arial'}),
                      html.Br(),
                      html.Br(),
                                html.Div([dbc.Row([
                                    dbc.Col([
                                        dbc.Card([
                                            html.Div(id = 'alex_coverage_card'),
                                            html.P('Total Coverage Volume', style={'fontSize': 15, 'fontFamily':'Arial'})
                                        ], color = 'light', outline = True, style={'fontSize':25, 'padding': 5, 'fontFamily':'Arial'})]),
                                    dbc.Col([
                                    dbc.Card([
                                            html.Div(id = 'alex_reach_card'),
                                            html.P('Total Reach', style={'fontSize': 15, 'fontFamily':'Arial'})
                                        ], color = 'light', outline = True, style={'fontSize':25, 'padding': 5, 'fontFamily':'Arial'})]),
                                    dbc.Col([
                                    dbc.Card([
                                            html.Div(id = 'alex_comms_pillars_coverage_card'),
                                            html.P('Comms Pillar Coverage Volume', style={'fontSize': 15, 'fontFamily':'Arial'})
                                        ], color = 'light', outline = True, style={'fontSize':25, 'padding': 5, 'fontFamily':'Arial'})]),
                                    dbc.Col([
                                    dbc.Card([
                                            html.Div(id = 'alex_comms_pillars_reach_card'),
                                            html.P('Comms Pillar Reach', style={'fontSize': 15, 'fontFamily':'Arial'})
                                        ], color = 'light', outline = True, style={'fontSize':25, 'padding': 5, 'fontFamily':'Arial'})]),
                                    dbc.Col([
                                    dbc.Card([
                                            html.Div(id = 'alex_sentiment_card'),
                                            html.P('Positive or Neutral Sentiment', style={'fontSize': 15, 'fontFamily':'Arial'})
                                        ], color = 'light', outline = True, style={'fontSize':25, 'padding': 5, 'fontFamily':'Arial'})]),
                                    ])], style = {'textAlign':'center'})], style = {'textAlign': 'center'}),                       
                    ], style = {'textAlign':'center'}),
        html.Br(),
        html.Br(),
        html.Div([html.H4('Visibility by Message (Percentage)', style = {'fontSize':20, 'fontFamily':'Arial'}),
                  dcc.Graph(id='vis_message_graph_perc',
                            style = {'align':'center',
                                     'width':'100%',
                                     'fontFamily':'Arial'})
                 ], style = {'textAlign':'center'}
                ),
        html.Br(),
        html.Br(),
        html.Div([
            html.H5('Alex Gorsky Engagements', style = {'fontSize':35, 'fontFamily':'Arial'}),
            dbc.Row([
                html.Div([
                    dbc.Col([
                        dcc.Graph(id = 'eng_aud_graph')
                    ])
                ], style = {
                    'width':'50%',
                    'align':'left',
                    'fontFamily':'Arial'
                }),
                html.Div([
                    dbc.Col([
                        dcc.Graph(id = 'speaking_engagements_graph')
                    ])
                ], style = {
                    'align':'right',
                    'width':'50%',
                    'fontFamily':'Arial'
                })
            ])
        ], style = {
            'textAlign':'center'
        }
        ),
        html.Div([
            dt.DataTable(id = 'speaking_engagements_table',
                         columns = [{'name':i, 'id':j} for i, j in zip(['Opportunity Name', 'Date', 'Internal/External', 'Topic', 'Audience'], df_engagements.loc[:, ['Opportunity Name', 'Date', 'Internal/External', 'Topic', 'Audience']])],
                         page_size = 10,
                         style_table = {
                             'fontFamily':'Arial'
                         },
                         style_cell = {
                             'overflow':'hidden',
                             'textOverflow':'ellipses',
                             'maxWidth':0,
                             'fontFamily':'Arial'
                         },
                         sort_action = 'native',
                         data = df_engagements.to_dict('records'),
                         export_format = 'xlsx')
                ], style = {
                    'width':'100%'
                }),
        html.Br(),
        html.Br(),
        html.Div([
            html.H6(
                'LinkedIn Performance',
                style = {
                    'fontSize':35,
                    'fontFamily':'Arial',
                    'textAlign':'center',
                    'padding':'2em'
                }),
            html.Div([dbc.Row([
                dbc.Col([
                    dbc.Card([
                        html.Div(id = 'linkedin_posts_card'),
                        html.P('Total Post Volume', style={'fontSize': 15, 'fontFamily':'Arial'})
                    ], color = 'light', outline = True, style={'fontSize':25, 'padding': 5, 'fontFamily':'Arial'})]),
                dbc.Col([
                    dbc.Card([
                        html.Div(id = 'linkedin_engagements_card'),
                        html.P('Total Engagements', style={'fontSize': 15, 'fontFamily':'Arial'})
                    ], color = 'light', outline = True, style={'fontSize':25, 'padding': 5, 'fontFamily':'Arial'})]),
                dbc.Col([
                    dbc.Card([
                        html.Div(id = 'linkedin_post_views_card'),
                        html.P('Post Views', style={'fontSize': 15, 'fontFamily':'Arial'})
                    ], color = 'light', outline = True, style={'fontSize':25, 'padding': 5, 'fontFamily':'Arial'})]),
                dbc.Col([
                    dbc.Card([
                        html.Div(id = 'linkedin_reshares_card'),
                        html.P('Reshares', style={'fontSize': 15, 'fontFamily':'Arial'})
                    ], color = 'light', outline = True, style={'fontSize':25, 'padding': 5, 'fontFamily':'Arial'})]),
                dbc.Col([
                    dbc.Card([
                        html.Div(id = 'linkedin_likes_card'),
                        html.P('Likes', style={'fontSize': 15, 'fontFamily':'Arial'})
                    ], color = 'light', outline = True, style={'fontSize':25, 'padding': 5, 'fontFamily':'Arial'})]),
                dbc.Col([
                    dbc.Card([
                        html.Div(id = 'linkedin_comments_card'),
                        html.P('Comments', style={'fontSize': 15, 'fontFamily':'Arial'})
                    ], color = 'light', outline = True, style={'fontSize':25, 'padding': 5, 'fontFamily':'Arial'})]),
            ])], style = {'textAlign':'center'})
        ], style = {'textAlign': 'center'}),
        html.Br(),
        html.Br(),
        html.Div([
            html.H6(
                'Blog Performance',
                style = {
                    'fontSize':35,
                    'fontFamily':'Arial',
                    'textAlign':'center',
                    'padding':'2em'
                }),
            html.Div([dbc.Row([
                dbc.Col([
                    dbc.Card([
                        html.Div(id = 'blog_posts_card'),
                        html.P('Total Post Volume', style={'fontSize': 15, 'fontFamily':'Arial'})
                    ], color = 'light', outline = True, style={'fontSize':25, 'padding': 5, 'fontFamily':'Arial'})]),
                dbc.Col([
                    dbc.Card([
                        html.Div(id = 'blog_pageviews_card'),
                        html.P('Total Pageviews', style={'fontSize': 15, 'fontFamily':'Arial'})
                    ], color = 'light', outline = True, style={'fontSize':25, 'padding': 5, 'fontFamily':'Arial'})]),
                dbc.Col([
                    dbc.Card([
                        html.Div(id = 'blog_sessions_card'),
                        html.P('Total Sessions', style={'fontSize': 15, 'fontFamily':'Arial'})
                    ], color = 'light', outline = True, style={'fontSize':25, 'padding': 5, 'fontFamily':'Arial'})]),
                dbc.Col([
                    dbc.Card([
                        html.Div(id = 'blog_likes_card'),
                        html.P('Total Likes', style={'fontSize': 15, 'fontFamily':'Arial'})
                    ], color = 'light', outline = True, style={'fontSize':25, 'padding': 5, 'fontFamily':'Arial'})]),
                dbc.Col([
                    dbc.Card([
                        html.Div(id = 'blog_comments_card'),
                        html.P('Total Comments', style={'fontSize': 15, 'fontFamily':'Arial'})
                    ], color = 'light', outline = True, style={'fontSize':25, 'padding': 5, 'fontFamily':'Arial'})]),
                dbc.Col([
                    dbc.Card([
                        html.Div(id = 'blog_CTR_card'),
                        html.P('Email CTR', style={'fontSize': 15, 'fontFamily':'Arial'})
                    ], color = 'light', outline = True, style={'fontSize':25, 'padding': 5, 'fontFamily':'Arial'})]),
            ])], style = {'textAlign':'center'}),
            html.Br(),
            html.Br(),
            html.Div([
                dt.DataTable(id='blog_table',
                                    columns=[{"name": i, "id": i} for i in df_blogs.columns],
                                    page_size = 10,
                                    style_table = {'fontFamily':'Arial'},
                                    style_cell = {'overflow':'hidden', 'textOverflow':'ellipses', 'maxWidth':0, 'fontFamily':'Arial'},
                                    sort_action = 'native',
                                    data=df_blogs.sort_values(by = ['Date of Posting'], ascending = False).to_dict('records'),
                                    export_format = 'xlsx')
            ], style = {'width':'100%',
                        'textAlign':'center',
                        'fontFamily':'Arial'}
        ),
        ], style = {'textAlign': 'center'}),
        html.Br(),
        html.Br(),
        html.Div([
            html.Div([html.P('Most Read News Articles', style = {'fontSize': 35, 'fontFamily':'Arial', 'color':'black', 'textAlign':'center'}),
                dt.DataTable(id='news_articles_table_alex',
                                    columns=[{"name": i, "id": i} for i in ['Name', 'Content', 'URL', 'Reach']],
                                    page_size = 10,
                                    style_table = {'fontFamily':'Arial'},
                                    style_cell = {'overflow':'hidden', 'textOverflow':'ellipses', 'maxWidth':0, 'fontFamily':'Arial'},
                                    sort_action = 'native',
                                    #data=df_article.sort_values(by = ['reach'], ascending = False).to_dict('records'),
                                    export_format = 'xlsx')
            ])], style = {'width':'100%',
                        'textAlign':'center',
                        'fontFamily':'Arial'},
            className='news_articles_table'
        ),
        html.Br(),
        html.Br(),
        html.Div([
            html.Div([html.P('Most Engaging Social Posts', style = {'fontSize': 35, 'fontFamily':'Arial', 'color':'black', 'textAlign':'center'}),
                dt.DataTable(id='social_posts_table_alex',
                                    columns=[{"name": i, "id": i} for i in ['Name', 'Content', 'URL', 'Engagement']],
                                    page_size = 10,
                                    style_table = {'fontFamily':'Arial'},
                                    style_cell = {'overflow':'hidden', 'textOverflow':'ellipses', 'maxWidth':0, 'fontFamily':'Arial'},
                                    sort_action = 'native',
                                    #data=df_social.sort_values(by = ['engagement'], ascending = False).to_dict('records'),
                                    export_format = 'xlsx')
            ])], style = {'width':'100%',
                        'textAlign':'center',
                        'fontFamily':'Arial'},
            className='social_posts_table'
        ),
        html.Br(),
        html.Br(),
        html.Div(
            [
                html.Div([html.Div([
                    html.H3('Competitor & Peer CEO Landscape', style = {'fontSize':35, 'fontFamily':'Arial'})]),
                                html.Br(),
                                html.Br(),
                                html.Div([dbc.Row([
                                    dbc.Col([
                                        dbc.Card([
                                            html.Div(id = 'article_card'),
                                            html.P('Total Articles', style={'fontSize': 15, 'fontFamily':'Arial'})
                                        ], color = 'light', outline = True, style={'fontSize':25, 'padding': 5, 'fontFamily':'Arial'})]),
                                    dbc.Col([
                                    dbc.Card([
                                            html.Div(id = 'reach_card'),
                                            html.P('Total Reach', style={'fontSize': 15, 'fontFamily':'Arial'})
                                        ], color = 'light', outline = True, style={'fontSize':25, 'padding': 5, 'fontFamily':'Arial'})]),
                                    dbc.Col([
                                    dbc.Card([
                                            html.Div(id = 'social_card'),
                                            html.P('Total Social Posts', style={'fontSize': 15, 'fontFamily':'Arial'})
                                        ], color = 'light', outline = True, style={'fontSize':25, 'padding': 5, 'fontFamily':'Arial'})]),
                                    dbc.Col([
                                    dbc.Card([
                                            html.Div(id = 'sentiment_card'),
                                            html.P('Mentions with Positive or Neutral Sentiment', style={'fontSize': 15, 'fontFamily':'Arial'})
                                        ], color = 'light', outline = True, style={'fontSize':25, 'padding': 5, 'fontFamily':'Arial'})]),
                                    ])], style = {'textAlign':'center'})])], style = {'textAlign': 'center'}),
                html.Br(),
                html.Br(),
        html.Div([
                html.Div([html.H4('Visibility Over Time', style = {'fontSize':35, 'fontFamily':'Arial'}),
                        dcc.Graph(id='vis_time_graph',
                                 style = {'align':'center',
                                         'width':'100%',
                                         'fontFamily':'Arial'})                        
                    ], style = {'textAlign':'center'}),
                html.Div([html.H5('Share of Visibility', style = {'fontSize':35, 'fontFamily':'Arial'}),
                        dcc.Graph(id = 'share_vis_graph',
                                 style = {'align':'center',
                                         'width':'100%',
                                         'fontFamily':'Arial'}),
                    ], style = {'textAlign':'center'}),
            ],
        ),
        html.Br(),
        html.Br(),
        html.Div([
            html.Div([html.P('Most Read News Articles', style = {'fontSize': 35, 'fontFamily':'Arial', 'color':'black', 'textAlign':'center'}),
                dt.DataTable(id='news_articles_table_overall',
                                    columns=[{"name": i, "id": i} for i in ['Name', 'Content', 'URL', 'Reach']],
                                    page_size = 10,
                                    style_table = {'fontFamily':'Arial'},
                                    style_cell = {'overflow':'hidden', 'textOverflow':'ellipses', 'maxWidth':0, 'fontFamily':'Arial'},
                                    sort_action = 'native',
                                    #data=df_article.sort_values(by = ['reach'], ascending = False).to_dict('records'),
                                    export_format = 'xlsx')
            ])], style = {'width':'100%',
                        'textAlign':'center',
                        'fontFamily':'Arial'},
            className='news_articles_table'
        ),
        html.Br(),
        html.Br(),
        html.Div([
            html.Div([html.P('Most Engaging Social Posts', style = {'fontSize': 35, 'fontFamily':'Arial', 'color':'black', 'textAlign':'center'}),
                dt.DataTable(id='social_posts_table_overall',
                                    columns=[{"name": i, "id": i} for i in ['Name', 'Content', 'URL', 'Engagement']],
                                    page_size = 10,
                                    style_table = {'fontFamily':'Arial'},
                                    style_cell = {'overflow':'hidden', 'textOverflow':'ellipses', 'maxWidth':0, 'fontFamily':'Arial'},
                                    sort_action = 'native',
                                    #data=df_social.sort_values(by = ['engagement'], ascending = False).to_dict('records'),
                                    export_format = 'xlsx')
            ])], style = {'width':'100%',
                          'textAlign':'center',
                          'fontFamily':'Arial'},
            className='social_posts_table'
        ),
        html.Br(),
        html.Br()],
    id="mainContainer",
    style={
        "display": "flex",
        "flex-direction": "column",
        "padding":"2em"
    }
)

@app.callback(
    [Output('alex_coverage_card', 'children'),
     Output('alex_reach_card', 'children'),
     Output('alex_comms_pillars_coverage_card', 'children'),
     Output('alex_comms_pillars_reach_card', 'children'),
     Output('alex_sentiment_card', 'children')],
    [Input('date_picker', 'start_date'),
     Input('date_picker', 'end_date')]
)

def card_func(start_date, end_date):

    query1 = f"""
    WITH Main_Table AS (
        SELECT reach,
        engagement, 
        extra_author_attributes_name, 
        matched_profile, tags_customer, 
        tags_internal, 
        tags_marking, 
        title_snippet,
        post_type,
        source_type,
        url,
        content_snippet,
        sentiment,
        EXTRACT(DATE FROM TIMESTAMP_MILLIS(published)) AS published_date
        FROM `jnj-ooc.jnj_ooc_dashboard_data.jnj_ooc_dashboard_data`
        WHERE REGEXP_CONTAINS(matched_profile, r'Alex Gorsky')
    )

    SELECT COUNT(url) as count_url
    FROM Main_Table
    WHERE published_date >= '{start_date}'
        AND published_date <= '{end_date}'
    """
    
    query2 = f"""
    WITH Main_Table AS (
        SELECT reach,
        engagement, 
        extra_author_attributes_name, 
        matched_profile, tags_customer, 
        tags_internal, 
        tags_marking, 
        title_snippet,
        post_type,
        source_type,
        url,
        content_snippet,
        sentiment,
        EXTRACT(DATE FROM TIMESTAMP_MILLIS(published)) AS published_date
        FROM `jnj-ooc.jnj_ooc_dashboard_data.jnj_ooc_dashboard_data`
        WHERE REGEXP_CONTAINS(matched_profile, r'Alex Gorsky')
    )

    SELECT sum(REACH) as sum_reach
    FROM Main_Table
    WHERE published_date >= '{start_date}'
        AND published_date <= '{end_date}'
    """
    
    query3 = f"""
    WITH Main_Table AS (
        SELECT reach,
        engagement, 
        extra_author_attributes_name, 
        matched_profile, tags_customer, 
        tags_internal, 
        tags_marking, 
        title_snippet,
        post_type,
        source_type,
        url,
        content_snippet,
        sentiment,
        EXTRACT(DATE FROM TIMESTAMP_MILLIS(published)) AS published_date
        FROM `jnj-ooc.jnj_ooc_dashboard_data.jnj_ooc_dashboard_data`
        WHERE REGEXP_CONTAINS(matched_profile, r'Alex Gorsky')
            AND tags_customer IS NOT NULL
    )

    SELECT COUNT(url) as count_url
    FROM Main_Table
    WHERE published_date >= '{start_date}'
        AND published_date <= '{end_date}'
    """
    
    query4 = f"""
    WITH Main_Table AS (
        SELECT reach,
        engagement, 
        extra_author_attributes_name, 
        matched_profile, tags_customer, 
        tags_internal, 
        tags_marking, 
        title_snippet,
        post_type,
        source_type,
        url,
        content_snippet,
        sentiment,
        EXTRACT(DATE FROM TIMESTAMP_MILLIS(published)) AS published_date
        FROM `jnj-ooc.jnj_ooc_dashboard_data.jnj_ooc_dashboard_data`
        WHERE REGEXP_CONTAINS(matched_profile, r'Alex Gorsky')
            AND tags_customer IS NOT NULL
    )

    SELECT SUM(reach) as sum_reach
    FROM Main_Table
    WHERE published_date >= '{start_date}'
        AND published_date <= '{end_date}'
    """
    
    query5 = f"""
    WITH Main_Table AS (
        SELECT COUNT(sentiment) as sentiment_count
        FROM `jnj-ooc.jnj_ooc_dashboard_data.jnj_ooc_dashboard_data`
        WHERE REGEXP_CONTAINS(matched_profile, r'Alex Gorsky')
            AND sentiment >= 0
            AND EXTRACT(DATE FROM TIMESTAMP_MILLIS(published)) >= '{start_date}'
            AND EXTRACT(DATE FROM TIMESTAMP_MILLIS(published)) <= '{end_date}'
    ),

    Total_Table AS (
        SELECT COUNT(url) as total_count
        FROM `jnj-ooc.jnj_ooc_dashboard_data.jnj_ooc_dashboard_data`
        WHERE REGEXP_CONTAINS(matched_profile, r'Alex Gorsky')
            AND EXTRACT(DATE FROM TIMESTAMP_MILLIS(published)) >= '{start_date}'
            AND EXTRACT(DATE FROM TIMESTAMP_MILLIS(published)) <= '{end_date}'
    )

    SELECT sentiment_count/total_count as sentiment_pct
    FROM Main_Table, Total_Table
    """
    
    dff_total_count_url = gbq.read_gbq(query1, project_id = project_id, dialect = 'standard', credentials = credentials)
    dff_total_sum_reach = gbq.read_gbq(query2, project_id = project_id, dialect = 'standard', credentials = credentials)
    dff_comms_count_url = gbq.read_gbq(query3, project_id = project_id, dialect = 'standard', credentials = credentials)
    dff_comms_sum_reach = gbq.read_gbq(query4, project_id = project_id, dialect = 'standard', credentials = credentials)
    dff_total_sentiment = gbq.read_gbq(query5, project_id = project_id, dialect = 'standard', credentials = credentials)
    
    card1 = '{:,}'.format(dff_total_count_url['count_url'].sum())
    card2 = '{:,}'.format(dff_total_sum_reach['sum_reach'].sum())
    card3 = '{:,}'.format(dff_comms_count_url['count_url'].sum())
    card4 = '{:,}'.format(dff_comms_sum_reach['sum_reach'].sum())
    card5 = '{:.0%}'.format(dff_total_sentiment['sentiment_pct'].sum())
            
    
    return card1, card2, card3, card4, card5

@app.callback(
    Output('vis_message_graph_perc', 'figure'),
    [Input('date_picker', 'start_date'),
    Input('date_picker', 'end_date'),
    Input('comms_pillar_toggle', 'on')])

def vis_message_graph_perc_func(start_date, end_date, on):
    query1 = f"""
    WITH Main_Table AS (
        SELECT reach,
        engagement, 
        extra_author_attributes_name, 
        matched_profile, tags_customer, 
        tags_internal, 
        tags_marking, 
        title_snippet,
        post_type,
        source_type,
        url,
        content_snippet,
        sentiment,
        EXTRACT(DATE FROM TIMESTAMP_MILLIS(published)) AS published_date
        FROM `jnj-ooc.jnj_ooc_dashboard_data.jnj_ooc_dashboard_data`
        WHERE REGEXP_CONTAINS(matched_profile, r'Alex Gorsky')
            AND REGEXP_CONTAINS(tags_customer, r'Frontline HCPs')
    )

    SELECT COUNT(url) as count_url
    FROM Main_Table
    WHERE published_date >= '{start_date}'
        AND published_date <= '{end_date}'
    """

    query2 = f"""
    WITH Main_Table AS (
        SELECT reach,
        engagement, 
        extra_author_attributes_name, 
        matched_profile, tags_customer, 
        tags_internal, 
        tags_marking, 
        title_snippet,
        post_type,
        source_type,
        url,
        content_snippet,
        sentiment,
        EXTRACT(DATE FROM TIMESTAMP_MILLIS(published)) AS published_date
        FROM `jnj-ooc.jnj_ooc_dashboard_data.jnj_ooc_dashboard_data`
        WHERE REGEXP_CONTAINS(matched_profile, r'Alex Gorsky')
            AND REGEXP_CONTAINS(tags_customer, r'Innovation')
    )

    SELECT COUNT(url) as count_url
    FROM Main_Table
    WHERE published_date >= '{start_date}'
        AND published_date <= '{end_date}'
    """
    
    query3 = f"""
    WITH Main_Table AS (
        SELECT reach,
        engagement, 
        extra_author_attributes_name, 
        matched_profile, tags_customer, 
        tags_internal, 
        tags_marking, 
        title_snippet,
        post_type,
        source_type,
        url,
        content_snippet,
        sentiment,
        EXTRACT(DATE FROM TIMESTAMP_MILLIS(published)) AS published_date
        FROM `jnj-ooc.jnj_ooc_dashboard_data.jnj_ooc_dashboard_data`
        WHERE REGEXP_CONTAINS(matched_profile, r'Alex Gorsky')
            AND REGEXP_CONTAINS(tags_customer, r'Values')
    )

    SELECT COUNT(url) as count_url
    FROM Main_Table
    WHERE published_date >= '{start_date}'
        AND published_date <= '{end_date}'
    """
    
    query4 = f"""
    WITH Main_Table AS (
        SELECT reach,
        engagement, 
        extra_author_attributes_name, 
        matched_profile, tags_customer, 
        tags_internal, 
        tags_marking, 
        title_snippet,
        post_type,
        source_type,
        url,
        content_snippet,
        sentiment,
        EXTRACT(DATE FROM TIMESTAMP_MILLIS(published)) AS published_date
        FROM `jnj-ooc.jnj_ooc_dashboard_data.jnj_ooc_dashboard_data`
        WHERE REGEXP_CONTAINS(matched_profile, r'Alex Gorsky')
            AND REGEXP_CONTAINS(tags_customer, r'Health Equity')
    )

    SELECT COUNT(url) as count_url
    FROM Main_Table
    WHERE published_date >= '{start_date}'
        AND published_date <= '{end_date}'
    """
    if on == True:
        query5 = f"""
        WITH Main_Table AS (
            SELECT reach,
            engagement, 
            extra_author_attributes_name, 
            matched_profile, tags_customer, 
            tags_internal, 
            tags_marking, 
            title_snippet,
            post_type,
            source_type,
            url,
            content_snippet,
            sentiment,
            EXTRACT(DATE FROM TIMESTAMP_MILLIS(published)) AS published_date
            FROM `jnj-ooc.jnj_ooc_dashboard_data.jnj_ooc_dashboard_data`
            WHERE REGEXP_CONTAINS(matched_profile, r'Alex Gorsky')
                AND tags_customer IS NOT NULL
        )

        SELECT COUNT(url) as count_url
        FROM Main_Table
        WHERE published_date >= '{start_date}'
            AND published_date <= '{end_date}'
        """
        
    else:
        query5 = f"""
        WITH Main_Table AS (
            SELECT reach,
            engagement, 
            extra_author_attributes_name, 
            matched_profile, tags_customer, 
            tags_internal, 
            tags_marking, 
            title_snippet,
            post_type,
            source_type,
            url,
            content_snippet,
            sentiment,
            EXTRACT(DATE FROM TIMESTAMP_MILLIS(published)) AS published_date
            FROM `jnj-ooc.jnj_ooc_dashboard_data.jnj_ooc_dashboard_data`
            WHERE REGEXP_CONTAINS(matched_profile, r'Alex Gorsky')
        )

        SELECT COUNT(url) as count_url
        FROM Main_Table
        WHERE published_date >= '{start_date}'
            AND published_date <= '{end_date}'
        """
        
    num_frontline = gbq.read_gbq(query1, project_id = project_id, dialect = 'standard', credentials = credentials)
    num_innovation = gbq.read_gbq(query2, project_id = project_id, dialect = 'standard', credentials = credentials)
    num_values = gbq.read_gbq(query3, project_id = project_id, dialect = 'standard', credentials = credentials)
    num_health = gbq.read_gbq(query4, project_id = project_id, dialect = 'standard', credentials = credentials)        
    num_total = gbq.read_gbq(query5, project_id = project_id, dialect = 'standard', credentials = credentials)

    
    fig = px.bar(x=['Frontline HCPs','Innovation','Values','Health Equity'],
                 y=[num_frontline['count_url'].sum()/num_total['count_url'].sum(),
                    num_innovation['count_url'].sum()/num_total['count_url'].sum(),
                    num_values['count_url'].sum()/num_total['count_url'].sum(),
                    num_health['count_url'].sum()/num_total['count_url'].sum()], 
                 text=[num_frontline['count_url'].sum()/num_total['count_url'].sum(),
                       num_innovation['count_url'].sum()/num_total['count_url'].sum(),
                       num_values['count_url'].sum()/num_total['count_url'].sum(),
                       num_health['count_url'].sum()/num_total['count_url'].sum()],
                labels={'x':'Topics', 'y':'Percentages'},
                color = ['Frontline HCPs', 'Innovation', 'Values', 'Health Equity'],
                color_discrete_map = {
                    'Frontline HCPs':'#00008B',
                    'Innovation':'#FF00FF',
                    'Values':'#1dcccf',
                    'Health Equity':'#ff0000'
	       })
    fig.update_traces(texttemplate='%{text:.0%}', textposition='outside')
        
    return fig

@app.callback(
    Output('speaking_engagements_graph', 'figure'),
    [Input('date_picker', 'start_date'),
     Input('date_picker', 'end_date')]
)

def engagements_graph_func(start_date, end_date):
    dff_engagements = df_engagements

    if start_date is not None: # add start time
        dff_engagements = dff_engagements[dff_engagements['Date'] >= start_date]

    if end_date is not None: # add end time
        dff_engagements = dff_engagements[dff_engagements['Date'] <= end_date]

    fig = px.pie(dff_engagements, values = 'Count', names = 'Internal/External')
    
    return fig

@app.callback(
    Output('eng_aud_graph', 'figure'),
    [Input('date_picker', 'start_date'),
     Input('date_picker', 'end_date')]
)

def eng_aud_graph_func(start_date, end_date):
    dff_engagements = df_engagements

    if start_date is not None: # add start time
        dff_engagements = dff_engagements[dff_engagements['Date'] >= start_date]

    if end_date is not None: # add end time
        dff_engagements = dff_engagements[dff_engagements['Date'] <= end_date]
    
    fig = px.bar(x = ['Employees', 'Stakebrokers', 'Gen Pop', 'HCPs', 'Investors'],
                 y = [dff_engagements[dff_engagements['Audience'] == 'Employees']['Audience'].count(),
                      dff_engagements[dff_engagements['Audience'] == 'Stakebrokers']['Audience'].count(),
                      dff_engagements[dff_engagements['Audience'] == 'Gen Pop']['Audience'].count(),
                      dff_engagements[dff_engagements['Audience'] == 'HCPs']['Audience'].count(),
                      dff_engagements[dff_engagements['Audience'] == 'Investors']['Audience'].count()],
                 text = [dff_engagements[dff_engagements['Audience'] == 'Employees']['Audience'].count(),
                         dff_engagements[dff_engagements['Audience'] == 'Stakebrokers']['Audience'].count(),
                         dff_engagements[dff_engagements['Audience'] == 'Gen Pop']['Audience'].count(),
                         dff_engagements[dff_engagements['Audience'] == 'HCPs']['Audience'].count(),
                         dff_engagements[dff_engagements['Audience'] == 'Investors']['Audience'].count()],
                 labels = {'x':'Audience Type', 
                           'y':'Count'},
                 color = ['Employees', 'Stakebrokers', 'Gen Pop', 'HCPs', 'Investors'],
                 color_discrete_map = {
                    'Employees':'#00008B',
                    'Stakebrokers':'#FF00FF',
                    'Gen Pop':'#1dcccf',
                    'HCPs':'#ff8800',
                    'Investors':'#8600c9'
                })
    fig.update_traces(textposition = 'outside')
    
    return fig

@app.callback(
    [Output('linkedin_posts_card', 'children'),
     Output('linkedin_engagements_card', 'children'),
     Output('linkedin_post_views_card', 'children'),
     Output('linkedin_reshares_card', 'children'),
     Output('linkedin_likes_card', 'children'),
     Output('linkedin_comments_card', 'children')],
    [Input('date_picker', 'start_date'),
     Input('date_picker', 'end_date')]
)

def linkedin_card_func(start_date, end_date):
    dff_linkedin = df_linkedin

    if start_date is not None: # add start time
        dff_linkedin = dff_linkedin[dff_linkedin['Date'] >= start_date]
    if end_date is not None: # add end time
        dff_linkedin = dff_linkedin[dff_linkedin['Date'] <= end_date]
    
    card1 = '{:,}'.format(dff_linkedin['Link'].count())
    card2 = '{:,}'.format(dff_linkedin[['Likes', 'Comments', 'Reshares']].sum().sum())
    card3 = '{:,}'.format(dff_linkedin['Views'].sum())
    card4 = '{:,}'.format(dff_linkedin['Reshares'].sum())
    card5 = '{:,}'.format(dff_linkedin['Likes'].sum())
    card6 = '{:,}'.format(dff_linkedin['Comments'].sum())
    
    return card1, card2, card3, card4, card5, card6

@app.callback(
    [Output('blog_posts_card', 'children'),
     Output('blog_pageviews_card', 'children'),
     Output('blog_sessions_card', 'children'),
     Output('blog_likes_card', 'children'),
     Output('blog_comments_card', 'children'),
     Output('blog_CTR_card', 'children'),
     Output('blog_table', 'data')],
    [Input('date_picker', 'start_date'),
     Input('date_picker', 'end_date')]
)

def blogs_func(start_date, end_date):
    dff_blogs = df_blogs

    if start_date is not None: # add start time
        dff_blogs = dff_blogs[dff_blogs['Date of Posting'] >= start_date]
    if end_date is not None: # add end time
        dff_blogs = dff_blogs[dff_blogs['Date of Posting'] <= end_date]
    
    card1 = '{:,}'.format(dff_blogs['Blog Title'].count())
    card2 = '{:,}'.format(dff_blogs['Pageviews'].sum())
    card3 = '{:,}'.format(dff_blogs['Sessions'].sum())
    card4 = '{:,}'.format(dff_blogs['Likes'].sum())
    card5 = '{:,}'.format(dff_blogs['Comments'].sum())
    card6 = '{:.0%}'.format(dff_blogs['Unique Email Clickthroughs'].sum()/dff_blogs['Unique Email Opens'].sum())
    
    return card1, card2, card3, card4, card5, card6, dff_blogs.to_dict('records')

@app.callback(
    [Output('news_articles_table_alex', 'data'),
     Output('social_posts_table_alex', 'data'),
     Output('speaking_engagements_table', 'data')],
    [Input('date_picker', 'start_date'),
     Input('date_picker', 'end_date'),
     Input('comms_pillar_toggle', 'on')]
)

def alex_tables_func(start_date, end_date, on):
    dff_engagements = df_engagements

    if start_date is not None: # add start time
        dff_engagements = dff_engagements[dff_engagements['Date'] >= start_date]
        
    if end_date is not None: # add end time
        dff_engagements = dff_engagements[dff_engagements['Date'] <= end_date]
    
    if on == True:
        query1 = f"""
        WITH Main_Table AS (
            SELECT reach,
            engagement, 
            extra_author_attributes_name, 
            matched_profile, tags_customer, 
            tags_internal, 
            tags_marking, 
            title_snippet,
            post_type,
            source_type,
            url,
            content_snippet,
            sentiment,
            EXTRACT(DATE FROM TIMESTAMP_MILLIS(published)) AS published_date
            FROM `jnj-ooc.jnj_ooc_dashboard_data.jnj_ooc_dashboard_data`
            WHERE REGEXP_CONTAINS(matched_profile, r'Alex Gorsky')
                AND tags_customer IS NOT NULL
                AND REGEXP_CONTAINS(source_type, r'ONLINENEWS') OR REGEXP_CONTAINS(source_type, r'BLOG')
        )

        SELECT extra_author_attributes_name as Name,
            content_snippet as Content,
            url as URL,
            reach as Reach
        FROM Main_Table
        WHERE published_date >= '{start_date}'
            AND published_date <= '{end_date}'
        ORDER BY Reach DESC
        """
        
        query2 = f"""
        WITH Main_Table AS (
            SELECT reach,
            engagement, 
            extra_author_attributes_name, 
            matched_profile, tags_customer, 
            tags_internal, 
            tags_marking, 
            title_snippet,
            post_type,
            source_type,
            url,
            content_snippet,
            sentiment,
            EXTRACT(DATE FROM TIMESTAMP_MILLIS(published)) AS published_date
            FROM `jnj-ooc.jnj_ooc_dashboard_data.jnj_ooc_dashboard_data`
            WHERE REGEXP_CONTAINS(matched_profile, r'Alex Gorsky')
                AND tags_customer IS NOT NULL
                AND REGEXP_CONTAINS(source_type, r'SOCIALMEDIA') OR REGEXP_CONTAINS(source_type, r'MESSAGEBOARD')
        )

        SELECT extra_author_attributes_name as Name,
            content_snippet as Content,
            url as URL,
            engagement as Engagement
        FROM Main_Table
        WHERE published_date >= '{start_date}'
            AND published_date <= '{end_date}'
        ORDER BY Engagement DESC
        """
    else:
        query1 = f"""
        WITH Main_Table AS (
            SELECT reach,
            engagement, 
            extra_author_attributes_name, 
            matched_profile, tags_customer, 
            tags_internal, 
            tags_marking, 
            title_snippet,
            post_type,
            source_type,
            url,
            content_snippet,
            sentiment,
            EXTRACT(DATE FROM TIMESTAMP_MILLIS(published)) AS published_date
            FROM `jnj-ooc.jnj_ooc_dashboard_data.jnj_ooc_dashboard_data`
            WHERE REGEXP_CONTAINS(matched_profile, r'Alex Gorsky')
                AND REGEXP_CONTAINS(source_type, r'ONLINENEWS') OR REGEXP_CONTAINS(source_type, r'BLOG')
        )

        SELECT extra_author_attributes_name as Name,
            content_snippet as Content,
            url as URL,
            reach as Reach
        FROM Main_Table
        WHERE published_date >= '{start_date}'
            AND published_date <= '{end_date}'
        ORDER BY Reach DESC
        """

        query2 = f"""
        WITH Main_Table AS (
            SELECT reach,
            engagement, 
            extra_author_attributes_name, 
            matched_profile, tags_customer, 
            tags_internal, 
            tags_marking, 
            title_snippet,
            post_type,
            source_type,
            url,
            content_snippet,
            sentiment,
            EXTRACT(DATE FROM TIMESTAMP_MILLIS(published)) AS published_date
            FROM `jnj-ooc.jnj_ooc_dashboard_data.jnj_ooc_dashboard_data`
            WHERE REGEXP_CONTAINS(matched_profile, r'Alex Gorsky')
                AND REGEXP_CONTAINS(source_type, r'SOCIALMEDIA') OR REGEXP_CONTAINS(source_type, r'MESSAGEBOARD')
        )

        SELECT extra_author_attributes_name as Name,
            content_snippet as Content,
            url as URL,
            engagement as Engagement
        FROM Main_Table
        WHERE published_date >= '{start_date}'
            AND published_date <= '{end_date}'
        ORDER BY Engagement DESC
        """
    
    dff_article = gbq.read_gbq(query1, project_id = project_id, dialect = 'standard', credentials = credentials)
    dff_social = gbq.read_gbq(query2, project_id = project_id, dialect = 'standard', credentials = credentials)
    
    return dff_article.to_dict('records'), dff_social.to_dict('records'), dff_engagements.to_dict('records')

@app.callback(
    Output('vis_time_graph', 'figure'),
    [Input('exec_dropdown', 'value'),
    Input('date_picker', 'start_date'),
    Input('date_picker', 'end_date'),
    Input('comms_pillar_toggle', 'on')])

def vis_time_graph_func(value, start_date, end_date, on):
    if on == True:
        query1 = f'''
        WITH Main_Table AS (
            SELECT reach,
            engagement, 
            extra_author_attributes_name, 
            matched_profile, 
            tags_customer, 
            tags_internal, 
            tags_marking, 
            title_snippet,
            post_type,
            source_type,
            url,
            content_snippet,
            sentiment,
            EXTRACT(DATE FROM TIMESTAMP_MILLIS(published)) AS published_date,
            SPLIT(matched_profile, ',') as mention_name,
            FROM `jnj-ooc.jnj_ooc_dashboard_data.jnj_ooc_dashboard_data`
            WHERE tags_customer IS NOT NULL
        ),

        Match_Table AS (
            SELECT *
            FROM UNNEST({value}) as exec_list
        ),

        Mentions_Table AS (
        SELECT reach,
            published_date,
            TRIM(REGEXP_EXTRACT(flattened_mentions, r'/([^/]+)/?$')) as name_list
        FROM Main_Table
        CROSS JOIN UNNEST(mention_name) AS flattened_mentions
        WHERE published_date >= '{start_date}'
            AND published_date <= '{end_date}'
        )

        SELECT published_date,
            name_list,
            SUM(reach)
            OVER(
                PARTITION BY name_list
                ORDER BY name_list, published_date ASC
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                ) as cumsum_reach
        FROM Mentions_Table
        INNER JOIN Match_Table ON Mentions_Table.name_list = Match_Table.exec_list
        '''
    else:
        query1 = f'''
        WITH Main_Table AS (
            SELECT reach,
            engagement, 
            extra_author_attributes_name, 
            matched_profile, 
            tags_customer, 
            tags_internal, 
            tags_marking, 
            title_snippet,
            post_type,
            source_type,
            url,
            content_snippet,
            sentiment,
            EXTRACT(DATE FROM TIMESTAMP_MILLIS(published)) AS published_date,
            SPLIT(matched_profile, ',') as mention_name,
            FROM `jnj-ooc.jnj_ooc_dashboard_data.jnj_ooc_dashboard_data`
        ),

        Match_Table AS (
            SELECT *
            FROM UNNEST({value}) as exec_list
        ),

        Mentions_Table AS (
        SELECT reach,
            published_date,
            TRIM(REGEXP_EXTRACT(flattened_mentions, r'/([^/]+)/?$')) as name_list
        FROM Main_Table
        CROSS JOIN UNNEST(mention_name) AS flattened_mentions
        WHERE published_date >= '{start_date}'
            AND published_date <= '{end_date}'
        )

        SELECT published_date,
            name_list,
            SUM(reach)
            OVER(
                PARTITION BY name_list
                ORDER BY name_list, published_date ASC
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                ) as cumsum_reach
        FROM Mentions_Table
        INNER JOIN Match_Table ON Mentions_Table.name_list = Match_Table.exec_list
        '''
    
    dff_grouped = gbq.read_gbq(query1, project_id = project_id, dialect = 'standard', credentials = credentials)
    fig = px.line(dff_grouped, x = 'published_date', y = 'cumsum_reach', color = 'name_list', labels = {'published_date':'Date Published', 'cumsum_reach':'Cummulative Reach', 'name_list':'Executive'}, color_discrete_map = colors)
    
    return fig

@app.callback(
     Output('share_vis_graph', 'figure'),
     [Input('exec_dropdown', 'value'),
     Input('date_picker', 'start_date'),
     Input('date_picker', 'end_date'),
     Input('comms_pillar_toggle', 'on')])

def share_vis_graphvis_time_graph_func(value, start_date, end_date, on):   
    if on == True:
        query1 = f'''
        WITH Main_Table AS (
            SELECT reach,
            engagement, 
            extra_author_attributes_name, 
            matched_profile, 
            tags_customer, 
            tags_internal, 
            tags_marking, 
            title_snippet,
            post_type,
            source_type,
            url,
            content_snippet,
            sentiment,
            EXTRACT(DATE FROM TIMESTAMP_MILLIS(published)) AS published_date,
            SPLIT(matched_profile, ',') as mention_name,
            FROM `jnj-ooc.jnj_ooc_dashboard_data.jnj_ooc_dashboard_data`
            WHERE tags_customer IS NOT NULL
        ),
        
        Sub_Main_Table AS (
            SELECT *
            FROM Main_Table
            WHERE published_date >= '{start_date}'
                AND published_date <= '{end_date}'
        ),

        Match_Table AS (
            SELECT *
            FROM UNNEST({value}) as exec_list
        ),

        Mentions_Table AS (
        SELECT SUM(reach) as sum_reach,
            TRIM(REGEXP_EXTRACT(flattened_mentions, r'/([^/]+)/?$')) as name_list
        FROM Sub_Main_Table
        CROSS JOIN UNNEST(mention_name) AS flattened_mentions
        GROUP BY name_list
        )

        SELECT *
        FROM Mentions_Table
        INNER JOIN Match_Table ON Mentions_Table.name_list = Match_Table.exec_list
        '''
    else:
        query1 = f'''
        WITH Main_Table AS (
            SELECT reach,
            engagement, 
            extra_author_attributes_name, 
            matched_profile, 
            tags_customer, 
            tags_internal, 
            tags_marking, 
            title_snippet,
            post_type,
            source_type,
            url,
            content_snippet,
            sentiment,
            EXTRACT(DATE FROM TIMESTAMP_MILLIS(published)) AS published_date,
            SPLIT(matched_profile, ',') as mention_name,
            FROM `jnj-ooc.jnj_ooc_dashboard_data.jnj_ooc_dashboard_data`
        ),
        
        Sub_Main_Table AS (
            SELECT *
            FROM Main_Table
            WHERE published_date >= '{start_date}'
                AND published_date <= '{end_date}'
        ),

        Match_Table AS (
            SELECT *
            FROM UNNEST({value}) as exec_list
        ),

        Mentions_Table AS (
        SELECT SUM(reach) as sum_reach,
            TRIM(REGEXP_EXTRACT(flattened_mentions, r'/([^/]+)/?$')) as name_list
        FROM Sub_Main_Table
        CROSS JOIN UNNEST(mention_name) AS flattened_mentions
        GROUP BY name_list
        )

        SELECT *
        FROM Mentions_Table
        INNER JOIN Match_Table ON Mentions_Table.name_list = Match_Table.exec_list
        '''
        
    dff_grouped = gbq.read_gbq(query1, project_id = project_id, dialect = 'standard', credentials = credentials)
    fig = px.bar(dff_grouped, x = 'name_list', y = 'sum_reach', labels = {'name_list':'Executive', 'sum_reach':'Total Reach'}, color = 'name_list', color_discrete_map = colors)
    fig.update_layout(barmode='stack', xaxis={'categoryorder':'total descending'})
    
    return fig

@app.callback(
    [Output('article_card', 'children'),
     Output('reach_card', 'children'),
     Output('social_card', 'children'),
     Output('sentiment_card', 'children')],
    [Input('exec_dropdown', 'value'),
     Input('date_picker', 'start_date'),
     Input('date_picker', 'end_date'),
     Input('comms_pillar_toggle', 'on')]
)

def card_func(value, start_date, end_date, on):
    if on == True:
        query1 = f'''
        WITH Main_Table AS (
            SELECT reach,
            engagement, 
            extra_author_attributes_name, 
            matched_profile, 
            tags_customer, 
            tags_internal, 
            tags_marking, 
            title_snippet,
            post_type,
            source_type,
            url,
            content_snippet,
            sentiment,
            EXTRACT(DATE FROM TIMESTAMP_MILLIS(published)) AS published_date,
            SPLIT(matched_profile, ',') as mention_name,
            FROM `jnj-ooc.jnj_ooc_dashboard_data.jnj_ooc_dashboard_data`
            WHERE tags_customer IS NOT NULL
        ),
        
        Sub_Main_Table AS (
            SELECT *
            FROM Main_Table
            WHERE published_date >= '{start_date}'
                AND published_date <= '{end_date}'
        ),

        Match_Table AS (
            SELECT *
            FROM UNNEST({value}) as exec_list
        ),

        Mentions_Table AS (
        SELECT reach,
            TRIM(REGEXP_EXTRACT(flattened_mentions, r'/([^/]+)/?$')) as name_list
        FROM Sub_Main_Table
        CROSS JOIN UNNEST(mention_name) AS flattened_mentions
        )

        SELECT SUM(reach) as sum_reach
        FROM Mentions_Table
        INNER JOIN Match_Table ON Mentions_Table.name_list = Match_Table.exec_list
        '''
        
        query2 = f'''
        WITH Main_Table AS (
            SELECT reach,
            engagement, 
            extra_author_attributes_name, 
            matched_profile, 
            tags_customer, 
            tags_internal, 
            tags_marking, 
            title_snippet,
            post_type,
            source_type,
            url,
            content_snippet,
            sentiment,
            EXTRACT(DATE FROM TIMESTAMP_MILLIS(published)) AS published_date,
            SPLIT(matched_profile, ',') as mention_name,
            FROM `jnj-ooc.jnj_ooc_dashboard_data.jnj_ooc_dashboard_data`
            WHERE tags_customer IS NOT NULL
                AND REGEXP_CONTAINS(source_type, r'ONLINENEWS') OR REGEXP_CONTAINS(source_type, r'BLOG')
        ),

        Sub_Main_Table AS (
            SELECT *
            FROM Main_Table
            WHERE published_date >= '{start_date}'
                AND published_date <= '{end_date}'
        ),

        Match_Table AS (
            SELECT *
            FROM UNNEST({value}) as exec_list
        ),

        Mentions_Table AS (
        SELECT url,
            TRIM(REGEXP_EXTRACT(flattened_mentions, r'/([^/]+)/?$')) as name_list
        FROM Sub_Main_Table
        CROSS JOIN UNNEST(mention_name) AS flattened_mentions
        )

        SELECT COUNT(url) as count_url
        FROM Mentions_Table
        INNER JOIN Match_Table ON Mentions_Table.name_list = Match_Table.exec_list
        '''
    
        query3 = f'''
        WITH Main_Table AS (
            SELECT reach,
            engagement, 
            extra_author_attributes_name, 
            matched_profile, 
            tags_customer, 
            tags_internal, 
            tags_marking, 
            title_snippet,
            post_type,
            source_type,
            url,
            content_snippet,
            sentiment,
            EXTRACT(DATE FROM TIMESTAMP_MILLIS(published)) AS published_date,
            SPLIT(matched_profile, ',') as mention_name,
            FROM `jnj-ooc.jnj_ooc_dashboard_data.jnj_ooc_dashboard_data`
            WHERE tags_customer IS NOT NULL
                AND REGEXP_CONTAINS(source_type, r'SOCIALMEDIA') OR REGEXP_CONTAINS(source_type, r'MESSAGEBOARD')
        ),

        Sub_Main_Table AS (
            SELECT *
            FROM Main_Table
            WHERE published_date >= '{start_date}'
                AND published_date <= '{end_date}'
        ),

        Match_Table AS (
            SELECT *
            FROM UNNEST({value}) as exec_list
        ),

        Mentions_Table AS (
        SELECT url,
            TRIM(REGEXP_EXTRACT(flattened_mentions, r'/([^/]+)/?$')) as name_list
        FROM Sub_Main_Table
        CROSS JOIN UNNEST(mention_name) AS flattened_mentions
        )

        SELECT COUNT(url) as count_url
        FROM Mentions_Table
        INNER JOIN Match_Table ON Mentions_Table.name_list = Match_Table.exec_list
        '''

        query4 = f"""
        WITH Main_Table AS (
            SELECT reach,
            engagement, 
            extra_author_attributes_name, 
            matched_profile, 
            tags_customer, 
            tags_internal, 
            tags_marking, 
            title_snippet,
            post_type,
            source_type,
            url,
            content_snippet,
            sentiment,
            EXTRACT(DATE FROM TIMESTAMP_MILLIS(published)) AS published_date,
            SPLIT(matched_profile, ',') as mention_name,
            FROM `jnj-ooc.jnj_ooc_dashboard_data.jnj_ooc_dashboard_data`
            WHERE tags_customer IS NOT NULL
                AND sentiment >= 0
        ),

        Sub_Main_Table AS (
            SELECT *
            FROM Main_Table
            WHERE published_date >= '{start_date}'
                AND published_date <= '{end_date}'
        ),

            Total_Table AS (
                SELECT reach,
                engagement, 
                extra_author_attributes_name, 
                matched_profile, 
                tags_customer, 
                tags_internal, 
                tags_marking, 
                title_snippet,
                post_type,
                source_type,
                url,
                content_snippet,
                sentiment,
                EXTRACT(DATE FROM TIMESTAMP_MILLIS(published)) AS published_date,
                SPLIT(matched_profile, ',') as mention_name,
                FROM `jnj-ooc.jnj_ooc_dashboard_data.jnj_ooc_dashboard_data`
                WHERE tags_customer IS NOT NULL
            ),

        Sub_Total_Table AS (
            SELECT *
            FROM Main_Table
            WHERE published_date >= '{start_date}'
                AND published_date <= '{end_date}'
        ),

        Match_Table AS (
            SELECT *
            FROM UNNEST({value}) as exec_list
        ),

        Main_Mentions_Table AS (
            SELECT COUNT(url) as sentiment_count,
                TRIM(REGEXP_EXTRACT(flattened_mentions, r'/([^/]+)/?$')) as name_list
            FROM Sub_Main_Table
            CROSS JOIN UNNEST(mention_name) AS flattened_mentions
            GROUP BY name_list
        ),

        Final_Main_Table AS (
            SELECT *
            FROM Main_Mentions_Table
            INNER JOIN Match_Table ON Main_Mentions_Table.name_list = Match_Table.exec_list
        ),

        Total_Mentions_Table AS (
            SELECT COUNT(url) as total_count,
            TRIM(REGEXP_EXTRACT(flattened_mentions, r'/([^/]+)/?$')) as name_list
            FROM Sub_Total_Table
            CROSS JOIN UNNEST(mention_name) AS flattened_mentions
            GROUP BY name_list
        ),

        Final_Total_Table AS (
            SELECT *
            FROM Total_Mentions_Table
            INNER JOIN Match_Table ON Total_Mentions_Table.name_list = Match_Table.exec_list
        )

        SELECT SUM(sentiment_count)/SUM(total_count) as sentiment_pct
        FROM Final_Main_Table, Final_Total_Table
        """
    
    else:
        query1 = f'''
        WITH Main_Table AS (
            SELECT reach,
            engagement, 
            extra_author_attributes_name, 
            matched_profile, 
            tags_customer, 
            tags_internal, 
            tags_marking, 
            title_snippet,
            post_type,
            source_type,
            url,
            content_snippet,
            sentiment,
            EXTRACT(DATE FROM TIMESTAMP_MILLIS(published)) AS published_date,
            SPLIT(matched_profile, ',') as mention_name,
            FROM `jnj-ooc.jnj_ooc_dashboard_data.jnj_ooc_dashboard_data`
        ),

        Sub_Main_Table AS (
            SELECT *
            FROM Main_Table
            WHERE published_date >= '{start_date}'
                AND published_date <= '{end_date}'
        ),

        Match_Table AS (
            SELECT *
            FROM UNNEST({value}) as exec_list
        ),

        Mentions_Table AS (
        SELECT reach,
            TRIM(REGEXP_EXTRACT(flattened_mentions, r'/([^/]+)/?$')) as name_list
        FROM Sub_Main_Table
        CROSS JOIN UNNEST(mention_name) AS flattened_mentions
        )

        SELECT SUM(reach) as sum_reach
        FROM Mentions_Table
        INNER JOIN Match_Table ON Mentions_Table.name_list = Match_Table.exec_list
        '''
        
        query2 = f'''
        WITH Main_Table AS (
            SELECT reach,
            engagement, 
            extra_author_attributes_name, 
            matched_profile, 
            tags_customer, 
            tags_internal, 
            tags_marking, 
            title_snippet,
            post_type,
            source_type,
            url,
            content_snippet,
            sentiment,
            EXTRACT(DATE FROM TIMESTAMP_MILLIS(published)) AS published_date,
            SPLIT(matched_profile, ',') as mention_name,
            FROM `jnj-ooc.jnj_ooc_dashboard_data.jnj_ooc_dashboard_data`
            WHERE REGEXP_CONTAINS(source_type, r'ONLINENEWS') OR REGEXP_CONTAINS(source_type, r'BLOG')
        ),

        Sub_Main_Table AS (
            SELECT *
            FROM Main_Table
            WHERE published_date >= '{start_date}'
                AND published_date <= '{end_date}'
        ),

        Match_Table AS (
            SELECT *
            FROM UNNEST({value}) as exec_list
        ),

        Mentions_Table AS (
        SELECT url,
            TRIM(REGEXP_EXTRACT(flattened_mentions, r'/([^/]+)/?$')) as name_list
        FROM Sub_Main_Table
        CROSS JOIN UNNEST(mention_name) AS flattened_mentions
        )

        SELECT COUNT(url) as count_url
        FROM Mentions_Table
        INNER JOIN Match_Table ON Mentions_Table.name_list = Match_Table.exec_list
        '''

        query3 = f'''
        WITH Main_Table AS (
            SELECT reach,
            engagement, 
            extra_author_attributes_name, 
            matched_profile, 
            tags_customer, 
            tags_internal, 
            tags_marking, 
            title_snippet,
            post_type,
            source_type,
            url,
            content_snippet,
            sentiment,
            EXTRACT(DATE FROM TIMESTAMP_MILLIS(published)) AS published_date,
            SPLIT(matched_profile, ',') as mention_name,
            FROM `jnj-ooc.jnj_ooc_dashboard_data.jnj_ooc_dashboard_data`
            WHERE REGEXP_CONTAINS(source_type, r'SOCIALMEDIA') OR REGEXP_CONTAINS(source_type, r'MESSAGEBOARD')
        ),

        Sub_Main_Table AS (
            SELECT *
            FROM Main_Table
            WHERE published_date >= '{start_date}'
                AND published_date <= '{end_date}'
        ),

        Match_Table AS (
            SELECT *
            FROM UNNEST({value}) as exec_list
        ),

        Mentions_Table AS (
        SELECT url,
            TRIM(REGEXP_EXTRACT(flattened_mentions, r'/([^/]+)/?$')) as name_list
        FROM Sub_Main_Table
        CROSS JOIN UNNEST(mention_name) AS flattened_mentions
        )

        SELECT COUNT(url) as count_url
        FROM Mentions_Table
        INNER JOIN Match_Table ON Mentions_Table.name_list = Match_Table.exec_list
        '''    

        query4 = f"""
        WITH Main_Table AS (
            SELECT reach,
            engagement, 
            extra_author_attributes_name, 
            matched_profile, 
            tags_customer, 
            tags_internal, 
            tags_marking, 
            title_snippet,
            post_type,
            source_type,
            url,
            content_snippet,
            sentiment,
            EXTRACT(DATE FROM TIMESTAMP_MILLIS(published)) AS published_date,
            SPLIT(matched_profile, ',') as mention_name,
            FROM `jnj-ooc.jnj_ooc_dashboard_data.jnj_ooc_dashboard_data`
                WHERE sentiment >= 0
        ),

        Sub_Main_Table AS (
            SELECT *
            FROM Main_Table
            WHERE published_date >= '{start_date}'
                AND published_date <= '{end_date}'
        ),

            Total_Table AS (
                SELECT reach,
                engagement, 
                extra_author_attributes_name, 
                matched_profile, 
                tags_customer, 
                tags_internal, 
                tags_marking, 
                title_snippet,
                post_type,
                source_type,
                url,
                content_snippet,
                sentiment,
                EXTRACT(DATE FROM TIMESTAMP_MILLIS(published)) AS published_date,
                SPLIT(matched_profile, ',') as mention_name,
                FROM `jnj-ooc.jnj_ooc_dashboard_data.jnj_ooc_dashboard_data`
            ),

            Sub_Total_Table AS (
                SELECT *
                FROM Main_Table
                WHERE published_date >= '{start_date}'
                    AND published_date <= '{end_date}'
            ),

            Match_Table AS (
                SELECT *
                FROM UNNEST({value}) as exec_list
            ),

            Main_Mentions_Table AS (
                SELECT COUNT(url) as sentiment_count,
                    TRIM(REGEXP_EXTRACT(flattened_mentions, r'/([^/]+)/?$')) as name_list
                FROM Sub_Main_Table
                CROSS JOIN UNNEST(mention_name) AS flattened_mentions
                GROUP BY name_list
            ),

            Final_Main_Table AS (
                SELECT *
                FROM Main_Mentions_Table
                INNER JOIN Match_Table ON Main_Mentions_Table.name_list = Match_Table.exec_list
            ),

            Total_Mentions_Table AS (
                SELECT COUNT(url) as total_count,
                TRIM(REGEXP_EXTRACT(flattened_mentions, r'/([^/]+)/?$')) as name_list
                FROM Sub_Total_Table
                CROSS JOIN UNNEST(mention_name) AS flattened_mentions
                GROUP BY name_list
            ),

            Final_Total_Table AS (
                SELECT *
                FROM Total_Mentions_Table
                INNER JOIN Match_Table ON Total_Mentions_Table.name_list = Match_Table.exec_list
            )

        SELECT SUM(sentiment_count)/SUM(total_count) as sentiment_pct
        FROM Final_Main_Table, Final_Total_Table
        """    

    dff = gbq.read_gbq(query1, project_id = project_id, dialect = 'standard', credentials = credentials)
    dff_article = gbq.read_gbq(query2, project_id = project_id, dialect = 'standard', credentials = credentials)
    dff_social = gbq.read_gbq(query3, project_id = project_id, dialect = 'standard', credentials = credentials)
    dff_sentiment = gbq.read_gbq(query4, project_id = project_id, dialect = 'standard', credentials = credentials)
    
    card1 = '{:,}'.format(dff_article['count_url'].sum())
    card2 = '{:,}'.format(dff['sum_reach'].sum())
    card3 = '{:,}'.format(dff_social['count_url'].sum())  
    card4 = '{:.0%}'.format(dff_sentiment['sentiment_pct'].sum())
            
    
    return card1, card2, card3, card4

@app.callback(
    [Output('news_articles_table_overall', 'data'),
     Output('social_posts_table_overall', 'data')],
    [Input('exec_dropdown', 'value'),
     Input('date_picker', 'start_date'),
     Input('date_picker', 'end_date'),
     Input('comms_pillar_toggle', 'on')]
)

def table_func(value, start_date, end_date, on):
    if on == True:        
        query1 = f'''
        WITH Main_Table AS (
            SELECT reach,
            engagement, 
            extra_author_attributes_name, 
            matched_profile, 
            tags_customer, 
            tags_internal, 
            tags_marking, 
            title_snippet,
            post_type,
            source_type,
            url,
            content_snippet,
            sentiment,
            EXTRACT(DATE FROM TIMESTAMP_MILLIS(published)) AS published_date,
            SPLIT(matched_profile, ',') as mention_name,
            FROM `jnj-ooc.jnj_ooc_dashboard_data.jnj_ooc_dashboard_data`
            WHERE tags_customer IS NOT NULL
                AND REGEXP_CONTAINS(source_type, r'ONLINENEWS') OR REGEXP_CONTAINS(source_type, r'BLOG')
        ),

        Sub_Main_Table AS (
            SELECT *
            FROM Main_Table
            WHERE published_date >= '{start_date}'
                AND published_date <= '{end_date}'
        ),

        Match_Table AS (
            SELECT *
            FROM UNNEST({value}) as exec_list
        ),

        Mentions_Table AS (
        SELECT mention_name as Name,
            content_snippet as Content,
            url as URL,
            reach as Reach,
            TRIM(REGEXP_EXTRACT(flattened_mentions, r'/([^/]+)/?$')) as name_list
        FROM Sub_Main_Table
        CROSS JOIN UNNEST(mention_name) AS flattened_mentions
        )

        SELECT name_list as Name,
            Content,
            URL,
            Reach
        FROM Mentions_Table
        INNER JOIN Match_Table ON Mentions_Table.name_list = Match_Table.exec_list
        ORDER BY Reach DESC
        '''
    
        query2 = f'''
        WITH Main_Table AS (
            SELECT reach,
            engagement, 
            extra_author_attributes_name, 
            matched_profile, 
            tags_customer, 
            tags_internal, 
            tags_marking, 
            title_snippet,
            post_type,
            source_type,
            url,
            content_snippet,
            sentiment,
            EXTRACT(DATE FROM TIMESTAMP_MILLIS(published)) AS published_date,
            SPLIT(matched_profile, ',') as mention_name,
            FROM `jnj-ooc.jnj_ooc_dashboard_data.jnj_ooc_dashboard_data`
            WHERE tags_customer IS NOT NULL
                AND REGEXP_CONTAINS(source_type, r'SOCIALMEDIA') OR REGEXP_CONTAINS(source_type, r'MESSAGEBOARD')
        ),
        
        Sub_Main_Table AS (
            SELECT *
            FROM Main_Table
            WHERE published_date >= '{start_date}'
                AND published_date <= '{end_date}'
        ),

        Match_Table AS (
            SELECT *
            FROM UNNEST({value}) as exec_list
        ),

        Mentions_Table AS (
        SELECT mention_name as Name,
            content_snippet as Content,
            url as URL,
            engagement as Engagement,
            TRIM(REGEXP_EXTRACT(flattened_mentions, r'/([^/]+)/?$')) as name_list
        FROM Sub_Main_Table
        CROSS JOIN UNNEST(mention_name) AS flattened_mentions
        )

        SELECT name_list as Name,
            Content,
            URL,
            Engagement
        FROM Mentions_Table
        INNER JOIN Match_Table ON Mentions_Table.name_list = Match_Table.exec_list
        ORDER BY Engagement DESC
        '''
    
    else:
        query1 = f'''
        WITH Main_Table AS (
            SELECT reach,
            engagement, 
            extra_author_attributes_name, 
            matched_profile, 
            tags_customer, 
            tags_internal, 
            tags_marking, 
            title_snippet,
            post_type,
            source_type,
            url,
            content_snippet,
            sentiment,
            EXTRACT(DATE FROM TIMESTAMP_MILLIS(published)) AS published_date,
            SPLIT(matched_profile, ',') as mention_name,
            FROM `jnj-ooc.jnj_ooc_dashboard_data.jnj_ooc_dashboard_data`
            WHERE REGEXP_CONTAINS(source_type, r'ONLINENEWS') OR REGEXP_CONTAINS(source_type, r'BLOG')
        ),

        Sub_Main_Table AS (
            SELECT *
            FROM Main_Table
            WHERE published_date >= '{start_date}'
                AND published_date <= '{end_date}'
        ),

        Match_Table AS (
            SELECT *
            FROM UNNEST({value}) as exec_list
        ),

        Mentions_Table AS (
        SELECT mention_name as Name,
            content_snippet as Content,
            url as URL,
            reach as Reach,
            TRIM(REGEXP_EXTRACT(flattened_mentions, r'/([^/]+)/?$')) as name_list
        FROM Sub_Main_Table
        CROSS JOIN UNNEST(mention_name) AS flattened_mentions
        )

        SELECT name_list as Name,
            Content,
            URL,
            Reach
        FROM Mentions_Table
        INNER JOIN Match_Table ON Mentions_Table.name_list = Match_Table.exec_list
        ORDER BY Reach DESC
        '''

        query2 = f'''
        WITH Main_Table AS (
            SELECT reach,
            engagement, 
            extra_author_attributes_name, 
            matched_profile, 
            tags_customer, 
            tags_internal, 
            tags_marking, 
            title_snippet,
            post_type,
            source_type,
            url,
            content_snippet,
            sentiment,
            EXTRACT(DATE FROM TIMESTAMP_MILLIS(published)) AS published_date,
            SPLIT(matched_profile, ',') as mention_name,
            FROM `jnj-ooc.jnj_ooc_dashboard_data.jnj_ooc_dashboard_data`
            WHERE REGEXP_CONTAINS(source_type, r'SOCIALMEDIA') OR REGEXP_CONTAINS(source_type, r'MESSAGEBOARD')
        ),
        
        Sub_Main_Table AS (
            SELECT *
            FROM Main_Table
            WHERE published_date >= '{start_date}'
                AND published_date <= '{end_date}'
        ),

        Match_Table AS (
            SELECT *
            FROM UNNEST({value}) as exec_list
        ),

        Mentions_Table AS (
        SELECT mention_name as Name,
            content_snippet as Content,
            url as URL,
            engagement as Engagement,
            TRIM(REGEXP_EXTRACT(flattened_mentions, r'/([^/]+)/?$')) as name_list
        FROM Sub_Main_Table
        CROSS JOIN UNNEST(mention_name) AS flattened_mentions
        )

        SELECT name_list as Name,
            Content,
            URL,
            Engagement
        FROM Mentions_Table
        INNER JOIN Match_Table ON Mentions_Table.name_list = Match_Table.exec_list
        ORDER BY Engagement DESC
        '''   

    dff_article = gbq.read_gbq(query1, project_id = project_id, dialect = 'standard', credentials = credentials)
    dff_social = gbq.read_gbq(query2, project_id = project_id, dialect = 'standard', credentials = credentials)
    
    return dff_article.to_dict('records'), dff_social.to_dict('records')


if __name__ == '__main__':
    app.debug = True
    app.run_server()