import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import glob
from gtts import gTTS
from googletrans import Translator

# Page configuration
st.set_page_config(
    page_title="Traductor Profesional",
    page_icon="🌎",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main > div {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3rem;
    }
    .css-1d391kg {
        padding: 2rem 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar content
with st.sidebar:
    st.title("🌎 Traductor Universal")
    st.markdown("---")
    st.subheader("Acerca de la aplicación")
    st.write("""
    Esta herramienta profesional de traducción te permite:
    
    • Traducir voz a texto en múltiples idiomas
    • Escuchar la pronunciación correcta
    • Seleccionar diferentes acentos
    • Obtener traducciones precisas
    
    ### Cómo usar:
    1. Presiona el botón de micrófono
    2. Habla claramente lo que deseas traducir
    3. Selecciona el idioma de entrada y salida
    4. Elige el acento deseado
    5. Presiona 'Convertir' para obtener tu traducción
    
    ### Idiomas soportados:
    Incluye una amplia gama de idiomas principales 
    como inglés, español, francés, alemán, portugués 
    y más.
    """)
    
    st.markdown("---")
    st.caption("Desarrollado con ❤️ usando Streamlit")

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.title("🎙️ Traductor Universal")
    st.subheader("Tu asistente de traducción profesional")

with col2:
    image = Image.open('OIG7.jpg')
    st.image(image, width=200)

st.markdown("---")

# Voice input section
st.write("### 🎤 Entrada de Voz")
st.write("Presiona el botón y habla claramente lo que deseas traducir")

stt_button = Button(label="🎤 Iniciar Grabación", width=300, height=50)

stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
 
    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if ( value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
    """))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)

if result:
    if "GET_TEXT" in result:
        st.info(f"Texto detectado: {result.get('GET_TEXT')}")
    
    try:
        os.mkdir("temp")
    except:
        pass

    text = str(result.get("GET_TEXT"))
    
    # Language selection
    st.markdown("### 🌍 Configuración de Idiomas")
    col1, col2 = st.columns(2)
    
    with col1:
        in_lang = st.selectbox(
            "Idioma de Entrada",
            ("Español", "Inglés", "Francés", "Alemán", "Portugués", "Bengali", 
             "Coreano", "Mandarín", "Japonés")
        )
    
    language_codes = {
        "Español": "es", "Inglés": "en", "Francés": "fr",
        "Alemán": "de", "Portugués": "pt", "Bengali": "bn",
        "Coreano": "ko", "Mandarín": "zh-cn", "Japonés": "ja"
    }
    
    input_language = language_codes[in_lang]
    
    with col2:
        out_lang = st.selectbox(
            "Idioma de Salida",
            ("Inglés", "Español", "Francés", "Alemán", "Portugués", "Bengali", 
             "Coreano", "Mandarín", "Japonés")
        )
    
    output_language = language_codes[out_lang]
    
    # Accent selection
    st.markdown("### 🗣️ Configuración de Acento")
    accent_mapping = {
        "Defecto": "com",
        "Español": "com.mx",
        "Francia": "fr",
        "Alemania": "de",
        "Portugal": "pt",
        "Reino Unido": "co.uk",
        "Estados Unidos": "com",
        "Canada": "ca",
        "Australia": "com.au",
        "Irlanda": "ie",
        "Sudáfrica": "co.za"
    }
    
    english_accent = st.selectbox(
        "Selecciona el acento deseado",
        list(accent_mapping.keys())
    )
    
    tld = accent_mapping[english_accent]
    
    def text_to_speech(input_language, output_language, text, tld):
        translator = Translator()
        translation = translator.translate(text, src=input_language, dest=output_language)
        trans_text = translation.text
        tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
        try:
            my_file_name = text[0:20]
        except:
            my_file_name = "audio"
        tts.save(f"temp/{my_file_name}.mp3")
        return my_file_name, trans_text
    
    # Output options
    st.markdown("### 📋 Opciones de Salida")
    display_output_text = st.checkbox("Mostrar texto traducido", value=True)
    
    if st.button("🔄 Convertir", help="Click para procesar la traducción"):
        with st.spinner('Procesando traducción...'):
            result, output_text = text_to_speech(input_language, output_language, text, tld)
            
            st.success("¡Traducción completada!")
            
            if display_output_text:
                st.markdown("#### 📝 Texto Traducido:")
                st.write(f"{output_text}")
            
            st.markdown("#### 🔊 Audio:")
            audio_file = open(f"temp/{result}.mp3", "rb")
            audio_bytes = audio_file.read()
            st.audio(audio_bytes, format="audio/mp3", start_time=0)
    
    # Cleanup old files
    def remove_files(n):
        mp3_files = glob.glob("temp/*mp3")
        if len(mp3_files) != 0:
            now = time.time()
            n_days = n * 86400
            for f in mp3_files:
                if os.stat(f).st_mtime < now - n_days:
                    os.remove(f)
                    print("Deleted ", f)

    remove_files(7)


        
    


