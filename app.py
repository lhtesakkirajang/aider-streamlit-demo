import streamlit as st
import threading
import time
import queue

st.title("🔴 Live Stream Demo with st.write_stream & Threading")

# Shared queue for streaming text
stream_queue = queue.Queue()

# Flag to stop the thread (optional)
stop_event = threading.Event()

def background_streaming_task():
    """Simulate a background task that generates streamed text."""
    messages = [
        "Initializing stream...\n",
        "Connecting to data source...\n",
        "Receiving packets...\n",
        "Processing data...\n",
        "Stream complete.\n"
    ]
    for msg in messages:
        if stop_event.is_set():
            break
        stream_queue.put(msg)
        time.sleep(1)

# Button to trigger the stream
if st.button("Start Streaming"):
    # Start the background thread
    thread = threading.Thread(target=background_streaming_task)
    thread.start()

    # Use st.write_stream to display data as it arrives
    def stream_generator():
        while thread.is_alive() or not stream_queue.empty():
            try:
                yield stream_queue.get(timeout=0.1)
            except queue.Empty:
                continue

    st.write_stream(stream_generator)

# Optional stop button (if needed)
# if st.button("Stop Stream"):
#     stop_event.set()
