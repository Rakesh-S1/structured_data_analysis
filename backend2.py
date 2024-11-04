from dotenv import load_dotenv
import os
import google.generativeai as genai
import pdfplumber
import ast
import sqlite3, pandas as pd

load_dotenv()
genai.configure(api_key=os.getenv("api_key"))

def extract_text_from_pdf(pdf_path):
    text_data = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text_data += page.extract_text()
    return text_data



def prompt_pdf(text_data):
    prompt = '''You are an expert data engineer/analyst. I will mention below non-table content and table content. 
    I want you to return only the table content along with a generated table name. 
    Please return this in a dictionary format, 
    where the key is the table name, and the value is a list of tuples containing the table name and its content.
    Do not include any formatting characters like ``` in your output.
    Ensure that all tables in the input are extracted and included in the output, even if they are adjacent to each other.
    Here are some examples for reference:
    Example 1:
    Extracted Text: Employee Records
    Employee ID Name Age Department Salary
    E001 John Doe 30 Marketing 60000
    E002 Jane Smith 28 Sales 55000
    E003 Mike Johnson 35 IT 70000
    Output:
    {
        "Employee Records": [
            ("Employee ID", "Name", "Age", "Department", "Salary"),
            ("E001", "John Doe", 30, "Marketing", 60000),
            ("E002", "Jane Smith", 28, "Sales", 55000),
            ("E003", "Mike Johnson", 35, "IT", 70000)
        ]
    }
    Example 2:
    Extracted Text: Inventory List
    Item ID Item Name Quantity Price
    I001 Laptop 50 1200.00
    I002 Mouse 150 25.00
    I003 Keyboard 100 45.00
    Extracted Text: Employee Records
    Employee ID Name Age Department Salary
    E001 John Doe 30 Marketing 60000
    E002 Jane Smith 28 Sales 55000
    E003 Mike Johnson 35 IT 70000
    Output:
    {
        "Inventory List": [
            ("Item ID", "Item Name", "Quantity", "Price"),
            ("I001", "Laptop", 50, 1200.00),
            ("I002", "Mouse", 150, 25.00),
            ("I003", "Keyboard", 100, 45.00)
        ],
        "Employee Records":[
            ("Employee ID", "Name", "Age", "Department", "Salary"),
            ("E001", "John Doe", 30, "Marketing", 60000),
            ("E002", "Jane Smith", 28, "Sales", 55000),
            ("E003", "Mike Johnson", 35, "IT", 70000)
        ]
    }
    Now, based on the extracted text below, please provide the output:'''
    prompt+=text_data
    return prompt

from pprint import pprint
def ingestion(a:dict):
    conn = sqlite3.connect('sales_report.db')  # Create or connect to a database

    # Iterate over each table in the dictionary
    for table_name, rows in a.items():
        # Extract header and data rows
        columns = rows[0]  # Get the header row
        data_rows = rows[1:]  # Get the data rows

        # Print for debugging
        print(f"Table: {table_name}")
        print(f"Columns: {columns}")
        print("Data Rows:")
        print(data_rows)

        # Create a DataFrame
        df = pd.DataFrame(data_rows, columns=columns)

        # Write the DataFrame to SQL database
        df.to_sql(table_name, conn, if_exists="replace", index=False)

    # Close the connection
    conn.close()
    pprint(a)



def model_output_preprocess(table_content:str):

    
    try:
        table_content = table_content.split("=", 1)[1].strip()
    except IndexError:
        table_content = table_content.strip()
    
    table_content = table_content.replace('(','[').replace(')',']')
    table_content = ast.literal_eval(table_content)
    print(table_content)

    return table_content

pdf_path = './M-Review_July 2024 2-1-22/M-Review_July 2024 2-18.pdf '
text_data = extract_text_from_pdf(pdf_path)

model = genai.GenerativeModel("gemini-pro")
response = model.generate_content(prompt_pdf(text_data=text_data))
a = response.text
a= a.replace('```','')

a = model_output_preprocess(a)
ingestion(a)

# print(text_data)
# 