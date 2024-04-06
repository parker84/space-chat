import streamlit as st
from groq import Groq
from decouple import config
import logging, coloredlogs
logger = logging.getLogger(__name__)
coloredlogs.install(level=config('LOG_LEVEL', 'INFO'), logger=logger)


GROQ_MODEL = 'mixtral-8x7b-32768'
TIMEOUT = 120
groq_client = Groq(
    api_key=config('GROQ_API_KEY'),
)

st.set_page_config(
    page_title='Space Chat',
    page_icon='🌌',
    initial_sidebar_state='collapsed'
)

def parse_groq_stream(stream):
    for chunk in stream:
        if chunk.choices:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

st.title('🛸 Space Chat')
st.caption('ChatGPT like space focused chatbot powered by [Groq](https://groq.com/).')

# Set a default model
if "groq_model" not in st.session_state:
    st.session_state["groq_model"] = GROQ_MODEL

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": """
            You are a world-leading expert on all things space.
            This includes but is not limited to: planets, stars, galaxies, black holes, astronomy, astrophysics, and space exploration.
            Format your responses with fun Emojis! 🚀🌌👽
            And wrap numbers in proper markdown formatting (ex: `123`).
            When discussing sizes / distances / etc, use relative terms like "`3x` larger than Earth" or "`25%` of the size of the Sun".
            In addition to include the actual units (ex: `52,343` kilometers).
            When talking about something being bigger - use x (ex: `3x`) when talking about something being smaller user % (ex: `25%`).
            Only answer the question - do not return something dumb like "[YourNextQuestion]"
         """
         },
        {"role": "assistant", "content": "Hey there! I'm an expert on everything to do with Space. Ask me about Uranus! 🌌"}
    ]

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message(message["role"], avatar="👩‍💻"):
            st.markdown(message["content"])
    elif message["role"] == "assistant":
        with st.chat_message(message["role"], avatar="👽"):
            st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("How big is it?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user", avatar="👩‍💻"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant", avatar="👽"):
        stream = groq_client.chat.completions.create(
            model=st.session_state["groq_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            temperature=0.0,
            stream=True,
        )
        response = st.write_stream(parse_groq_stream(stream))
    st.session_state.messages.append({"role": "assistant", "content": response})