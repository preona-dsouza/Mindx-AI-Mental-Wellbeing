import streamlit as st
import pandas as pd
from textblob import TextBlob
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from project_paths import TRANSCRIPTIONS_CSV

# Function to analyze sentiment
def analyze_sentiment(text):
    analysis = TextBlob(text)
    return analysis.sentiment.polarity

# Function to convert sentiment score to a rating out of 5
def score_to_rating(score):
    return round((score + 1) * 2.5)  # Scale from -1 to 1 to 0 to 5

# Function to predict mood based on sentiment score
def predict_mood(score):
    if score > 0.5:
        return "Happy"
    elif score > 0:
        return "Content"
    elif score == 0:
        return "Neutral"
    elif score > -0.5:
        return "Sad"
    else:
        return "Angry"

# Function to create a PDF from the DataFrame
def create_pdf(df, overall_rating, overall_mood, resources, music):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Title
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, height - 50, "Sentiment Analysis Results")

    # Overall rating and mood
    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, height - 80, f"Overall Rating: {overall_rating}/5")
    p.drawString(100, height - 100, f"Mood: {overall_mood}")

    # Resources
    p.setFont("Helvetica", 12)
    p.drawString(100, height - 120, "Recommended Resources:")
    y = height - 140
    for resource in resources:
        p.linkURL(resource['link'], (100, y, 500, y + 20), relative=0)  # Create a clickable link
        p.drawString(100, y, resource['title'])  # Draw the title
        y -= 20  # Move down for the next resource

    # # Locations
    # p.setFont("Helvetica", 12)
    # p.drawString(100, y, "Recommended Locations:")
    # y -= 20
    # for location in locations:
    #     p.drawString(100, y, location)  # Draw the location
    #     y -= 20  # Move down for the next location

    # Music
    p.setFont("Helvetica", 12)
    p.drawString(100, y, "Recommended Relaxing Music:")
    y -= 20
    for song in music:
        p.drawString(100, y, song['title'])  # Draw the song title
        y -= 20  # Move down for the next song

    # Column headers
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Message")
    p.drawString(300, y, "Sentiment Score")
    p.drawString(450, y, "Sentiment Analysis")

    # Add data to PDF
    p.setFont("Helvetica", 10)
    y -= 20  # Move down for the data
    for index, row in df.iterrows():
        p.drawString(50, y, str(row['message']))
        p.drawString(300, y, str(row['sentiment_score']))
        p.drawString(450, y, str(row['sentiment_analysis']))
        y -= 20  # Move down for the next row

    p.save()
    buffer.seek(0)
    return buffer

# Function to get resources based on overall mood
 
