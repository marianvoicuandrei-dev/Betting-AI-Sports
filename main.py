import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

# --- CONFIGURARE INTERFAȚĂ ---
st.set_page_config(page_title="AI Sports Predictor PRO", layout="wide")

# --- FUNCȚII MATEMATICE (MOTORUL AI) ---
def predict_probabilities(home_xg, away_xg):
    # Generăm probabilitățile de goluri (0-5) pentru fiecare echipă
    home_probs = [poisson.pmf(i, home_xg) for i in range(6)]
    away_probs = [poisson.pmf(i, away_xg) for i in range(6)]
    
    # Matricea de rezultate
    m = np.outer(home_probs, away_probs)
    
    win = np.sum(np.tril(m, -1))
    draw = np.sum(np.diag(m))
    loss = np.sum(np.triu(m, 1))
    
    return win, draw, loss

def calculate_kelly(prob, odd, bankroll=1000):
    if odd <= 1: return 0
    b = odd - 1
    f_star = (prob * b - (1 - prob)) / b
    # Folosim Fractional Kelly (25%) pentru siguranță
    return max(0, round(f_star * bankroll * 0.25, 2))

# --- DESIGN DASHBOARD ---
st.title("⚽ AI EuroPredictor Pro")
st.sidebar.header("Setări Cont")
budget = st.sidebar.number_input("Buget Total (EUR)", value=1000)

league = st.sidebar.selectbox("Alege Liga", ["Premier League", "La Liga", "Serie A", "SuperLiga Romania"])

st.write(f"### Analiză live: {league}")

# --- DATE SIMULATE (Aici vor veni datele din API-ul tău după conectare) ---
data = {
    "Meci": ["Real Madrid vs Barcelona", "FCSB vs Rapid", "Man City vs Liverpool"],
    "Home_xG_Stat": [2.1, 1.4, 2.5],
    "Away_xG_Stat": [1.2, 1.1, 1.8],
    "Cota_Casa": [1.95, 2.30, 2.05]
}
df = pd.DataFrame(data)

# --- CALCULARE REZULTATE ---
results = []
for i, row in df.iterrows():
    p_win, p_draw, p_loss = predict_probabilities(row['Home_xG_Stat'], row['Away_xG_Stat'])
    fair_odd = 1 / p_win
    edge = (row['Cota_Casa'] / fair_odd) - 1
    stake = calculate_kelly(p_win, row['Cota_Casa'], budget)
    
    results.append({
        "Meci": row['Meci'],
        "Prob. Victorie (%)": f"{round(p_win * 100, 1)}%",
        "Cota Corecta AI": round(fair_odd, 2),
        "Cota Casei": row['Cota_Casa'],
        "Edge (%)": f"{round(edge * 100, 1)}%",
        "Miza Recomandata": f"{stake} EUR"
    })

# --- AFIȘARE TABEL FINAL ---
st.table(pd.DataFrame(results))

st.info("💡 Sfat: Pariază doar unde 'Edge' este pozitiv (scris cu verde în mintea ta) și 'Miza' este mai mare de 0.")
