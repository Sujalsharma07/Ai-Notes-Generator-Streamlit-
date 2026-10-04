import streamlit as st
import mysql.connector
from PyPDF2 import PdfReader
from groq import Groq

client = Groq(api_key=st.secrets["GROQ_API_KEY"])
def db():

    return mysql.connector.connect(

        host="mysql",

        user="root",

        password="root",

        database="ai_notes_generator"

    )
st.title("AI Notes Generator")
menu = st.sidebar.selectbox("Menu", ["Login", "Register"])
if menu == "Register":
    u = st.text_input("Username", key="reg_user")

    p = st.text_input("Password", type="password", key="reg_pass")

    if st.button("Register"):

        d = db()
        c = d.cursor()

        c.execute(
            "CREATE TABLE IF NOT EXISTS users(username VARCHAR(50), password VARCHAR(50))"
        )

        c.execute(
            "INSERT INTO users VALUES(%s,%s)",
            (u, p)
        )

        d.commit()

        st.success("Registered")


if menu == "Login":

    u = st.text_input("Username", key="Log_user")

    p = st.text_input("Password", type="password", key="Log_pass")

    if st.button("Login"):

        d = db()
        c = d.cursor()

        c.execute(
            "SELECT * FROM users WHERE username=%s AND password=%s",
            (u, p)
        )

        if c.fetchone():

            st.session_state["u"] = u

            st.success("Logged in")

        else:

            st.error("Invalid")


if "u" in st.session_state:

    F = st.file_uploader("PDF", type=["pdf"])

    if F:

        r = PdfReader(F)

        t = ""

        for p in r.pages:

            t += p.extract_text() or ""

        if st.button("Generate"):

            response = client.chat.completions.create(

                model="openai/gpt-oss-20b",

                messages=[
                    {
                        "role": "user",
                        "content": f"Make short notes:\n{t[:3000]}"
                    }
                ]

            )

            out = response.choices[0].message.content

            st.write(out)