import streamlit as st
from supabase import create_client, Client

# --- KONFIGURACJA POŁĄCZENIA ---
URL = "https://opnoncvsjvmzsbimtgww.supabase.co"
KEY = "sb_publishable__RETIuoreizHaYlDnRsxLw_SnjX9du9"

@st.cache_resource
def init_connection():
    return create_client(URL, KEY)

try:
    supabase = init_connection()
except Exception as e:
    st.error(f"Błąd połączenia: {e}")
    st.stop()

st.set_page_config(page_title="Zarządzanie Magazynem", layout="wide")
st.title("📦 System Zarządzania Produktami")

tab1, tab2, tab3 = st.tabs(["➕ Dodaj Produkt", "📂 Dodaj Kategorię", "📊 Podgląd Bazy"])

# --- ZAKŁADKA: KATEGORIE ---
with tab2:
    st.header("Nowa Kategoria")
    with st.form("category_form", clear_on_submit=True):
        kat_nazwa = st.text_input("Nazwa kategorii")
        kat_opis = st.text_area("Opis")
        if st.form_submit_button("Zapisz kategorię"):
            if kat_nazwa:
                try:
                    # Ujednolicone klucze: nazwa, opis
                    supabase.table("Kategorie").insert({"nazwa": kat_nazwa, "opis": kat_opis}).execute()
                    st.success(f"Dodano kategorię: {kat_nazwa}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Błąd: {e}")
            else:
                st.error("Nazwa jest wymagana!")

# --- ZAKŁADKA: PRODUKTY ---
with tab1:
    st.header("Nowy Produkt")
    try:
        categories_res = supabase.table("Kategorie").select("id, nazwa").execute()
        categories_data = categories_res.data
    except:
        categories_data = []

    if not categories_data:
        st.warning("Najpierw dodaj kategorię!")
    else:
        cat_options = {item['nazwa']: item['id'] for item in categories_data}
        
        with st.form("product_form", clear_on_submit=True):
            p_nazwa = st.text_input("Nazwa produktu")
            p_liczba = st.number_input("Ilość", min_value=0, step=1)
            p_cena = st.number_input("Cena", min_value=0.0, step=0.01, format="%.2f")
            p_kat = st.selectbox("Kategoria", options=list(cat_options.keys()))
            
            if st.form_submit_button("Dodaj produkt"):
                if p_nazwa:
                    try:
                        # Ujednolicone klucze: nazwa, liczba, cena, kategorie_id
                        payload = {
                            "nazwa": p_nazwa,
                            "liczba": p_liczba,
                            "cena": p_cena,
                            "kategorie_id": cat_options[p_kat]
                        }
                        supabase.table("Produkty").insert(payload).execute()
                        st.success(f"Dodano produkt: {p_nazwa}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Błąd: {e}")
                else:
                    st.error("Nazwa jest wymagana!")

# --- ZAKŁADKA: PODGLĄD ---
with tab3:
    st.header("Aktualny stan magazynu")
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Lista Kategorii")
        res_k = supabase.table("Kategorie").select("id, nazwa, opis").execute()
        if res_k.data:
            st.dataframe(res_k.data, use_container_width=True, hide_index=True)
            
    with c2:
        st.subheader("Lista Produktów")
        res_p = supabase.table("Produkty").select("id, nazwa, liczba, cena, kategorie_id").execute()
        if res_p.data:
            st.dataframe(res_p.data, use_container_width=True, hide_index=True)
