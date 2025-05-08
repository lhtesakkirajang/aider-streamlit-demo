import os
import streamlit as st
import subprocess
import threading
import time

# ========== Config (adjust your API key and model below) ==========
OPENAI_KEY = os.environ['OPENAI_API_KEY']  # <-- replace with your OpenAI key
AIDER_COMMAND = f"aider --model  o3-mini --api-key openai={OPENAI_KEY} --auto-accept-architect --auto-commits --yes-always --architect --no-auto-test"

# ========== Background Thread: Reads output from aider ==========
def read_output(process, complete_logs, stop_event):
    partial_line = ""
    while not stop_event.is_set():
        char = process.stdout.read(1)  # Read one character at a time
        if char:
            partial_line += char
            if char == "\n":  # If a newline character is encountered
                complete_logs.append(partial_line.rstrip())  # Append the complete line to logs
                partial_line = ""  # Reset the partial line
                # st.experimental_rerun()  # Trigger UI update
        elif process.poll() is not None:  # If the process has ended
            break

    # Ensure any remaining partial line is added before exiting
    if partial_line:
        complete_logs.append(partial_line.rstrip())

    stop_event.set()
    complete_logs.append("🔚 Aider session ended.")
    # st.experimental_rerun()

# ========== Start the aider subprocess ==========
def start_aider():
    return subprocess.Popen(
        AIDER_COMMAND,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        shell=True,
        bufsize=1
    )

# ========== Streamlit App ==========
st.title("💬 Aider Interactive Terminal (Chat-Like)")

# -- Initialize session state --
if "process" not in st.session_state:
    st.session_state.process = None
if "complete_logs" not in st.session_state:
    st.session_state.complete_logs = []
if "reader_thread" not in st.session_state:
    st.session_state.reader_thread = None
if "stop_event" not in st.session_state:
    st.session_state.stop_event = threading.Event()
if "aider_running" not in st.session_state:
    st.session_state.aider_running = False

# -- Start Aider --
if st.button("🚀 aider-install / Start Session", disabled=st.session_state.aider_running):
    try:
        st.session_state.process = start_aider()
        st.session_state.stop_event.clear()
        st.session_state.aider_running = True

        st.session_state.reader_thread = threading.Thread(
            target=read_output,
            args=(st.session_state.process, st.session_state.complete_logs, st.session_state.stop_event),
            daemon=True
        )
        st.session_state.reader_thread.start()
        st.success("✅ Aider session started.")
    except Exception as e:
        st.error(f"❌ Failed to start Aider: {e}")

# -- Display logs --
st.subheader("🖥️ Logs")
st.text_area(
    "Complete Logs",
    "\n".join(st.session_state.complete_logs[-100:]),
    height=400,
    key="complete_log_area",
    disabled=True
)

# Input and controls
if st.session_state.aider_running:
    user_input = st.text_input("📝 Your Prompt:", key="user_prompt")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📤 Send", use_container_width=True):
            if user_input.strip():
                try:
                    st.session_state.process.stdin.write(user_input + "\n")
                    st.session_state.process.stdin.flush()
                    st.success("Prompt sent to Aider.")
                    st.rerun()  # to clear input
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("Type something to send.")
    with col2:
        if st.button("🔄 Refresh Logs", use_container_width=True):
            st.rerun()
    with col3:
        if st.button("🛑 Stop Session", use_container_width=True):
            st.session_state.stop_event.set()
            st.session_state.process.terminate()
            st.session_state.process = None
            st.session_state.aider_running = False
            st.success("🛑 Aider session stopped.")


# Auto-refresh every 1s to simulate live stream
if st.session_state.aider_running:
    time.sleep(1)
    st.rerun()