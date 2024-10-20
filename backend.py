import pandas as pd
import sqlite3
import os
import streamlit as st
from typing import Literal
from dotenv import load_dotenv
import google.generativeai as genai
import matplotlib.pyplot as plt,seaborn as sns

load_dotenv()
genai.configure(api_key=os.getenv("api_key"))

def create_styled_table(df):
    # Convert DataFrame to HTML
    st.markdown(
        '''
        <style>
        .dataframe thead th {
            font-weight: bold;
            text-align: center;
        }
        .dataframe tbody tr td {
            text-align: center;
        }
        </style>
        ''',
        unsafe_allow_html=True
    )
    
    styled_df = df.style.set_properties(**{
        'text-align': 'center'
    }).set_table_styles(
        [{'selector': 'thead th', 'props': [('font-weight', 'bold')]}]
    )
    
    return styled_df

def data_ingestion(dataset, table_name, type: Literal["c", "j"] = "c"):
    if type == "c":
        data = pd.read_csv(dataset)
    elif type == "j":
        data = pd.read_json(dataset)
    fields = data.columns.to_list()
    data.ffill(inplace=True)
    with sqlite3.connect("mydatabase.db") as conn:
        data.to_sql(table_name, conn, if_exists="replace", index=False)
    return fields


def get_gemini_response(question, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content([prompt, question])
    return response.text


def read_sql_query(sql, db):
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        column_names = [description[0] for description in cur.description]
    return column_names, rows


def prompt_Design(table_name, fields):
    prompt = [
        f"""
    you are an expert in converting english question to SQL query!
    the SQL has a database and in that the table name is:{table_name} 
    and has the following columns : {fields} \n\n
    for example,\nexample 1: How many entries of records are present?,
    the sql command will be something like this SELECT COUNT(*) FROM {table_name};
    example 2: Tell me avg of some column?,
    the sql command will be something like this SELECT AVG(some column) FROM {table_name};
    the sql query should be generate from {table_name} table completely without any assumptions 
    also the sql code should not have ```in the beginning or end and sql word is output"""
    ]
    return prompt
