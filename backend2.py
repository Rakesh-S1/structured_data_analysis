from dotenv import load_dotenv
import os
import google.generativeai as genai
import pdfplumber

load_dotenv()
genai.configure(api_key=os.getenv("api_key"))

def extract_text_from_pdf(pdf_path):
    text_data = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text_data += page.extract_text()
    return text_data

pdf_path = 'Sales_Report.pdf'
text_data = extract_text_from_pdf(pdf_path)
print("Extracted Text:", text_data)

def prompt_pdf(text_data):
    prompt = '''
        You are an expert data engineer/analyst. I will mention below non-table content and table content. 
        I want you to return only the table content along with a generated table name. 
        Please return this in a dictionary format, 
        where the key is the table name, and the value is a list of tuples containing the table name and its content.
        Do not include any formatting characters like ``` in your output.
        I want you to handle all the tables present,Ensure that all tables in the input are extracted and included in the output.

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
                ("Employee Records", "Employee ID", "Name", "Age", "Department", "Salary"),
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
                ("Inventory List", "Item ID", "Item Name", "Quantity", "Price"),
                ("I001", "Laptop", 50, 1200.00),
                ("I002", "Mouse", 150, 25.00),
                ("I003", "Keyboard", 100, 45.00)
            ],
            "Employee Records":[
            ("Employee Records", "Employee ID", "Name", "Age", "Department", "Salary"),
                ("E001", "John Doe", 30, "Marketing", 60000),
                ("E002", "Jane Smith", 28, "Sales", 55000),
                ("E003", "Mike Johnson", 35, "IT", 70000)
            ]
        }

        Now, based on the extracted text below, please provide the output:

    '''
    prompt+=text_data
    return prompt

model = genai.GenerativeModel("gemini-pro")
response = model.generate_content(prompt_pdf(text_data=text_data))
a = response.text
a= a.replace('```','')
print(a)