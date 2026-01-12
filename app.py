import streamlit as st
import os
import json
from groq import Groq
from dotenv import load_dotenv

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Cinemagraph Prompt Gen",
    page_icon="🎬",
    layout="wide"
)

# --- 2. SETUP API KEY (VERSI ANTI-CRASH) ---
api_key = None

# Coba ambil dari Streamlit Cloud Secrets dulu
try:
    if "GROQ_API_KEY" in st.secrets:
        api_key = st.secrets["GROQ_API_KEY"]
except FileNotFoundError:
    pass # Lanjut ke cara berikutnya jika secrets tidak ditemukan

# Jika belum ketemu, coba ambil dari file .env (Lokal)
if not api_key:
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")

# Cek akhir
if not api_key:
    st.warning("⚠️ API Key belum ditemukan. Jika di Cloud, harap set 'Secrets'. Jika di Lokal, cek .env")

# --- 4. FUNGSI GENERATE (GAYA VISUAL YANG KUAT) ---
def generate_prompts(topic, style):
    if not api_key:
        st.error("❌ API Key Groq belum disetting di file .env!")
        return None
        
    client = Groq(api_key=api_key)
    
    # Definisi Keyword Gaya yang Wajib Muncul
    style_keywords = ""
    if style == "Realistis (Cinematic)":
        style_keywords = "Photorealistic, 8k, Unreal Engine 5, Cinematic Lighting, Macro Photography, Highly Detailed Texture."
    elif style == "Ghibli Anime":
        style_keywords = "Studio Ghibli Art Style, Hand-drawn 2D Animation, Hayao Miyazaki aesthetic, Vibrant Colors, Painted Backgrounds."
    elif style == "3D Pixar/Disney":
        style_keywords = "Pixar 3D Animation Style, Disney/Pixar Render, Soft Lighting, Cute Character Design, High Fidelity 3D."
    elif style == "Lofi Hip Hop Art":
        style_keywords = "Lofi Hip Hop Aesthetic, Anime Chill Vibes, Vector Art, Flat Design, Pastel Color Palette, Nostalgic."
    elif style == "Cyberpunk/Neon":
        style_keywords = "Cyberpunk Aesthetic, Neon Lights, Dark Atmosphere, Blade Runner Vibe, Futuristic City, High Contrast."
    elif style == "Watercolor (Cat Air)":
        style_keywords = "Watercolor Painting Style, Soft Edges, Artistic Brush Strokes, Dreamy Atmosphere, Paper Texture."
    
    # Prompt System
    system_prompt = f"""
    You are a Technical Director for Cinemagraphs.
    
    USER SELECTED STYLE: {style}
    STYLE KEYWORDS TO USE: "{style_keywords}"
    
    CRITICAL RULES:
    1. CAMERA: STRICTLY STATIC. Locked Tripod. No Zoom.
    2. SUBJECTS: Allowed, but must be described as "MOTIONLESS" or "FROZEN".
    
    Output JSON ONLY with keys:
    
    "imagen_prompt":
    - Start or End with the STYLE KEYWORDS provided above.
    - Describe the scene based on the topic "{topic}".
    - Focus on how the light interacts with the style (e.g., "Neon reflection" for Cyberpunk, "Soft sunlight" for Ghibli).
    
    "veo_prompt":
    - Start with: "STRICTLY STATIC CAMERA. {style.upper()} STYLE."
    - Describe ONE subtle motion (e.g., rain, smoke).
    - Explicitly state: "The [subject] remains completely frozen/motionless."
    - End with: "Maintain fixed focal length. Background remains frozen."
    """
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Topic: {topic}. Ensure the style '{style}' is clearly described."}
            ],
            temperature=0.6,
            response_format={"type": "json_object"}
        )
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        st.error(f"Error: {e}")
        return None

# --- 5. TAMPILAN WEBSITE (UI) ---
st.title("🎬 Cinemagraph Prompt Factory")
st.markdown("Generator prompt video looping dengan **Visual Style Enforcement**.")

# --- SIDEBAR (INPUT) ---
with st.sidebar:
    st.header("⚙️ Konfigurasi")
    
    # Dropdown Gaya Visual
    style_option = st.selectbox(
        "Pilih Gaya Visual:",
        (
            "Realistis (Cinematic)", 
            "Ghibli Anime", 
            "3D Pixar/Disney", 
            "Lofi Hip Hop Art",
            "Cyberpunk/Neon",
            "Watercolor (Cat Air)"
        )
    )
    
    topic = st.text_area(
        "Ide Topik:", 
        height=150, 
        placeholder="Contoh: Kucing oren tidur di atas pagar saat sore hari."
    )
    
    generate_btn = st.button("✨ Generate Prompt", type="primary", use_container_width=True)
    
    st.divider()
    st.info(f"💡 AI akan dipaksa menggunakan keyword gaya: **{style_option}**")

# --- LOGIKA UTAMA (OUTPUT) ---
if generate_btn and topic:
    with st.spinner(f"🎨 Meracik visual gaya {style_option}..."):
        result = generate_prompts(topic, style_option)
    
    if result:
        st.success(f"✅ Prompt Siap! Gaya visual **{style_option}** sudah ditanamkan.")
        
        # Layout 2 Kolom
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📸 Prompt Gambar")
            st.caption("Lihat keyword gaya di sini:")
            st.code(result.get("imagen_prompt"), language="text")
            
        with col2:
            st.subheader("🎥 Prompt Veo")
            st.caption("Instruksi gerak sesuai gaya:")
            st.code(result.get("veo_prompt"), language="text")
            
        # Download button JSON
        st.divider()
        json_str = json.dumps(result, indent=2)
        st.download_button(
            label="💾 Simpan Prompt (JSON)",
            data=json_str,
            file_name=f"prompt_{style_option.split()[0].lower()}.json",
            mime="application/json"
        )

elif generate_btn and not topic:
    st.warning("⚠️ Harap masukkan topik video terlebih dahulu!")


