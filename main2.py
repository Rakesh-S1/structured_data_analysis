from backend import *
from backend2 import *
st.set_page_config(page_title="SQL Query Retriever",
                   layout="centered", page_icon="📈")

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



def pre__(file_type, table_name, uploaded_file):
    """
    Ingests data from a file into a specified table and updates the session state.
    """
    try:
        st.session_state.fields = data_ingestion(
            uploaded_file, table_name, file_type)
        st.success(
            f"Data ingested successfully into the '{
                st.session_state.table_name}' table."
        )
        st.session_state.tables[st.session_state.table_name] = st.session_state.fields
    except Exception as e:
        st.error(f"An error occurred: {e}")


def remove_duplicate_columns(columns, data):
    """
    Takes in columns and data, merges duplicate columns if their data is identical,
    and returns a DataFrame with duplicates removed.
    """
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
                df[col] = group[0]  # Keep the first occurrence
                for dup_col in group[1:]:
                    df = df.drop(dup_col.name, axis=1)  # Drop duplicates

    # df_transposed = df.T
    # df_transposed = df_transposed.drop_duplicates(keep='first')
    # return df_transposed.T
    return df


def prompttttt(a: dict):
    """
    Generates a prompt for converting English questions to SQL queries based on provided table and column names.
    """
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
    st.session_state.prompt = b

st.header("Upload Your Data File")
uploaded_files = st.file_uploader(
    "Choose files", type=["csv", "json"], accept_multiple_files=True
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
        print(response)
        st.subheader('the generated SQL query:')
        st.write(response)
        column, response = read_sql_query(response, "mydatabase.db")
        print(column, response)

        st.subheader("the response is:")
        if response:
            #     pass
            # #     df = remove_duplicate_columns(columns=column, data=response)
            # # #     # df = create_styled_table(df)
            if 'final_df' not in st.session_state:
                st.session_state.final_df = None
            print(column, '\n', response)
            try:
                st.session_state.final_df = pd.DataFrame(columns=column, data=response)
                st.dataframe(st.session_state.final_df)
            except:
                # df = create_styled_table(response)
                # st.table(df)
                st.session_state.final_df = remove_duplicate_columns(columns=column, data=response)
                st.dataframe(st.session_state.final_df)
