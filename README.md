import streamlit as st
import sqlite3
import pandas as pd

# Konfiguracja nazwy bazy danych
DB_NAME = "produkty.db"

def init_db():
    """Inicjalizuje bazę danych i tworzy tabelę, jeśli nie istnieje."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS produkty (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nazwa TEXT NOT NULL,
            kategoria TEXT NOT NULL,
            cena REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def dodaj_produkt(nazwa, kategoria, cena):
    """Dodaje nowy produkt do bazy danych."""
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute(
            "INSERT INTO produkty (nazwa, kategoria, cena) VALUES (?, ?, ?)",
            (nazwa, kategoria, cena)
        )
        conn.commit()

def pobierz_produkty():
    """Pobiera wszystkie dane z bazy do formatu DataFrame."""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT nazwa, kategoria, cena FROM produkty", conn)
    conn.close()
    return df

# --- INTERFEJS STREAMLIT ---
st.set_page_config(page_title="Baza Produktów", page_icon="💰")
init_db()

st.title("📦 System Zarządzania Produktami")

# Formularz wprowadzania danych
with st.form("dodawanie_produktu", clear_on_submit=True):
    st.subheader("Dodaj nowy produkt")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        nazwa = st.text_input("Nazwa produktu")
    with col2:
        kategoria = st.selectbox("Kategoria", ["Elektronika", "Dom", "Ogród", "Spożywcze", "Odzież"])
    with col3:
        cena = st.number_input("Cena (PLN)", min_value=0.0, step=0.01, format="%.2f")
    
    submit_button = st.form_submit_button("Dodaj do bazy")

    if submit_button:
        if nazwa:
            dodaj_produkt(nazwa, kategoria, cena)
            st.success(f"Dodano: {nazwa} w cenie {cena:.2f} PLN")
        else:
            st.error("Proszę podać nazwę produktu.")

st.divider()

# Wyświetlanie tabeli
st.subheader("📋 Lista produktów w bazie")
dane = pobierz_produkty()

if not dane.empty:
    # Wyświetlamy tabelę z odpowiednim formatowaniem ceny
    st.dataframe(
        dane.style.format({"cena": "{:.2f} PLN"}),
        use_container_width=True,
        hide_index=True
    )
    
    # Podsumowanie
    st.write(f"**Suma produktów:** {len(dane)}")
else:
    st.info("Baza danych jest pusta.")
