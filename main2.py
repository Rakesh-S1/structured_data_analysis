import pandas as pd
import streamlit as st

st.set_page_config(page_title="SQL Query Retriever", layout='centered', page_icon='📈')
st.title('📈 SQL Generator')

st.header("Upload Your Data Files")

uploaded_files = st.file_uploader("Choose CSV files", type=["csv"], accept_multiple_files=True)

# Check if any files are uploaded
if uploaded_files:
    for uploaded_file in uploaded_files:
        # Read each CSV file
        df = pd.read_csv(uploaded_file)
        
        # Display the file name and content
        st.subheader(f"File: {uploaded_file.name}")
        st.dataframe(df)

