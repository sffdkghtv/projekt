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
    st.error(f"Błąd połączenia z Supabase: {e}")
    st.stop()

st.set_page_config(page_title="Zarządzanie Magazynem", layout="wide")

# --- MENU BOCZNE (SIDEBAR) ---
with st.sidebar:
    st.title("📂 Menu Główne")
    try:
        # Szybka statystyka w menu bocznym
        res_count = supabase.table("Produkty").select("id", count="exact").execute()
        st.metric("Liczba produktów", res_count.count if res_count.count else 0)
    except:
        pass
        
    wybor_menu = st.radio(
        "Wybierz widok:",
        ["🛠️ Panel Zarządzania", "📊 Podgląd Bazy Danych"]
    )

# --- WIDOK: PANEL ZARZĄDZANIA ---
if wybor_menu == "🛠️ Panel Zarządzania":
    st.title("🛠️ Zarządzanie Magazynem")
    
    tab1, tab2, tab4, tab5 = st.tabs([
        "📦 Dodaj Produkt", 
        "➕ Dodaj Kategorię", 
        "🔄 Aktualizuj Stan", 
        "🗑️ Usuń Dane"
    ])

    # --- DODAWANIE KATEGORII ---
    with tab2:
        st.header("Nowa Kategoria")
        with st.form("category_form", clear_on_submit=True):
            kat_nazwa = st.text_input("Nazwa kategorii")
            kat_opis = st.text_area("Opis")
            if st.form_submit_button("Zapisz kategorię"):
                if kat_nazwa:
                    try:
                        supabase.table("Kategorie").insert({"nazwa": kat_nazwa, "opis": kat_opis}).execute()
                        st.success(f"Dodano kategorię: {kat_nazwa}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Błąd: {e}")
                else:
                    st.error("Nazwa jest wymagana!")

    # --- DODAWANIE PRODUKTU ---
    with tab1:
        st.header("Nowy Produkt")
        try:
            cat_res = supabase.table("Kategorie").select("id, nazwa").execute()
            categories_data = cat_res.data
        except:
            categories_data = []
        
        if not categories_data:
            st.warning("Dodaj najpierw kategorię!")
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
                            supabase.table("Produkty").insert({
                                "nazwa": p_nazwa, "liczba": p_liczba, 
                                "cena": p_cena, "kategorie_id": cat_options[p_kat]
                            }).execute()
                            st.success(f"Dodano: {p_nazwa}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Błąd: {e}")

    # --- AKTUALIZACJA ILOŚCI ---
    with tab4:
        st.header("🔄 Zmień ilość na stanie")
        try:
            p_upd_res = supabase.table("Produkty").select("id, nazwa, liczba").execute()
            p_list = p_upd_res.data
        except:
            p_list = []

        if p_list:
            p_map = {item['nazwa']: item for item in p_list}
            sel_p = st.selectbox("Produkt", options=list(p_map.keys()), key="upd_sel")
            curr_item = p_map[sel_p]
            new_val = st.number_input("Nowa ilość", min_value=0, value=int(curr_item['liczba']))
            if st.button("Zaktualizuj", type="primary"):
                supabase.table("Produkty").update({"liczba": new_val}).eq("id", curr_item['id']).execute()
                st.success("Zmieniono stan magazynowy!")
                st.rerun()
        else:
            st.info("Brak produktów.")

    # --- USUWANIE ---
    with tab5:
        st.header("🗑️ Usuwanie")
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Usuń Produkt")
            p_del_res = supabase.table("Produkty").select("id, nazwa").execute()
            if p_del_res.data:
                p_del_map = {i['nazwa']: i['id'] for i in p_del_res.data}
                to_del = st.selectbox("Wybierz produkt", options=list(p_del_map.keys()))
                if st.button("Usuń", type="primary"):
                    supabase.table("Produkty").delete().eq("id", p_del_map[to_del]).execute()
                    st.rerun()

# --- WIDOK: PODGLĄD BAZY ---
elif wybor_menu == "📊 Podgląd Bazy Danych":
    st.title("📊 Aktualny Stan Bazy")
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("Kategorie")
        res_k = supabase.table("Kategorie").select("*").execute()
        st.dataframe(res_k.data, use_container_width=True, hide_index=True)
        
    with col_b:
        st.subheader("Produkty")
        res_p = supabase.table("Produkty").select("*").execute()
        st.dataframe(res_p.data, use_container_width=True, hide_index=True)
