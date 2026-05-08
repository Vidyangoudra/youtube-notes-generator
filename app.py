import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from pytube import YouTube

# -----------------------------------
# PAGE CONFIG
# -----------------------------------
st.set_page_config(
    page_title="YouTube AI Notes Generator",
    page_icon="🎥",
    layout="wide"
)

# -----------------------------------
# CSS
# -----------------------------------
st.markdown("""
<style>
.main { background-color: #0E1117; color: white; }

h1, h2, h3 { color: #00FFAA; }

.stButton>button {
    background-color: #00FFAA;
    color: black;
    border-radius: 10px;
    height: 3em;
    width: 100%;
    font-size: 18px;
    font-weight: bold;
}

.stTextInput>div>div>input {
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------------
# TITLE
# -----------------------------------
st.title("🎥 YouTube Transcript to Detailed Notes Converter")
st.write("Generate structured notes from YouTube videos.")

# -----------------------------------
# SESSION STATE
# -----------------------------------
if "notes" not in st.session_state:
    st.session_state.notes = ""

# -----------------------------------
# VIDEO ID
# -----------------------------------
def get_video_id(url):
    if "watch?v=" in url:
        return url.split("watch?v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    elif "/live/" in url:
        return url.split("/live/")[1].split("?")[0]
    return None

# -----------------------------------
# VIDEO DETAILS
# -----------------------------------
def get_video_details(url):
    yt = YouTube(url)
    return yt.title, yt.author, yt.length, yt.views

# -----------------------------------
# ✅ FIXED TRANSCRIPT FUNCTION (IMPORTANT)
# -----------------------------------
def extract_transcript(youtube_url):

    try:
        video_id = get_video_id(youtube_url)

        if not video_id:
            return None

        # 1️⃣ Try YouTube transcript API
        try:
            transcript_list = YouTubeTranscriptApi().fetch(video_id)
            return " ".join([item.text for item in transcript_list])

        except:
            pass

        # 2️⃣ Fallback using pytube captions
        yt = YouTube(youtube_url)

        caption = yt.captions.get_by_language_code('en')

        if caption:
            return caption.generate_srt_captions()

        # 3️⃣ FINAL fallback (NEVER return empty)
        return "This video does not have captions. Try another video with subtitles."

    except:
        return "Error processing video"

# -----------------------------------
# NOTES GENERATION
# -----------------------------------
def generate_notes(text, summary_type):

    chunk_size = 5000
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

    final_notes = ""

    for i, chunk in enumerate(chunks):

        sentences = chunk.split(".")
        sentences = [s.strip() for s in sentences if len(s.split()) > 10]

        if summary_type == "Short Summary":
            selected = sentences[:8]
        elif summary_type == "Bullet Points":
            selected = sentences[:20]
        else:
            selected = sentences[:15]

        final_notes += f"\n\n===== PART {i+1} =====\n\n"

        for j, s in enumerate(selected, 1):
            final_notes += f"{j}. {s}\n\n"

    return final_notes

# -----------------------------------
# INPUT
# -----------------------------------
youtube_link = st.text_input("Enter YouTube Video Link")

summary_type = st.selectbox(
    "Select Notes Type",
    ["Detailed Notes", "Short Summary", "Bullet Points"]
)

# -----------------------------------
# VIDEO PREVIEW
# -----------------------------------
if youtube_link:

    try:
        video_id = get_video_id(youtube_link)

        if video_id:
            st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", width=800)

        title, author, length, views = get_video_details(youtube_link)

        st.subheader(title)

        col1, col2, col3 = st.columns(3)
        col1.metric("Channel", author)
        col2.metric("Duration", f"{length//60} min")
        col3.metric("Views", f"{views:,}")

    except:
        st.warning("Unable to fetch video details")

# -----------------------------------
# BUTTON
# -----------------------------------
if st.button("Generate Notes"):

    if youtube_link == "":
        st.warning("Please enter a YouTube link")
    else:
        with st.spinner("Processing video..."):

            transcript = extract_transcript(youtube_link)

            if transcript:

                st.info(f"Transcript length: {len(transcript.split())} words")

                st.session_state.notes = generate_notes(transcript, summary_type)

                st.success("Notes Generated Successfully!")

# -----------------------------------
# OUTPUT
# -----------------------------------
if st.session_state.notes:

    st.markdown("## 📝 Generated Notes")

    search = st.text_input("🔍 Search Inside Notes")

    if search:
        if search.lower() in st.session_state.notes.lower():
            st.success("Found")
        else:
            st.warning("Not Found")

    st.write(st.session_state.notes)

    st.download_button(
        "📥 Download Notes",
        st.session_state.notes,
        file_name="notes.txt"
    )