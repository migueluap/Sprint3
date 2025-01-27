from typing import Optional
import requests
import streamlit as st
import json
from app.settings import API_BASE_URL
from PIL import Image
import time
import os


def login(username: str, password: str) -> Optional[str]:
    """This function calls the login endpoint of the API to authenticate the user
    and get a token.

    Args:
        username (str): email of the user
        password (str): password of the user

    Returns:
        Optional[str]: token if login is successful, None otherwise
    """

    # TODO: Implement the login function
    # Steps to Build the `login` Function:
    #  1. Construct the API endpoint URL using `API_BASE_URL` and `/login`.
    #  2. Set up the request headers with `accept: application/json` and
    #     `Content-Type: application/x-www-form-urlencoded`.
    #  3. Prepare the data payload with fields: `grant_type`, `username`, `password`,
    #     `scope`, `client_id`, and `client_secret`.
    #  4. Use `requests.post()` to send the API request with the URL, headers,
    #     and data payload.
    #  5. Check if the response status code is `200`.
    #  6. If successful, extract the token from the JSON response.
    #  7. Return the token if login is successful, otherwise return `None`.
    #  8. Test the function with various inputs.

    # Construct API endpoint URL
    login_url = f"{API_BASE_URL}/login"

    # st.write(f"Attempting to connect to: {login_url}")
    # Set up headers
    headers = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    # Prepare data payload
    data = {
        "grant_type": "",
        "username": username,
        "password": password,
        "scope": "",
        "client_id": "",
        "client_secret": ""
    }

    try:
        # Send POST request
        response = requests.post(login_url, headers=headers, data=data)

        # Check if login was successful
        if response.status_code == 200:
            # Extract token from response
            token = response.json().get("access_token")
            return token

    except requests.exceptions.RequestException:
        pass

    return None


def predict(token: str, uploaded_file: Image) -> requests.Response:
    """This function calls the predict endpoint of the API to classify the uploaded
    image.

    Args:
        token (str): token to authenticate the user
        uploaded_file (Image): image to classify

    Returns:
        requests.Response: response from the API
    """
    # TODO: Implement the predict function
    # Steps to Build the `predict` Function:
    #  1. Create a dictionary with the file data. The file should be a
    #     tuple with the file name and the file content.
    #  2. Add the token to the headers.
    #  3. Make a POST request to the predict endpoint.
    #  4. Return the response.
    #response = None
    #return response

    url = f"{API_BASE_URL}/model/predict" #Ahora usa la URL correcta

    # 1. Crear un diccionario con los datos del archivo
    files = {'file': (uploaded_file.name, uploaded_file.getvalue())}  #Se usa el nombre del archivo esperado

    # 2. Agregar el token en los headers
    headers = {'Authorization': f'Bearer {token}'}

    try:
        response = requests.post(url, files=files, headers=headers)
        response.raise_for_status()  # Lanza un error si el status code es 4xx o 5xx
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error en la solicitud: {e}")




def send_feedback(
    token: str, feedback: str, score: float, prediction: str, image_file_name: str
) -> requests.Response:
    """This function calls the feedback endpoint of the API to send feedback about
    the classification.
    Args:
        token (str): token to authenticate the user
        feedback (str): string with feedback
        score (float): confidence score of the prediction
        prediction (str): predicted class
        image_file_name (str): name of the image file
    Returns:
        requests.Response: _description_
    """

      # TODO: Implement the send_feedback function
    # Steps to Build the `send_feedback` Function:
    # 1. Create a dictionary with the feedback data including feedback, score,
    #    predicted_class, and image_file_name.
    # 2. Add the token to the headers.
    # 3. Make a POST request to the feedback endpoint.
    # 4. Return the response.


    # Construct feedback endpoint URL
    #feedback_url = f"{API_BASE_URL}/model/feedback"
    feedback_url = f"{API_BASE_URL}/feedback"
   
   # Create headers with token
    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Create feedback data dictionary
    feedback_data = {
        "feedback": feedback,
        "score": score,
        "predicted_class": prediction,
        "image_file_name": image_file_name
    }

 

    try:
        # Send POST request to feedback endpoint
        response = requests.post(
            feedback_url,
            headers=headers,
            json=feedback_data,
            #timeout=30
        )

        # Check if response is successful
        # if response.status_code != 200:
        #     st.error(f"Error sending feedback: {response.status_code} - {response.text}")

        return response

    except requests.exceptions.RequestException as e:
        st.error(f"Connection error while sending feedback: {str(e)}")
        return None
    #response = None
    #return response



# Interfaz de usuario
st.set_page_config(page_title="Image Classifier", page_icon="📷")
st.markdown(
    "<h1 style='text-align: center; color: #4B89DC;'>Image Classifier</h1>",
    unsafe_allow_html=True,
)
# Formulario de login
if "token" not in st.session_state:
    st.markdown("## Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        token = login(username, password)
        if token:
            st.session_state.token = token
            st.success("Login successful!")
        else:
            st.error("Login failed. Please check your credentials.")
else:
    st.success("You are logged in!")
if "token" in st.session_state:
    token = st.session_state.token
    # Cargar imagen
    uploaded_file = st.file_uploader("Sube una imagen", type=["jpg", "jpeg", "png"])
    print(type(uploaded_file))
    # Mostrar imagen escalada si se ha cargado
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Imagen subida", width=300)
    if "classification_done" not in st.session_state:
        st.session_state.classification_done = False
    # Botón de clasificación
    if st.button("Classify"):
        if uploaded_file is not None:
            response = predict(token, uploaded_file)
            if response and response.status_code == 200:
                result = response.json()
                st.write(f"**Prediction:** {result['prediction']}")
                st.write(f"**Score:** {result['score']}")
                st.session_state.classification_done = True
                st.session_state.result = result
            else:
                st.error(f"{response.status_code}: {response.content}")
                #st.error("Error classifying image. Please try again.")
        else:
            st.warning("Please upload an image before classifying.")
    # Mostrar campo de feedback solo si se ha clasificado la imagen
    if st.session_state.classification_done:
        st.markdown("## Feedback")
        feedback = st.text_area("If the prediction was wrong, please provide feedback.")
        if st.button("Send Feedback"):
            if feedback:
                token = st.session_state.token
                result = st.session_state.result
                score = result["score"]
                prediction = result["prediction"]
                image_file_name = result.get("image_file_name", "uploaded_image")
                response = send_feedback(
                    token, feedback, score, prediction, image_file_name
                )
                if response.status_code == 201:
                    st.success("Thanks for your feedback!")
                else:
                    st.error("Error sending feedback. Please try again.")
            else:
                st.warning("Please provide feedback before sending.")
                st.warning("Please provide feedback before sending.")
    # Pie de página
    st.markdown("<hr style='border:2px solid #4B89DC;'>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center; color: #4B89DC;'>2024 Image Classifier App</p>",
        unsafe_allow_html=True,
    )
