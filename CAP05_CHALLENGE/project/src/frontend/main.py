import requests
import json
import time
import streamlit as st
import sseclient  # sseclient-py
import logging
from requests.exceptions import ChunkedEncodingError, RequestException


def backend_call(query: str):
    url = f"http://orchestrator/streamingSearch?query={query}"
    try:
        # Increase timeout and add connection resilience
        stream_response = requests.get(url, stream=True, timeout=60)
        client = sseclient.SSEClient(stream_response)  # type: ignore

        # Loop through events with error handling
        try:
            for event in client.events():
                yield event
        except ChunkedEncodingError:
            # Handle premature connection termination
            st.warning("Connection interrupted. Some data may be missing.")
            yield {"event": "error", "data": "Connection interrupted"}
        except Exception as e:
            st.error(f"Error receiving data: {str(e)}")
            yield {"event": "error", "data": str(e)}
    except RequestException as e:
        st.error(f"Failed to connect to backend: {str(e)}")
        yield {"event": "error", "data": f"Connection error: {str(e)}"}


def display_chat_messages():
    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def process_user_input(prompt):
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)


def process_backend_response(prompt):
    full_response = ""
    columns = st.columns(2)
    button_count = 0
    button_placeholders, message_placeholder = [], None
    with st.spinner("Thinking..."):
        for chunk in backend_call(prompt):
            # Handle error events
            if getattr(chunk, "event", None) == "error":
                if message_placeholder:
                    message_placeholder.markdown(f"{full_response}\n\n*Connection error occurred*")
                break
                
            button_count, button_placeholders = display_backend_response(
                chunk, button_count, columns, button_placeholders
            )
            full_response, message_placeholder = process_chunk_event(
                chunk, full_response, message_placeholder
            )

    # Only append to session state if we got a complete response
    if full_response:
        st.session_state.messages.append({"role": "assistant", "content": full_response})


def display_backend_response(chunk, button_count, columns, button_placeholders):
    """
    The function `display_backend_response` processes search event data to create buttons with shortened
    labels.
    
    :param chunk: The `chunk` parameter seems to be an object that contains information related to an
    event, possibly related to a search operation. It is being used to extract items from the data and
    process them to create button placeholders based on certain conditions. The function then returns
    the updated `button_count` and `button
    :param button_count: The `button_count` parameter in the `display_backend_response` function is used
    to keep track of the number of buttons that have been processed or created so far. It is incremented
    each time a new button is added to the interface
    :param columns: The `columns` parameter in the `display_backend_response` function is used to
    specify the number of columns in the display layout. It is likely used to organize and structure the
    display of the backend response data in a visually appealing way, such as arranging items in a grid
    or table format with a specific
    :param button_placeholders: The `button_placeholders` parameter is a list that stores button
    placeholders. These button placeholders are created dynamically in the `display_backend_response`
    function for each item in the search results. Each button placeholder is assigned a label based on
    the item's link, and a unique key is generated for the button
    :return: The function `display_backend_response` is returning the updated `button_count` and
    `button_placeholders` after processing the `chunk` data in the case where the event is "search".
    """

    if chunk.event == "search":
        for item in json.loads(chunk.data).get("items"):
            button_placeholder = assign_button_placeholder(columns, button_placeholders)
            button_placeholder.button(
                label=item.get("link")[8:42] + "...", key=button_count
            )
            button_count += 1
            button_placeholders.append(button_placeholder)
            time.sleep(0.05)
    return button_count, button_placeholders


def assign_button_placeholder(columns, button_placeholders):
    
    return (
        columns[0].empty() if len(button_placeholders) % 2 == 0 else columns[1].empty()
    )


def process_chunk_event(chunk, full_response, message_placeholder):
    if chunk.event == "token":
        if not message_placeholder:
            message_placeholder = st.empty()
        full_response += chunk.data
        message_placeholder.markdown(full_response + "▌")
    return full_response, message_placeholder


st.title("InternetWhisper")
# Initialize chat history
st.session_state.messages = st.session_state.get("messages", [])

display_chat_messages()

# Accept user input
if prompt := st.chat_input("Ask me a question..."):
    process_user_input(prompt)
    process_backend_response(prompt)
