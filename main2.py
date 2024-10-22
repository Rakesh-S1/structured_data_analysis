from backend import *

<<<<<<< HEAD
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
=======
st.set_page_config(page_title="SQL Query Retriever", layout="centered", page_icon="📈")

st.title("📈 SQL generator")
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
    "Choose files", type=["csv", "json"], accept_multiple_files=True
)


def pre__(file_type, table_name):
    try:
        st.session_state.fields = data_ingestion(uploaded_file, table_name, file_type)
        st.success(
            f"Data ingested successfully into the '{
                st.session_state.table_name}' table."
        )
        st.session_state.tables[st.session_state.table_name] = st.session_state.fields
    except Exception as e:
        st.error(f"An error occurred: {e}")

def remove_duplicate_columns(columns, data):
    # Create a dictionary to track the occurrence of each column
    column_count = {}
    
    # Step 1: Identify duplicate columns
    for col in columns:
        if col in column_count:
            column_count[col] += 1
        else:
            column_count[col] = 1
    
    # Step 2: Create a new list for cleaned columns and a new data structure
    cleaned_columns = []
    cleaned_data = []
    
    # Step 3: Track the index of each column in the original data
    for col in columns:
        if column_count[col] == 1:
            cleaned_columns.append(col)
            # Append all values from the data
            cleaned_data = [row + (None,) for row in cleaned_data]  # Add None for alignment
            for idx in range(len(data)):
                cleaned_data[idx] = cleaned_data[idx][:-1] + (data[idx][columns.index(col)],)
        else:
            # Only add the first occurrence of the column to cleaned_columns
            if col not in cleaned_columns:
                cleaned_columns.append(col)
                # Append all values from the data
                cleaned_data = [row + (None,) for row in cleaned_data]  # Add None for alignment
                for idx in range(len(data)):
                    cleaned_data[idx] = cleaned_data[idx][:-1] + (data[idx][columns.index(col)],)
    
    # Remove duplicate values from cleaned_data
    cleaned_data = []
    for i in range(len(data)):
        new_row = []
        for col in cleaned_columns:
            index = columns.index(col)
            new_row.append(data[i][index])
        cleaned_data.append(new_row)

    # Step 4: Create a DataFrame
    df = pd.DataFrame(cleaned_data, columns=cleaned_columns)
    
    return df

def prompttttt(a: dict):
    # The initial base prompt
    b = [
        f"""
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
    """
    ]
    for i, j in a.items():
        b[0] += f"table {i} has fields {j}\n"
    print(b)
    st.write(b)
    st.session_state.prompt = b


if uploaded_files and st.button("Ingest Data"):
    for uploaded_file in uploaded_files:
        if uploaded_file.name.endswith(".csv"):
            file_type = "c"
            st.session_state.table_name = (
                os.path.splitext(uploaded_file.name)[0]
                .replace("-", "_")
                .replace(" ", "")
            )

            pre__(file_type, st.session_state.table_name)
        elif uploaded_file.name.endswith(".json"):
            file_type = "j"
        else:
            st.error(
                f"Unsupported file type: {uploaded_file.name}. Please upload a CSV or JSON file."
            )
        st.session_state.data_ingested = True

st.text(st.session_state.tables)

prompttttt(st.session_state.tables)
if "data_ingested" in st.session_state and st.session_state.data_ingested:
    st.header("Gemini App to Retrieve SQL Data")
    question = st.text_input("Enter your query")
    st.session_state.question = question
    if st.button("Get data"):
        print(1)
        print(st.session_state.question)
        print(st.session_state.prompt)
        response = (
            get_gemini_response(
                question=st.session_state.question, prompt=st.session_state.prompt[0]
            )
            .replace("```", "")
            .replace("sql", "")
            .strip()
        )
        column, response = read_sql_query(response, "mydatabase.db")
        print(column, response)
        
        st.subheader("the response is:")
        if response:
            df = remove_duplicate_columns(columns=column, data=response)
        #     # df = create_styled_table(df)
            if 'final_df' not in st.session_state:
                st.session_state.final_df = None
            st.session_state.final_df = df    
            # st.table(df)
            st.dataframe(st.session_state.final_df)


#     st.session_state.table_name = table_name
#     if "prompt" not in st.session_state:
#         st.session_state.prompt = []
#     if "fields" not in st.session_state:
#         st.session_state.fields = []

#     if st.button("Ingest Data"):
#         try:
#             st.session_state.fields = data_ingestion(
#                 uploaded_file, st.session_state.table_name, file_type
#             )
#             st.success(
#                 f"Data ingested successfully into the '{
#                     st.session_state.table_name}' table."
#             )
#             st.session_state.prompt = prompt_Design(
#                 st.session_state.table_name, st.session_state.fields
#             )
#             st.session_state.data_ingested = True
#         except Exception as e:
#             st.error(f"An error occurred: {e}")
# else:
#     st.info("please upload again")

# if "data_ingested" in st.session_state and st.session_state.data_ingested:
#     st.header("Gemini App to Retrieve SQL Data")
#     question = st.text_input("Enter your query")

#     if st.button("Get data"):
#         if question:
#             response = (
#                 get_gemini_response(question, st.session_state.prompt[0])
#                 .replace("```", "")
#                 .replace("sql", "")
#                 .strip()
#             )
#             print(st.session_state.prompt[0])
#             column, response = read_sql_query(response, "mydatabase.db")
#             st.subheader("the response is:")
#             if response:
#                 df = pd.DataFrame(response, columns=column)
#                 df = create_styled_table(df)
#                 if 'final_df' not in st.session_state:
#                     st.session_state.final_df = None
#                 st.session_state.final_df = df
#                 # st.table(df)
#                 st.dataframe(df)
# st.markdown('<div class="scrollable-table">'+ df.to_html()+'</div>', unsafe_allow_html=True)


# st.markdown(create_styled_table(df), unsafe_allow_html=True)
# st.table(df)
>>>>>>> 5445c3e5a9e00f03f45bc14b2a12489c3e059d1c