def get_resources(overall_mood):
    resources ={
    "Happy": [
          {"title": "Happify", "link": "https://www.happify.com/"},  # App for mood boosting activities
          #{"title": "Headspace", "link": "https://www.headspace.com/"},  # Meditation app
          {"title": "Motivational Video: 'No EXCUSES - Best Motivational Video' by Ben Lionel Scott", "link": "http://www.youtube.com/watch?v=wnHW6o8WMas"},
          {"title": "Motivational Video: 'LOCK IN FOR 2025 - New Year Motivational Speech Video' by Motiversity", "link": "http://www.youtube.com/watch?v=5WasnbQQad4"}
      ],
    "Content": [
        {"title": "Mindfulness and How It Can Change Your Life by Richard J. Davidson", "link": "https://www.youtube.com/watch?v=7CBfCW67xT8"},
        {"title": "The Science of Mindfulness by Dr. Shauna Shapiro", "link": "https://www.youtube.com/watch?v=IeblJdB2-Vo"},
        {"title": "The Art of Stillness by Pico Iyer", "link": "https://www.ted.com/talks/pico_iyer_the_art_of_stillness"},
        {"title": "The Power of Vulnerability by Brené Brown", "link": "https://www.ted.com/talks/brene_brown_the_power_of_vulnerability"},
        {"title": "Train Your Mind for Peak Performance by Dr. Alia Crum", "link": "https://www.youtube.com/watch?v=0tqq66zwa7g"}
    ],
    "Neutral": [
        {"title": "The Paradox of Choice by Barry Schwartz", "link": "https://www.ted.com/talks/barry_schwartz_the_paradox_of_choice"},
        {"title": "How to Make Stress Your Friend by Kelly McGonigal", "link": "https://www.ted.com/talks/kelly_mcgonigal_how_to_make_stress_your_friend"},
        {"title": "Atomic Habits: The 4 Laws of Behavior Change by James Clear", "link": "https://www.youtube.com/watch?v=U_nzqnXWvSo"},
        {"title": "The Power of Now by Eckhart Tolle (Lecture)", "link": "https://www.youtube.com/watch?v=1W3sC94ssrE"},
        {"title": "Designing Your Life by Bill Burnett", "link": "https://www.youtube.com/watch?v=SngzQQO15vE"}
    ],
    "Sad": [
        {"title": "There's No Shame in Taking Care of Your Mental Health by Sangu Delle", "link": "https://www.ted.com/talks/sangu_delle_there_s_no_shame_in_taking_care_of_your_mental_health"},
        {"title": "The Secret to Overcoming Depression by Johann Hari", "link": "https://www.youtube.com/watch?v=MB5IX-np5fE"},
        {"title": "Emotional First Aid by Guy Winch", "link": "https://www.ted.com/talks/guy_winch_the_case_for_emotional_hygiene"},
        {"title": "Healing Trauma by Dr. Bessel van der Kolk", "link": "https://www.youtube.com/watch?v=53RX2ESIqsM"},
        {"title": "This Could Be Why You're Depressed and Anxious by Johann Hari", "link": "https://www.ted.com/talks/johann_hari_this_could_be_why_you_re_depressed_and_anxious"}
    ],
    "Angry": [
        {"title": "How to Manage Your Anger? Ft. Juna Mustad", "link": "https://youtu.be/Oa91XgiDGbU?si=PN_vtQirzwG_b3ny"},
        {"title": "Top 9 Key Ideas | Arun Gandhi | The Gift of Anger | Philosophy", "link": "https://www.youtube.com/watch?v=euy-c78yr4g"},
        #{"title": "Understanding and Addressing Anger in Relationships by Dr. John Gottman", "link": "https://www.youtube.com/watch?v=8LdsTk7H2zQ"},
        {"title": "Nonviolent Communication and Dealing with Anger by Marshall Rosenberg", "link": "https://www.youtube.com/watch?v=LSGfqyhleUA"}
    ]
}

    return resources.get(overall_mood, [])
# Function to get locations based on overall mood
# def get_locations(overall_mood):
#     locations = {
#         "Happy": ["Local Park", "Beach", "Amusement Park"],
#         "Content": ["Library", "Coffee Shop", "Art Gallery"],
#         "Neutral": ["Community Center", "Shopping Mall", "Public Garden"],
#         "Sad": ["Counseling Center", "Support Group", "Quiet Cafe"],
#         "Angry": ["Meditation Center", "Yoga Studio", "Nature Trails"]
#     }
#     return locations.get(overall_mood, [])

# Function to get music recommendations based on overall mood
def get_music(overall_mood):
    music = {
        "Happy": [
            {"title": "Happy - relaxing songs", "url": "https://youtu.be/hlWiI4xVXKY?si=798zF9Rm39SRRMRy"},
            {"title": "Relaxing music", "url": "https://youtu.be/AKy6Jx59fis?si=MpjOZqXq_N7ue9cD"},
            {"title": "Guitar relaxing music", "url": "https://youtu.be/pd4j9osCNT4?si=DXc4dOxsT3h6lrcR"}
        ],
        "Content": [
            {"title": "Relaxing songs", "url": "https://youtu.be/BHACKCNDMW8?si=iy0FFb91o8OrTKms"},
            {"title": "Mood lightening", "url": "https://www.youtube.com/live/RHIzSBRZ15M?si=pUC4PuiKo5c7uUnv"},
            {"title": "Jazz ,music", "url": "https://www.youtube.com/live/Cm9TrViv7HU?si=ekutBnvAm7jOeC68"}
        ],
        "Neutral": [
            {"title": "Beautiful relaxing music", "url": "https://youtu.be/lFcSrYw-ARY?si=PU0eEin0IZ4iwdym"},
            {"title": "River Flows in You - Yiruma", "url": "https://youtu.be/bX0zIR0RMcc?si=GfcBD30V2B9kdTV3"},
            {"title": "Clair de Lune - Claude Debussy", "url": "https://youtu.be/m0FNHDP-Tlk?si=GO4bi-y0n2B-Gwq5"}
        ],
        "Sad": [
            {"title": "Sad relaxing", "url": "https://youtu.be/L5vMKOx17cY?si=lQeqOWasP-uTebzA"},
            {"title": "Mood Booster", "url": "https://youtu.be/ljnGl5nvUJY?si=hE4E0ibu2SFdI1ry"},
            {"title": "Stress relief", "url": "https://youtu.be/lFcSrYw-ARY?si=BGqhK__Y1lw30oTg"}
        ],
        "Angry": [
            {"title": "Beat your anger", "url": "https://youtu.be/de2TdvDaS5A?si=E7H5ULpYnq4fdQyB"},
            {"title": "inner healing music", "url": "https://youtu.be/T235jK9xR8Q?si=twW-TSh0Dmz9vIOD"},
            {"title": "Anger relieving music", "url": "https://youtu.be/kEvTlSBg8cs?si=QtU2qYHKFsJMAgIA"}
        ]
    }

    return music.get(overall_mood, [])

