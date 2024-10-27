from backend import *


st.set_page_config(page_title="SQL Query Retriever", layout="centered", page_icon="📈")

st.title("SQL generator")
if "table_name" not in st.session_state:
    st.session_state.table_name = {}
if "tables" not in st.session_state:
    st.session_state.tables = {}
if "prompt" not in st.session_state:
    st.session_state.prompt = []
if "fields" not in st.session_state:
    st.session_state.fields = []
if "question" not in st.session_state:
    st.session_state.question = []
if "data_ingested" not in st.session_state:
    st.session_state.data_ingested = False


st.header("Upload Your Data File")
uploaded_files = st.file_uploader(
    "Choose files", type=["csv", "json", "pdf"], accept_multiple_files=True
)
if uploaded_files and st.button("Ingest Data"):
    for uploaded_file in uploaded_files:
        if uploaded_file.name.endswith(".csv"):
            file_type = "c"
            st.session_state.table_name = (
                os.path.splitext(uploaded_file.name)[0]
                .replace("-", "_")
                .replace(" ", "")
            )

            pre__(file_type, st.session_state.table_name, uploaded_file)
        elif uploaded_file.name.endswith(".json"):
            file_type = "j"
            st.session_state.table_name = (
                os.path.splitext(uploaded_file.name)[0]
                .replace("-", "_")
                .replace(" ", "")
            )
            pre__(file_type, st.session_state.table_name, uploaded_file)
        elif uploaded_file.name.endswith(".pdf"):
            textdata = extract_text_from_pdf(uploaded_file)
            print("Extracted Text:", textdata)
            model = genai.GenerativeModel("gemini-pro")
            response = model.generate_content(prompt_design_pdf(text_data=textdata))
            a = response.text
            a = a.replace("```", "")
            pdf_to_dict(table_output_preprocess(a))
            print(st.session_state.tables)
        else:
            st.error(
                f"Unsupported file type: {
                    uploaded_file.name}. Please upload a CSV or JSON file."
            )
        st.session_state.data_ingested = True


prompttttt(st.session_state.tables)
if "data_ingested" in st.session_state and st.session_state.data_ingested:
    st.header("Gemini App to Retrieve SQL Data")
    question = st.text_input("Enter your query")
    st.session_state.question = question
    if st.button("Get data"):

        response = (
            get_gemini_response(
                question=st.session_state.question, prompt=st.session_state.prompt[0]
            )
            .replace("```", "")
            .replace("sql", "")
            .strip()
        )
        st.subheader("the generated SQL query:")
        st.write(response)
        column, response = read_sql_query(response, "mydatabase.db")

        st.subheader("the response is:")
        if response:

            if "final_df" not in st.session_state:
                st.session_state.final_df = None
            try:
                st.session_state.final_df = pd.DataFrame(columns=column, data=response)
                st.dataframe(st.session_state.final_df)
            except:
                # df = create_styled_table(response)
                # st.table(df)
                st.session_state.final_df = remove_duplicate_columns(
                    columns=column, data=response
                )
                st.dataframe(st.session_state.final_df)
