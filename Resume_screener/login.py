import streamlit as st
import sqlite3
st.title("AI Resume Screener - Login")
#db connection
conn = sqlite3.connect('resume_data.db',check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")
conn.commit()

#session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

menu = ["Login", "Signup"]
choice = st.selectbox("Menu", menu)

# ---------------- SIGNUP ----------------
if choice == "Signup":
    st.subheader("Create a new account")
    new_user = st.text_input("Username")
    new_password = st.text_input("Password", type='password')
    if st.button("Signup"):
        if new_user and new_password:
            try:
                cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (new_user, new_password))
                conn.commit()
                st.success("Account created successfully! Please login.")
            except sqlite3.IntegrityError:
                st.error("Username already exists. Please choose a different one.")
        else:
            st.error("Please enter both username and password.")

# ---------------- LOGIN ----------------
elif choice == "Login":
    st.subheader("Login to your account")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    if st.button("Login"):
        if username and password:
            cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
            result = cursor.fetchone()
            if result:
                st.session_state.logged_in = True
                st.success(f"Welcome, {username}!")
                st.switch_page("pages/resume_screener.py")
                st.switch_page("pages/resume_advisor.py")
            else:
                st.error("Invalid username or password.")
        else:
            st.error("Please enter both username and password.")
