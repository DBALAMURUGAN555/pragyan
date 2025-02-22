import streamlit as st
import requests
import time

st.title("🔐 Secure Authentication System")

page = st.sidebar.radio("Navigation", ["Login", "Signup"])

api_url = "http://localhost:5000"

# SIGNUP
if page == "Signup":
    st.subheader("📝 Create a New Account")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Register"):
        if not username or not password or not confirm_password:
            st.warning("⚠️ All fields are required!")
        elif password != confirm_password:
            st.error("❌ Passwords do not match!")
        else:
            response = requests.post(f"{api_url}/register", json={"username": username, "password": password})
            if response.status_code == 201:
                st.success("✅ Account created successfully! You can now log in.")
            else:
                st.error("❌ " + response.json().get("error", "Something went wrong."))

# LOGIN
if page == "Login":
    st.subheader("🔑 Login to Your Account")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        response = requests.post(f"{api_url}/login", json={"username": username, "password": password})
        if response.status_code == 200:
            st.success(f"✅ Welcome {username}!")

            with st.expander("⚠️ Behavioral Authentication Required"):
                start_time = time.time()
                key_input = st.text_input("Type this exact phrase: 'securelogin'")
                end_time = time.time()
                
                mouse_clicks = st.button("Click me exactly 3 times")
                
                typing_speed = end_time - start_time
                mouse_movements = [15, 20, 30]  # Simulated values
                
                if key_input == "securelogin" and mouse_clicks:
                    track_response = requests.post(f"{api_url}/track", json={
                        "user_id": username,
                        "keyboard_intervals": [typing_speed],
                        "mouse_movements": mouse_movements
                    })
                    result = track_response.json()
                    st.info(f"Behavior Check: {result['status']}")
                else:
                    st.warning("❌ Authentication failed! Try again.")
        else:
            st.error("❌ Invalid username or password!")
