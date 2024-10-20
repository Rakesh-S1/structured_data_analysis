import pandas as pd
import sqlite3
import os
import streamlit as st
from typing import Literal
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("api_key"))

def create_styled_table(df):
    # Convert DataFrame to HTML
    table_html = df.to_html(index=False, classes='styled-table', escape=False)
    
    # Define custom CSS for table
    table_style = """
    <style>
    .styled-table {
        border-collapse: collapse;
        margin: 25px 0;
        font-size: 18px;
        font-family: Arial, sans-serif;
        min-width: 400px;
        width: 100%;
        text-align: left;
    }
    .styled-table th {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        padding: 12px 15px;
    }
    .styled-table td {
        padding: 12px 15px;
    }
    .styled-table tbody tr {
        border-bottom: 1px solid #dddddd;
    }
    .styled-table tbody tr:nth-of-type(even) {
        background-color: #f3f3f3;
    }
    .styled-table tbody tr:last-of-type {
        border-bottom: 2px solid #4CAF50;
    }
    .table-container {
        max-height: 400px;  /* Fixed height for the table */
        overflow-y: auto;   /* Scrollable content */
        width: 100%;
    }
    </style>
    """
    
    # Combine table style and content
    full_html = f"{table_style}<div class='table-container'>{table_html}</div>"
    return full_html

def data_ingestion(dataset, table_name, type: Literal["c", "j"] = "c"):
    if type == "c":
        data = pd.read_csv(dataset)
    elif type == "j":
        data = pd.read_json(dataset)
    fields = data.columns.to_list()
    data.ffill(inplace=True)
    with sqlite3.connect("mydatabase.db") as conn:
        data.to_sql(table_name, conn, if_exists="append", index=False)
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
