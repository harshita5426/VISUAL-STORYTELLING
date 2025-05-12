import streamlit as st
import os
from database.db import get_user_stories, delete_story
from datetime import datetime
from fpdf import FPDF

st.set_page_config(page_title="User Gallery", layout="wide")
st.title("📚 My Generated Story Gallery")


if "user_id" not in st.session_state:
    st.warning("Please login from main page.")
    st.stop()

user_id = st.session_state["user_id"]


st.subheader(f"Welcome {st.session_state['username']} 👋 to StoryFusion")


st.subheader("🖼️ My Generated Stories")

stories = get_user_stories(user_id)

if stories:
    stories = [s for s in stories if len(s) > 5 and s[5]]
    stories = sorted(stories, key=lambda x: x[5], reverse=True)

    for s in stories:
        with st.expander(f"{s[2]}"):
            image_path = s[4]
            if os.path.exists(image_path):
                st.image(image_path, use_container_width=True)
            else:
                st.warning("⚠️ Image file not found.")
            
            st.markdown(f"**Description:** {s[3]}")
            timestamp_str = datetime.fromisoformat(s[5]).strftime("%Y-%m-%d %H:%M:%S")
            st.caption(f"🕒 Uploaded on: {timestamp_str}")

            # Download as PDF
            if st.button(f"📥 Download as PDF: {s[2]}", key=f"pdf_{s[0]}"):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                pdf.cell(200, 10, txt=s[2], ln=True, align="C")
                pdf.ln(10)
                pdf.multi_cell(0, 10, txt=s[3])

                if os.path.exists(image_path):
                    pdf.image(image_path, x=10, y=60, w=pdf.w - 20)
                
                pdf_output = f"story_{s[0]}.pdf"
                pdf.output(pdf_output)

                with open(pdf_output, "rb") as f:
                    st.download_button("⬇️ Download PDF", f, file_name=pdf_output)

                os.remove(pdf_output)

            # Add delete button with confirmation
            if st.button(f"🗑️ Delete Story: {s[2]}", key=f"delete_{s[0]}"):
                st.session_state["story_to_delete"] = s[0]
                st.session_state["story_name_to_delete"] = s[2]
                st.rerun()

    if "story_to_delete" in st.session_state:
        st.warning(f"Are you sure you want to delete '{st.session_state['story_name_to_delete']}'?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Yes, delete"):
                delete_story(st.session_state["story_to_delete"])
                st.success("Story deleted successfully.")
                del st.session_state["story_to_delete"]
                del st.session_state["story_name_to_delete"]
                st.experimental_rerun()
        with col2:
            if st.button("❌ Cancel"):
                del st.session_state["story_to_delete"]
                del st.session_state["story_name_to_delete"]
                st.experimental_rerun()

else:
    st.info("No generated stories yet. Try uploading an image to generate one!")
    if st.button("➕ Create Your First Story"):
        st.switch_page("pages/3_StoryFusion.py")  
