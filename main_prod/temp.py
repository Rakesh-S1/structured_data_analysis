import os
import re
import ast
import sqlite3
import pdfplumber
import pandas as pd
import streamlit as st
from typing import Literal
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("api_key"))

def extract_text_from_pdf(pdf_path):
    text_data = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text_data += page.extract_text()
    return text_data

def extract_tables_from_pdf(pdf_path):
    tables = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_tables = page.extract_tables()
            for table in page_tables:
                merged_table = merge_multiline_columns(table)
                tables.append(merged_table)
    return tables

def merge_multiline_columns(table):
    merged_table = []
    for row in table:
        merged_row = []
        for cell in row:
            if isinstance(cell, list):
                merged_cell = ' '.join(cell)
                merged_row.append(merged_cell)
            else:
                merged_row.append(cell)
        merged_table.append(merged_row)
    return merged_table

def prompt_design_pdf(tables):
    prompt = """You are an expert data engineer/analyst. I will mention below non-table content and table content. 
    I want you to return only the table content along with a generated table name. 
    Please return this in a dictionary format,
    where the key is the table name, and the value is a list of tuples containing the table name and its content.
    Do not include any formatting characters like ``` in your output.
    I want you to handle all the tables present. Ensure that all tables in the input are extracted and included in the output.
    Now, based on the extracted text below, please provide the output:"""

    for i, table in enumerate(tables):
        prompt += f"\nTable {i + 1}:\n"
        for row in table:
            prompt += " ".join(map(str, row)) + "\n"
    
    return prompt



def table_output_preprocess(table_content: str):
    try:
        # Attempt to fix common formatting issues
        table_content = table_content.split("=", 1)[1].strip()
    except IndexError:
        table_content = table_content.strip()
    
    # Debugging step: Print the table_content before evaluation
    print("Original Table Content:", table_content)
    
    # Attempt to correct unclosed brackets
    table_content = re.sub(r"\[(?![^[]*\])", "[[", table_content)  # Ensure each '[' has a closing ']' after it
    
    try:
        table_content = ast.literal_eval(table_content)
    except (SyntaxError, ValueError) as e:
        print("Error in literal_eval:", e)
        # Further debugging or correction steps can be added here
        raise
    
    return table_content


def data_ingest(table_name, data: pd.DataFrame):
    with sqlite3.connect("mydatabase.db") as conn:
        data.to_sql(table_name, conn, if_exists="replace", index=False)

def pdf_to_dict(tables):
    table_dict = {}
    for i, rows in enumerate(tables):
        columns = [col.replace("-", "_").replace(" ", "") for col in rows[0]]
        data_rows = rows[1:]
        df = pd.DataFrame(data_rows, columns=columns)
        table_name = f"table_{i + 1}"
        table_dict[table_name] = columns
        data_ingest(table_name, df)
    return table_dict

def data_ingestion(dataset, table_name, type: Literal["c", "j"] = "c"):
    if type == "c":
        data = pd.read_csv(dataset)
    elif type == "j":
        data = pd.read_json(dataset)
    fields = data.columns.to_list()
    data.ffill(inplace=True)
    data_ingest(table_name=table_name, data=data)
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
    prompt = [f"""
        You are an expert in converting English question to SQL query!
        The SQL has a database and in that the table name is: {table_name} 
        and has the following columns: {fields}
        For example,
        Example 1: How many entries of records are present?, 
        the SQL command will be something like this SELECT COUNT(*) FROM {table_name};
        Example 2: Tell me avg of some column?, 
        the SQL command will be something like this SELECT AVG(some column) FROM {table_name};
        The SQL query should be generated from {table_name} table completely without any assumptions.
        Also, the SQL code should not have ``` in the beginning or end and sql word is output
    """]
    return prompt

def prompttttt(a: dict):
    prompt = ["""
        You are an expert in converting English questions to SQL queries!
        Your tables are mentioned below along with column names.
        Example 1: "How many entries of records are present?"
        The SQL command will be: SELECT COUNT(*) FROM table_name;
        Example 2: "Tell me the average of some column?"
        The SQL command will be: SELECT AVG(column_name) FROM table_name;
        The SQL query should be generated from the provided table and column names with no assumptions.
        When performing JOIN operations or subqueries, do NOT return duplicate columns.
        Always qualify column names with their table names when necessary (e.g., `table_name.column_name`) to avoid ambiguity.
        The SQL query should NOT include any SQL code fencing or extra words like `sql`.
    """]
    for i, j in a.items():
        prompt[0] += f"table {i} has fields {j}\n"
    st.session_state.prompt = prompt

def pre__(file_type, table_name, uploaded_file):
    try:
        st.session_state.fields = data_ingestion(uploaded_file, table_name, file_type)
        st.success(f"Data ingested successfully into the '{st.session_state.table_name}' table.")
        st.session_state.tables[st.session_state.table_name] = st.session_state.fields
    except Exception as e:
        st.error(f"An error occurred: {e}")

def remove_duplicate_columns(columns, data):
    df = pd.DataFrame(data, columns=columns)
    column_groups = {}
    for col in df.columns:
        if col not in column_groups:
            column_groups[col] = [df[col]]
        else:
            column_groups[col].append(df[col])
    for col, group in column_groups.items():
        if len(group) > 1:
            if all(group[0].equals(g) for g in group[1:]):
                df[col] = group[0]
                for dup_col in group[1:]:
                    df = df.drop(dup_col.name, axis=1)
    return df

# Example usage
# pdf_path = 'your_pdf_file.pdf'
# extracted_tables = extract_tables_from_pdf(pdf_path)
# pdf_to_dict(extracted_tables)
