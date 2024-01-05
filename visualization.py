import openai
import os
import pandas as pd
from dotenv import load_dotenv
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

# Load environment variables
load_dotenv()
# Set OpenAI API key
openai.api_key = os.getenv('openai_api_key')

def visualization(data,response):

    # Extracting data
    x_axis, y_axis = zip(*data)
    
    print(f"X-AXIS : {x_axis} \nY-AXIS : {y_axis}")
    process_labels = response[1:-1].replace('"', '')
    extracted_labels = process_labels.split(',')
    horizontal_axis = extracted_labels[1].strip()
    vertical_axis = extracted_labels[2].strip()
    #df = pd.DataFrame({horizontal_axis: x_axis, vertical_axis: y_axis})
    st.title(extracted_labels[3].strip())
    # sns.set(style="whitegrid")
    # plt.figure(figsize=(2,2))
    # bar_plot = sns.barplot(x=horizontal_axis, y=vertical_axis, data=df, palette="viridis", hue=horizontal_axis, legend=False)
    # bar_plot.set(xlabel=horizontal_axis, ylabel=vertical_axis, title=extracted_labels[3].strip())
    # st.pyplot(plt)
    # Create a dictionary for DataFrame
    data_dict = {x: y for x, y in zip(x_axis, y_axis)}

    # Display the bar chart using st.bar_chart
    st.bar_chart(data=data_dict, use_container_width=True)
 



def make_prompt(user_query):
    prompt = f"""You are an expert Data Scientist\
                 you have to follow the specified instructions.\
                 
                Identify the nature of user_query\
                in what form the user_query needs to be answered\
                there can be 3 forms:
                1. Insight
                2. Graph
                3. Chart
            
                If the answer is graph or chart user the user_query to get two labels for x-axis and y-axis\
                append the labels at the end of response list.\
                
                Suggest a title for the graph/chart and append it at the end of the response list.
            
                The response should just be the list formed.

                Example:
                                        
                ["Chart","Countr","Count","Number of Customers in Each Country"]
                       

        ```{user_query}```        
        
    """
    return prompt

def get_completion(messages, model="gpt-3.5-turbo"):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0,
    )
    return response.choices[0].message["content"]

def get_answer(user_query):

    prompt = make_prompt(user_query)
    messages = [
        {"role": "system", "content": prompt}
    ] 

    response = get_completion(messages)
    
    return response



