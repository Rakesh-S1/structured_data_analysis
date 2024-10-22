from backend import *

st.set_page_config(page_title="SQL Query Retriever", layout='centered', page_icon='📈')
st.title('📈 SQL generator')
st.header("Upload Your Data File")
uploaded_file = st.file_uploader("Choose a file", type=["csv", "json"])
if uploaded_file is not None:
    if uploaded_file.name.endswith(".csv"):
        file_type = "c"
    elif uploaded_file.name.endswith(".json"):
        file_type = "j"
    else:
        st.error("Unsupported file type. Please upload a CSV or JSON file.")
        
    if "table_name" not in st.session_state:
        st.session_state.table_name = ""
    table_name = os.path.splitext(uploaded_file.name)[0].replace('-','_').replace(' ','')
    st.session_state.table_name = table_name
    if "prompt" not in st.session_state:
        st.session_state.prompt = []
    if "fields" not in st.session_state:
        st.session_state.fields = []

    if st.button("Ingest Data"):
        try:
            st.session_state.fields = data_ingestion(
                uploaded_file, st.session_state.table_name, file_type
            )
            st.success(
                f"Data ingested successfully into the '{
                    st.session_state.table_name}' table."
            )
            st.session_state.prompt = prompt_Design(
                st.session_state.table_name, st.session_state.fields
            )
            st.session_state.data_ingested = True
        except Exception as e:
            st.error(f"An error occurred: {e}")
else:
    st.info("please upload again")

if "data_ingested" in st.session_state and st.session_state.data_ingested:
    st.header("Gemini App to Retrieve SQL Data")
    question = st.text_input("Enter your query")

    if st.button("Get data"):
        if question:
            response = (
                get_gemini_response(question, st.session_state.prompt[0])
                .replace("```", "")
                .replace("sql", "")
                .strip()
            )
            print(st.session_state.prompt[0])
            column, response = read_sql_query(response, "mydatabase.db")
            st.subheader("the response is:")
            if response:
                df = pd.DataFrame(response, columns=column)
                df = create_styled_table(df)
                if 'final_df' not in st.session_state:
                    st.session_state.final_df = None
                st.session_state.final_df = df    
                # st.table(df)
                st.dataframe(df)
                # st.markdown('<div class="scrollable-table">'+ df.to_html()+'</div>', unsafe_allow_html=True)

    
                # st.markdown(create_styled_table(df), unsafe_allow_html=True)
                # st.table(df)
