import streamlit as st
from utils.auth import login_user, signup_user, hash_password, verify_password
from database.db import create_tables, get_user_type


create_tables()
print("✅ Tables created!")

st.set_page_config(page_title="Art of Visual Storytelling", layout="wide")

st.title("🎨 Art of Visual Storytelling")

menu = ["Login", "Sign Up"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Login":
    st.subheader("Login Section")

    username = st.text_input("Username")
    password = st.text_input("Password", type='password')

    if st.button("Login"):
        success, user_type, user_id = login_user(username, password)

        if success:
            st.success("Login successful!")
            st.session_state["user_type"] = user_type
            st.session_state["username"] = username
            st.session_state["user_id"] = user_id
            # Redirect based on user type
            if user_type == "admin":
                st.switch_page("pages/1_Admin_Panel.py")
            else:
                st.switch_page("pages/2_User_Gallery.py")
        else:
            st.error("Incorrect Username/Password")

elif choice == "Sign Up":
    st.subheader("Create New Account")
    new_user = st.text_input("Username")
    new_pass = st.text_input("Password", type='password')
    user_type = st.selectbox("Role", ["user", "admin"])

    if st.button("Sign Up"):
        signup_user(new_user, new_pass, user_type)
        st.success("Account Created! Go to Login")
