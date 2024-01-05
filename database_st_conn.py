import mysql.connector
import streamlit as st
import pandas as pd
import openai
import os
from dotenv import load_dotenv
import generate_insights as Ins
import visualization as visual
# Load environment variables
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv('openai_api_key')

def make_prompt(customer_query,schema):
    prompt = f"""You are a professional DataBase Adminstrator \
        You have to write the syntatically sementically correct sql query \
        the sql query should be transformed from the customer_query \
        the attributes and table names to be used for formulating the sql query should be identical to the provided schema\
        schema is a dictionary with table names as keys and table columns as their respective values \
        schema can have a single table only or multiple relational tables\
        while formulating the sql query consider the principles of relational database concepts\
        append a semicolon (;)at the end of sql query.\
        if the customer_query doesn't sound like a query, say "Please enter the relevent query !".
        
        
        ```{customer_query}```        
        ```{schema}```
    """
    return prompt

def get_completion(messages, model="gpt-3.5-turbo"):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0,
    )
    return response.choices[0].message["content"]

def get_answer(user_query,schema):

    prompt = make_prompt(user_query,schema)
    messages = [
        {"role": "system", "content": prompt}
    ] 

    response = get_completion(messages)
    
    return response


# Function to establish a database connection
def database_connection(host, user, password, database):
    schema = {}
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        if connection.is_connected():
            with st.sidebar:
               st.success(f"Connection Successfull !")

            cursor = connection.cursor()

            # Define your SQL query
            schema_query = f""" SELECT table_name, column_name
                            FROM INFORMATION_SCHEMA.COLUMNS
                            WHERE table_schema = '{database}';"""

            # Execute the query
            cursor.execute(schema_query)

            # Fetch all rows
            rows = cursor.fetchall()

            # Display the fetched data using st.write
            # with st.sidebar:
            #     st.subheader("Schema:")
            for row in rows:
                table_name, column_name = row
                if table_name not in schema:
                    schema[table_name] = []
                schema[table_name].append(column_name)
            #st.write(schema)
            return connection,schema

    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
        return None

# Function to fetch data from the database
def fetch_data(connection,response):
    try:
        cursor = connection.cursor()
        query = response
        cursor.execute(query)
        rows = cursor.fetchall()
        #st.subheader("Fetched data:")
        if rows:
            return rows
        else:
            st.error(f"Error: Invalid query! Please provide correct information.")

    except mysql.connector.Error as err:
        st.error(f"Error: {err}")

    # finally:
    #     # Close the cursor and connection
    #     if cursor:
    #         cursor.close()
    #     if connection.is_connected():
    #         connection.close()
    #         st.success("Connection closed")
if 'db_connection' not in st.session_state:
    st.session_state['db_connection']=[]

if 'connect_db' not in st.session_state:
    st.session_state['connect_db']=[]

if 'schema' not in st.session_state:
    st.session_state['schema']=[]
# Main function
def main():
    st.title("Data Craft")
    # Custom CSS styles for button and text box
    st.markdown(
        """
        <style>
            .stButton>button {
            background-color: #000000;
            color: #FFFFFF;
            }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Sidebar for input fields
    with st.sidebar:
        st.subheader("Connection Settings")
        host = st.text_input("MySQL Host:")
        user = st.text_input("MySQL Username:")
        password = st.text_input("MySQL Password:", type="password")
        database = st.text_input("MySQL Database Name:")

    # Connect to the database when the "Connect" button is clicked
    check_connection=st.sidebar.button("Connect", key='check_connection')
    st.session_state['connect_db']=check_connection
    if st.session_state['connect_db'] is not None:
        #print(st.sidebar.button("Connect"))
        if host and user and database:
            
            db_connection,schema = database_connection(host, user, password, database)
            st.session_state['schema']=schema
            st.session_state['db_connection']=db_connection
            #st.write(st.session_state['db_connection'])
        if st.session_state['db_connection'] is not None:
            
            st.markdown("---")
            with st.form(key='my_form', clear_on_submit=True):  
                user_query = st.text_area("Enter your query:", height=150, max_chars=1000)
                submit_button = st.form_submit_button(label='Draft Insights')
                #st.write(submit_button)
            if submit_button:
                
                if user_query:
                    sql_query = get_answer(user_query, st.session_state['schema'])

                    with st.expander("Generated SQL Query", expanded=True):
                        st.success(sql_query)
                    if sql_query != "Please enter the relevant query!":

                        # Perform database operations here
                        data = fetch_data(db_connection, sql_query)
                        print(f"==========DATA=============  {data}")
                        query_nature = visual.get_answer(sql_query)
                        if any(element is None for element in data[0]):
             
                             st.error(f"Error: Invalid query! Please provide correct information.")
                        else:
                            
                            print(f"USER QUERY : {sql_query} \nsql_query : {query_nature}")
                            if "Insight" in query_nature:
                                # for element in data:
                                #     st.success(element)
                                processed_data = Ins.get_insights(user_query,data)
                                st.success(processed_data)
                            else:
                                visual.visualization(data,query_nature)
                        
      
if __name__ == "__main__":
    main()
