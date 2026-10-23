import os
import streamlit as st
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

st.set_page_config(page_title="AutoPublisher Pro", page_icon="⚡", layout="centered")

st.markdown("""
    <style>
    .main-header { 
        background: #ffcc00; padding: 20px; border-radius: 15px; 
        text-align: center; color: #111; font-weight: bold; font-size: 24px; 
        margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stButton>button { 
        background-color: #ff5722; color: white; font-size: 18px; 
        font-weight: bold; border-radius: 8px; width: 100%; padding: 12px; 
    }
    .badge { 
        background: #d4edda; color: #155724; padding: 4px 8px; 
        border-radius: 4px; font-size: 14px; font-weight: bold; 
    }
    </style>
    <div class="main-header">⚡ AutoPublisher Pro<br><span style="font-size: 14px; font-weight: normal;">YouTube Automation Dashboard</span></div>
""", unsafe_allow_html=True)

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def get_youtube_service():
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        return build('youtube', 'v3', credentials=creds)
    else:
        raise Exception("❌ 'token.json' file nahi mili! Please repo mein token.json upload karein.")

st.markdown("### 🔗 Connected Accounts")
st.markdown("**YouTube Channel:** <span class='badge'>Connected Safe (API v3)</span>", unsafe_allow_html=True)
st.markdown("---")
st.markdown("### 📤 Bulk Upload & Smart Scheduler")

uploaded_files = st.file_uploader("Select Multiple Videos from Gallery", type=["mp4", "mov", "avi", "mkv"], accept_multiple_files=True)

title_input = st.text_input("Default Title (For Batch)", "My Automated Video")
desc_input = st.text_area("Video Description", "Uploaded automatically via AutoPublisher Dashboard")

enable_schedule = st.checkbox("⏰ Schedule Video Publish Time?")
publish_date, publish_time = None, None

if enable_schedule:
    col1, col2 = st.columns(2)
    with col1:
        publish_date = st.date_input("Publish Date")
    with col2:
        publish_time = st.time_input("Publish Time")

if st.button("🚀 Upload & Schedule All Videos"):
    if not uploaded_files:
        st.error("❌ Pehle kam se kam ek video select karo!")
    else:
        with st.spinner("Uploading videos to YouTube... Please wait ⏳"):
            try:
                youtube = get_youtube_service()
                success_count = 0
                
                for idx, uploaded_file in enumerate(uploaded_files):
                    temp_path = f"/tmp/{uploaded_file.name}"
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    video_title = f"{title_input} ({idx+1})" if len(uploaded_files) > 1 else title_input

                    body = {
                        'snippet': {
                            'title': video_title,
                            'description': desc_input,
                            'tags': ['automation', 'shorts', 'android'],
                            'categoryId': '22'
                        },
                        'status': {
                            'selfDeclaredMadeForKids': False
                        }
                    }

                    if enable_schedule and publish_date and publish_time:
                        dt = datetime.combine(publish_date, publish_time)
                        formatted_time = dt.strftime('%Y-%m-%dT%H:%M:%S.000Z')
                        body['status']['privacyStatus'] = 'private'
                        body['status']['publishAt'] = formatted_time
                    else:
                        body['status']['privacyStatus'] = 'private'

                    media = MediaFileUpload(temp_path, chunksize=-1, resumable=True)
                    request_api = youtube.videos().insert(
                        part=','.join(body.keys()),
                        body=body,
                        media_body=media
                    )

                    response = None
                    while response is None:
                        status, response = request_api.next_chunk()
                    
                    success_count += 1

                st.success(f"🎉 SUCCESS! Total **{success_count}** videos successfully uploaded & scheduled!")
            except Exception as e:
                st.error(f"❌ Upload Error: {str(e)}")
