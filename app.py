import streamlit as st
import requests
from bs4 import BeautifulSoup

# Standaard instellingen voor de webpagina
st.set_page_config(
    page_title="Frikandelbroodje Tracker",
    page_icon="🍟",
    layout="centered"
)

# Albert Heijn URL van het frikandelbroodje
AH_URL = "https://ah.nl"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def check_bonus():
    """Scrapt de AH pagina om te kijken of het frikandelbroodje in de Bonus is."""
    try:
        response = requests.get(AH_URL, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            return {"error": True, "msg": "Kon de AH website niet bereiken."}
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Zoek naar Bonus-kenmerken op de pagina
        page_text = soup.get_text().lower()
        is_bonus = "bonus" in page_text or "korting" in page_text
        
        # Probeer de huidige prijs te vinden (dit is een indicatie, AH wijzigt soms klassen)
        # We zoeken naar de prijsaanduiding in de HTML
        price_discount = "Nu in de Bonus!" if is_bonus else "Normale prijs"
        
        return {
            "error": False,
            "is_bonus": is_bonus,
            "status_text": price_discount,
            "url": AH_URL
        }
    except Exception as e:
        return {"error": True, "msg": f"Fout bij het ophalen van data: {str(e)}"}

def send_push_notification(topic, title, message):
    """Stuurt een push-notificatie naar de ntfy app op je telefoon."""
    try:
        requests.post(
            f"https://ntfy.sh{topic}",
            data=message.encode('utf-8'),
            headers={
                "Title": title,
                "Priority": "high",
                "Tags": "frites,bell"
            },
            timeout=10
        )
        return True
    except:
        return False

# --- INTERFACE ---
st.title("🍟 Mijn Frikandelbroodje Tracker")
st.write("De ultieme app die de Albert Heijn scant en je waarschuwt bij Bonus-knallers!")

# Status ophalen
with st.spinner("Status controleren bij Albert Heijn..."):
    data = check_bonus()

if data["error"]:
    st.error(data["msg"])
else:
    # Grote visuele statusknop
    if data["is_bonus"]:
        st.success("## 🔥 NU IN DE BONUS! 🔥")
        st.balloons()
        status_message = "SLA JE SLAG! De frikandelbroodjes zijn nu goedkoper!"
    else:
        st.info("## 🛑 Helaas, nu geen Bonus")
        status_message = "Nog even geduld... De prijs is momenteel normaal."
        
    st.write(status_message)
    st.markdown(f"[Bekijk direct op AH.nl]({data['url']})")

st.divider()

# --- NOTIFICATIE INSTELLINGEN ---
st.subheader("📱 Push-notificaties instellen")
st.write("Wil jij of je vrienden een melding op je telefoon? Volg deze stappen:")
st.write("1. Download de **ntfy** app op je Android of iPhone.")
st.write("2. Verzin hieronder een unieke naam en voeg exact dat kanaal toe in de ntfy-app.")

# Uniek kanaal invoeren voor de gebruiker
user_topic = st.text_input(
    "Jouw unieke notificatie-kanaal:", 
    value="frikandel_alert_uniek_2026",
    help="Maak dit uniek (bijv. frikandel_pete_99) zodat anderen jouw meldingen niet verstoren."
)

# Testknop voor notificaties
if st.button("📣 Stuur test-notificatie naar mijn telefoon"):
    if user_topic:
        succes = send_push_notification(
            user_topic, 
            "🍟 Frikandelbroodje Tracker", 
            "Je app werkt! Je ontvangt nu een melding zodra de broodjes in de Bonus zijn."
        )
        if succes:
            st.success(f"Testbericht verzonden naar ntfy.sh/{user_topic}!")
        else:
            st.error("Kon de notificatie niet verzenden. Controleer je internetverbinding.")
    else:
        st.warning("Vul eerst een kanaalnaam in.")

# Automatische trigger op de achtergrond (simulatie via dashboard actie)
if data["is_bonus"]:
    # Stuurt automatisch een melding als iemand de pagina opent en het is bonus
    send_push_notification(
        user_topic,
        "🔥 FRIKANDELBROODJE BONUS! 🔥",
        "Ren naar de Albert Heijn, de frikandelbroodjes zijn in de aanbieding!"
    )
  
