# install Streamlit and execute
# > streamlit run app.py

import re
import time
import requests
import pandas as pd
import streamlit as st
from openai import OpenAI
from datetime import datetime as dt
import matplotlib.pyplot as plt 
import matplotlib.ticker as mtick

# st.set_page_config(layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("../data/web.csv", sep="|")
    cols_to_drop = [col for col in df.columns if re.search('visit', col)]
    df.drop(cols_to_drop, axis=1, inplace=True)
    df['day']=pd.to_datetime(df['day'])
    df.set_index(['day'],drop=True, inplace=True)
    df=df.groupby('identifier').resample('W').sum()
    return df.drop('identifier', axis=1).reset_index(0)

def plot(df,date,identifier,col):
    
    df = df[(df.identifier==identifier)]
    maxi1=round(df[col].max()*1.5)
    
    df=df.loc[df.index[0]:pd.Timestamp(date)]
    fig, (ax1) = plt.subplots(1,figsize=(5,3),dpi=100)
    ax1.plot(df[col],marker='o', linestyle='--', linewidth=2,markersize=3, color='tab:green')

    ax1.set_xlim([START, END])
    ax1.set_ylim([0, maxi1])
    ax1.tick_params(axis='x', labelsize=7)
    ax1.tick_params(axis='y', labelsize=7 , rotation=33)    
    ax1.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.0e'))

    plt.title('%s per week for account %s'%(col, identifier), fontsize=11)
    plt.tight_layout()
    return fig

st.title("my Streamlit App")

t = st.sidebar.selectbox('Sidebar',['EDA', 'Cheat sheet', 'Open AI'])

if t == 'EDA':

    res=load_data()

    id = list(res.identifier.unique())
    option1 = st.selectbox('Account Number', ['?']+id)

    if option1=='?':
        st.stop()

    st.dataframe(res[(res.identifier==option1)].sort_index(ascending=False))

    ts = list(res.columns)
    ts.remove('identifier')
    option2 = st.selectbox('Feature', ts)

    if st.button('Plot'):
        START=res.index[0]
        END=res.index[-1]
        for date in pd.date_range(start = START, end = END,freq = '1W'):
            fig = plot(res, date, option1, option2)
            if date==START:
                empty = st.pyplot(fig)
            else:
                empty.pyplot(fig)
            time.sleep(.005)
        
        st.balloons()

if t == 'Cheat sheet':

  with st.expander("Cheat sheet", expanded=True):

    st.markdown(
        """
        <style>
            div[role=radiogroup] label:first-of-type {
                visibility: hidden;
                height: 0px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if 'b' not in st.session_state:
        st.session_state.b = False

    b = st.button('Hit me')
    if b or st.session_state.b:
       st.session_state.b = True
       st.write("Ouch")

    c = st.checkbox('Check me out')
    if c:
       st.write("Checked")

    r = st.radio('Radio', ['',1,2,3], index=0)
    if r :
       st.write(r)

    sb = st.selectbox('Select', ['',1,2,3])
    if sb:
       st.write(sb)

    ms = st.multiselect('Multiselect', ['',1,2,3])
    if ms:
       st.write(ms)

    s = st.slider('Slide me', min_value=0, max_value=10, step=1)
    st.write(s)

    sd = st.slider(label='Slide me (date)', value=dt.today().date(), format="MM/DD/YYYY")
    st.write(sd)

    ss = st.select_slider('Slide to select', options=['A','B'])

    t = st.text_input('Enter some text')

    f = st.number_input('Enter a number (float)')

    for i in range(int(st.number_input(label='Enter a number (int)', max_value=10, value=3, step=1))):
        st.write(i)

    st.text_area('Text area')
    st.date_input('Date input')
    st.time_input('Time input')
    st.color_picker('Color picker')
    st.file_uploader('File uploader')

    st.code('for i in range(8):\n\
    print(i)')

    st.latex(r''' e^{i\pi} + 1 = 0 ''')

    def get_app_name():
        return 'Streamlit'

    with st.echo():
        # Everything inside this block will be both printed to the screen and executed.

        def get_punctuation():
            return '•'

        t = 'A faster way to build and share data apps'

        st.write(get_app_name(), get_punctuation(), t)

    # And now we're back to _not_ printing to the screen

    st.title("Title")

    st.header("Header")

    st.subheader("Subheader")

    st.caption("Caption")

    st.info("Info")

    st.success("Success")

    st.warning("Warning")

    st.error("Error")

    re = RuntimeError('RuntimeError')
    st.exception(re)

if t == "Open AI":

    api_key = st.text_input("API key")
    client = OpenAI(api_key=api_key)

    if api_key:
        response = requests.request(
            method="GET",
            url="https://api.openai.com/v1/models",
            headers={
                'accept': "application/json",
                'Authorization': f"Bearer {api_key}"
            }
        ).json()
        models = [model['id'] for model in response['data']]
        model = st.selectbox("Select model", models)

    def answer(model, messages):

        response = client.chat.completions.create(
           # model="gpt-3.5-turbo",
           # model="gpt-4",
           model=model,
           messages=messages,
           temperature=0.2,
           max_tokens=256,
           frequency_penalty=0.0
        )

        return response

    assistant_prompt = st.text_area("content 👇 (role: assistant )")
    user_prompt = st.text_area("content 👇 (role: user)")

    if api_key and model and (assistant_prompt and user_prompt):

        go = st.button("🟢")

        if go:

            messages = [
                {"role": "assistant", "content": assistant_prompt},
                {"role": "user", "content": user_prompt}
                ]
            response = answer(model, messages)

            tokens_used = response.usage.total_tokens
            st.write("%d tokens used."%tokens_used)

            response_text = response.choices[0].message.content
            st.write(response_text)
