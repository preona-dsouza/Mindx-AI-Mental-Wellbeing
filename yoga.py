import streamlit as st
import time

# Yoga Poses Data with Time (in seconds)
yoga_poses = {
    "Stressed or Anxious": [
        {"name": "Child's Pose (Balasana)", "time": 60, 
         "description": "Relax your body and focus on deep breathing. Sit back on your heels, stretch your arms forward, and rest your forehead on the mat.", 
         "video_link": "https://www.youtube.com/watch?v=fzM3uSrr4-g"},
        {"name": "Cat-Cow Pose (Marjaryasana-Bitilasana)", "time": 90, 
         "description": "Alternate between arching your back (cow pose) and rounding it (cat pose) while coordinating with your breath.", 
         "video_link": "https://www.youtube.com/watch?v=wE2LM90CXKg"},
        {"name": "Legs-Up-the-Wall Pose (Viparita Karani)", "time": 120, 
         "description": "Lie on your back and lift your legs against a wall. Stay relaxed and breathe deeply.", 
         "video_link": "https://www.youtube.com/watch?v=7SzdiqW8vTk"}
    ],
    "Sad or Low": [
        {"name": "Cobra Pose (Bhujangasana)", "time": 45, 
         "description": "Lie on your stomach, place your hands under your shoulders, and lift your chest while keeping your hips grounded.", 
         "video_link": "https://www.youtube.com/watch?v=jX2-qT_rMaU"},
        {"name": "Bridge Pose (Setu Bandhasana)", "time": 60, 
         "description": "Lie on your back, bend your knees, and lift your hips to create a gentle backbend.", 
         "video_link": "https://www.youtube.com/watch?v=f_EfphhfH9A"}
    ]
    # Add more moods and poses as needed
}

# Streamlit App
st.title("Dynamic Yoga Routine Recommender")
st.subheader("Find a step-by-step yoga routine based on your mood!")

# User Input
emotion = st.selectbox("How are you feeling?", list(yoga_poses.keys()))

# Display Routine
if emotion:
    st.write(f"### Your Yoga Routine for '{emotion}':")
    selected_poses = yoga_poses[emotion]
    
    # Display all poses with descriptions
    for pose in selected_poses:
        st.write(f"**{pose['name']}** - {pose['time']} seconds")
        st.write(pose['description'])
        st.write(f"[Watch Tutorial Video]({pose['video_link']})")

    # Dynamic Timer for Each Pose
    if st.button("Start Routine"):
        st.write("### Let's begin your yoga session!")
        for pose in selected_poses:
            st.write(f"🧘 Now: {pose['name']}")
            st.write(pose['description'])
            # for t in range(pose["time"], 0, -1):
            #     st.write(f"Time left: {t} seconds", end="\r")
            #     time.sleep(1)
            # st.success(f"✅ Finished {pose['name']}!")
            # st.write("---")
        
        st.write("🎉 Great job completing your routine! Namaste. 🙏")

# Footer
st.write("Developed for wellness and mindfulness.")