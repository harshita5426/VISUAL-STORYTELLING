import streamlit as st
from database.db import get_all_stories, delete_story

st.set_page_config(page_title="Admin Panel", layout="wide")
st.title("🛠️ Admin Panel")

# Ensure the user is logged in and is an admin
if "username" not in st.session_state or st.session_state["user_type"] != "admin":
    st.warning("Access Denied. Please login as admin.")
    st.stop()

# Fetch all stories from the database
stories = get_all_stories()

# Display all stories
for s in stories:
    with st.expander(f"📖 {s[2]} by {s[1]}"):
        st.image(s[4], width=400)
        st.write(s[3])

        
        delete_confirm = st.button("Delete", key=f"delete_{s[0]}")
        if delete_confirm:
            confirm = st.checkbox(f"Are you sure you want to delete the story titled '{s[2]}'?")
            if confirm:
                delete_story(s[0])
                st.success(f"Story '{s[2]}' deleted successfully.")
                st.experimental_rerun()  # Refresh the page to show updated stories
            else:
                st.warning("Story deletion cancelled.")
