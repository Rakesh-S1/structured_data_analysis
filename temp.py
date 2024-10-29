import os
import google.generativeai as genai
import pdfplumber
import sqlite3
import pandas as pd
import ast
from dotenv import load_dotenv
from pprint import pprint

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("api_key"))

def extract_tables_from_pdf(pdf_path):
    tables = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted_tables = page.extract_tables()
            tables.extend(extracted_tables)
    return tables

def check_and_correct_transposed(table_data):
    if len(table_data) > 0 and len(table_data) < len(table_data[0]):
        table_data = list(map(list, zip(*table_data)))
    return table_data

def prompt_table_data(table_data):
    prompt = '''You are an expert data engineer/analyst. I will provide table content below.
    I want you to return this table content along with a generated table name.
    Please return this in a dictionary format,
    where the key is the table name, and the value is a list of tuples containing the table content.
    Do not include any formatting characters like ``` in your output.
    Here is the table content:'''
    prompt += str(table_data)
    return prompt

def ingestion(tables_dict):
    conn = sqlite3.connect('sales_report.db')
    for table_name, rows in tables_dict.items():
        columns = rows[1:]
        data_rows = rows[1:]
        df = pd.DataFrame(data_rows, columns=columns)
        df.to_sql(table_name, conn, if_exists="replace", index=False)
    conn.close()
    pprint(tables_dict)

def model_output_preprocess(output_text):
    try:
        table_content = output_text.split("=", 1)[1].strip()
    except IndexError:
        table_content = output_text.strip()
    table_content = table_content.replace('(','[').replace(')',']')
    table_content = ast.literal_eval(table_content)
    return table_content

pdf_path = './M-Review_July 2024 2-1-22/M-Review_July 2024 2-4.pdf'
tables = extract_tables_from_pdf(pdf_path)

all_tables_dict = {}
model = genai.GenerativeModel("gemini-pro")
for table_data in tables:
    if table_data:
        corrected_table_data = check_and_correct_transposed(table_data)
        prompt = prompt_table_data(corrected_table_data)
        response = model.generate_content(prompt)
        table_dict = model_output_preprocess(response.text.replace('```', ''))
        all_tables_dict.update(table_dict)

ingestion(all_tables_dict)