# Yoga Poses Data with Time (in seconds)
yoga_poses = {
    "Content": [
        {
            "name": "Child's Pose (Balasana)",
            "time": 60,
            "description": "Resting pose to calm the mind and release tension in the back and shoulders.",
            "video_link": "https://www.youtube.com/watch?v=zqwK6J3yHfA"
        },
        {
            "name": "Easy Pose (Sukhasana)",
            "time": 60,
            "description": "Simple seated pose for grounding and meditation.",
            "video_link": "https://www.youtube.com/watch?v=lnXchPpbutE"
        },
        {
            "name": "Cat-Cow Pose (Marjaryasana-Bitilasana)",
            "time": 60,
            "description": "Gentle backbend and forward fold to release tension in the spine.",
            "video_link": "https://www.youtube.com/watch?v=y39PrKY_4JM"
        },
        {
            "name": "Downward-Facing Dog (Adho Mukha Svanasana)",
            "time": 60,
            "description": "Inversion to improve circulation and reduce stress.",
            "video_link": "https://www.youtube.com/watch?v=j97SSGsnCAQ"
        }],
        "Neutral": [
        {
         "name": "Legs-Up-the-Wall Pose (Viparita Karani)",
            "time": 120,
            "description": "Lie on your back and lift your legs against a wall. Stay relaxed and breathe deeply.",
            "video_link": "https://www.youtube.com/watch?v=_OQEIiZLY-0"
        },
        {
            "name": "Shoulder Stand (Salamba Sarvangasana)",
            "time": 60,
            "description": "Inverted pose to improve circulation and reduce stress (advanced pose, practice with guidance).",
            "video_link": "https://www.youtube.com/watch?v=-JecKm9OiOQ"
        },
    ],
    "Sad": [
        {
            "name": "Warrior II (Virabhadrasana II)",
            "time": 60,
            "description": "Grounding and empowering pose to boost mood and confidence.",
            "video_link": "https://www.youtube.com/watch?v=4Ejz7IgODlU"
        },
        {
            "name": "Triangle Pose (Trikonasana)",
            "time": 60,
            "description": "Strengthens legs and core, improves balance and focus.",
            "video_link": "https://www.youtube.com/watch?v=upFYlxZHif0"
        },
        {
            "name": "Camel Pose (Ustrasana)",
            "time": 30,
            "description": "Opens the chest and improves breathing, can uplift mood.",
            "video_link": "https://www.youtube.com/watch?v=SHi7k92QJlg"
        },
        {
            "name": "Inversions (if practiced safely)",
            "time": 30,
            "description": "Increase blood flow to the brain and can improve mood.",
            "video_link": "https://www.youtube.com/watch?v=9YX4nlXuqso"
        },
        {
            "name": "Supported Bridge Pose (Setu Bandha Sarvangasana)",
            "time": 60,
            "description": "Gentle backbend to open the chest and improve mood.",
            "video_link": "https://www.youtube.com/watch?v=NnbvPeAIhmA"
        }
    ],
    "Angry": [
        {
            "name": "Wide-Legged Forward Fold (Prasarita Padottanasana)",
            "time": 60,
            "description": "Calming and grounding pose to release tension and frustration.",
            "video_link": "https://www.youtube.com/watch?v=F7you4Sw1o0"
        },
        {
            "name": "Twisting poses (Seated Twist, Supine Twist)",
            "time": 60,
            "description": "Release tension in the spine and improve digestion.",
            "video_link": "https://www.youtube.com/watch?v=ciGK6HyYqV4"
        },
        {
            "name": "Cooling poses (like Child's Pose or Legs-Up-the-Wall Pose)",
            "time": 60,
            "description": "Calm the nervous system.",
            "video_link": "https://www.youtube.com/watch?v=zqwK6J3yHfA"
        },
    ],
    "Happy": [
        {
            "name": "Sun Salutations (Surya Namaskar)",
            "time": 120,
            "description": "Energizing and uplifting sequence of poses.",
            "video_link": "https://m.youtube.com/watch?v=ZP34IA0d8LI&t=12s"
        },
        {
            "name": "Dancer's Pose (Natarajasana)",
            "time": 30,
            "description": "Improves balance and increases energy.",
            "video_link": "https://www.youtube.com/watch?v=TXNgRNsqcPo"
        },
        {
            "name": "Inversions (if practiced safely)",
            "time": 30,
            "description": "Can boost mood and increase energy.",
            "video_link": "https://www.youtube.com/watch?v=9YX4nlXuqso"
        },
        {
            "name": "Heart openers (like Camel Pose or Wheel Pose - practice with guidance)",
            "time": 30,
            "description": "Open the chest and promote feelings of joy.",
            "video_link": "https://www.youtube.com/watch?v=SHi7k92QJlg"
        },
        {
            "name": "Playful poses like Happy Baby Pose to release tension and uplift the mood",
            "time": 30,
            "description": "Release tension and uplift the mood.",
            "video_link": "https://www.youtube.com/watch?v=Rg8L0_ZDick"
        }
    ]
}

