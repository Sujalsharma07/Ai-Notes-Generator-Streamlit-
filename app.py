import streamlit as st
import sqlite3
from PyPDF2 import PdfReader
from groq import Groq

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def db():
    
    conn = sqlite3.connect("database.db", check_same_thread=False)
    return conn

st.title("AI Notes Generator")

menu = st.sidebar.selectbox("Menu", ["Login", "Register"])

if menu == "Register":
    u = st.text_input("Username", key="reg_user")
    p = st.text_input("Password", type="password", key="reg_pass")

    if st.button("Register"):
        d = db()
        c = d.cursor()
        c.execute(
            "CREATE TABLE IF NOT EXISTS users(username TEXT, password TEXT)"
        )
        c.execute(
            "INSERT INTO users VALUES(?, ?)",
            (u, p)
        )

        d.commit()
        d.close() 
        st.success("Registered successfully!")

if menu == "Login":
    u = st.text_input("Username", key="Log_user")
    p = st.text_input("Password", type="password", key="Log_pass")

    if st.button("Login"):
        d = db()
        c = d.cursor()

        # Database table pehle hi check kar rahe hain taaki crash na ho
        c.execute(
            "CREATE TABLE IF NOT EXISTS users(username TEXT, password TEXT)"
        )

        # %s ki jagah ? ka use kiya hai
        c.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (u, p)
        )

        if c.fetchone():
            st.session_state["u"] = u
            st.success("Logged in")
            st.rerun() # Page ko refresh karne ke liye taaki PDF uploader turant dikhe
        else:
            st.error("Invalid Username or Password")
        
        d.close()

# Logged in state check
if "u" in st.session_state:
    st.write(f"Welcome, **{st.session_state['u']}**!")
    F = st.file_uploader("PDF", type=["pdf"])

    if F:
        r = PdfReader(F)
        t = ""

        for page in r.pages:
            t += page.extract_text() or ""

        if st.button("Generate"):
            with st.spinner("Generating short notes..."):
                response = client.chat.completions.create(
                    model="openai/gpt-oss-20b", # Groq ke standard model ke sath update kiya hai
                    messages=[
                        {
                            "role": "user",
                            "content": f"Make short notes:\n{t[:3000]}"
                        }
                    ]
                )

                out = response.choices[0].message.content
                st.subheader("Your Short Notes:")
                st.write(out)