# Streamlit app layout
st.title("Mental Healthcare Chatbot Sentiment Analysis and Yoga Routine Recommender")

# Directly read the CSV file from a specified path
csv_file_path = TRANSCRIPTIONS_CSV
if not csv_file_path.is_file():
    st.warning("No transcription history was found yet. Use the voice chatbot to create a transcription, then open this page again.")
    st.stop()
df = pd.read_csv(csv_file_path)
if df.empty or "message" not in df.columns:
    st.warning("The transcription file is empty or does not contain the required 'message' column.")
    st.stop()

# Display the uploaded data
st.write("### Uploaded Data:")
st.dataframe(df)

# Analyze sentiment for each message
df['sentiment_score'] = df['message'].apply(analyze_sentiment)
df['sentiment_analysis'] = df['sentiment_score'].apply(predict_mood)

# Calculate overall rating and mood
overall_rating = score_to_rating(df['sentiment_score'].mean())
overall_mood = predict_mood(df['sentiment_score'].mean())

# Display results
st.write("### Sentiment Analysis Results:")
st.dataframe(df)

# Get recommended resources, locations, and music
resources = get_resources(overall_mood)
# locations = get_locations(overall_mood)
music = get_music(overall_mood)

# Create PDF report
if st.button("Generate PDF Report", key="generate_pdf_button"):
    pdf_buffer = create_pdf(df, overall_rating, overall_mood, resources, music)
    st.download_button("Download PDF", pdf_buffer, "sentiment_analysis_report.pdf", key="download_pdf_button")

# Display overall rating and mood
st.write(f"### Overall Rating: {overall_rating}/5")
st.write(f"### Predicted Mood: {overall_mood}")

# Display recommended resources as clickable links
st.write("### Recommended Resources:")
for resource in resources:
    st.markdown(f"- [{resource['title']}]({resource['link']})")

# # Display recommended locations
# st.write("### Recommended Locations:")
# for location in locations:
#     st.markdown(f"- {location}")

# Display recommended yoga routine
st.write("### Recommended Yoga Routine:")
selected_poses = yoga_poses[overall_mood]

# Display all poses with descriptions and videos
for pose in selected_poses:
    st.write(f"**{pose['name']}** - {pose['time']} seconds")
    st.write(pose['description'])
    st.video(pose['video_link'])  # Embed the video instead of just a link


# Display recommended relaxing music and play it
st.write("### Recommended Relaxing Music:")
for song in music:
    st.markdown(f"- {song['title']}")
    st.video(song['url'])  # Play the music using the YouTube URL


import os
def truncate_csv():
    file_path = TRANSCRIPTIONS_CSV
    if os.path.exists(file_path):
        os.remove(file_path)
  

if st.button('Go to Login Page'):
            truncate_csv()
            st.markdown('<a href="http://127.0.0.1:5500/front/login.html" target="_self">Go to Login</a>', unsafe_allow_html=True)

# Footer
st.write("Developed for wellness and mindfulness.")