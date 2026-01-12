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
st.title("📦 System Zarządzania Produktami")

# --- ZAKŁADKI ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📦 Dodaj Produkt", 
    "➕ Dodaj Kategorię", 
    "📊 Podgląd Bazy", 
    "🔄 Aktualizuj Stan", 
    "🗑️ Usuń Dane"
])

# --- DODAWANIE KATEGORII ---
with tab2:
    st.header("Nowa Kategoria")
    with st.form("category_form", clear_on_submit=True):
        kat_nazwa = st.text_input("Nazwa kategorii")
        kat_opis = st.text_area("Opis")
        submit_kat = st.form_submit_button("Zapisz kategorię")

        if submit_kat:
            if kat_nazwa:
                try:
                    data = {"nazwa": kat_nazwa, "opis": kat_opis}
                    supabase.table("Kategorie").insert(data).execute()
                    st.success(f"Dodano kategorię: {kat_nazwa}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Błąd zapisu: {e}")
            else:
                st.error("Nazwa kategorii jest wymagana!")

# --- DODAWANIE PRODUKTU ---
with tab1:
    st.header("Nowy Produkt")
    try:
        categories_res = supabase.table("Kategorie").select("id, nazwa").execute()
        categories_data = categories_res.data
    except Exception as e:
        categories_data = []
    
    if not categories_data:
        st.warning("Najpierw dodaj przynajmniej jedną kategorię!")
    else:
        cat_options = {item['nazwa']: item['id'] for item in categories_data}
        
        with st.form("product_form", clear_on_submit=True):
            prod_nazwa = st.text_input("Nazwa produktu")
            prod_liczba = st.number_input("Liczba (sztuki)", min_value=0, step=1)
            prod_cena = st.number_input("Cena", min_value=0.0, step=0.01, format="%.2f")
            prod_kat_nazwa = st.selectbox("Kategoria", options=list(cat_options.keys()))
            
            submit_prod = st.form_submit_button("Dodaj produkt")
            
            if submit_prod:
                if prod_nazwa:
                    try:
                        product_data = {
                            "nazwa": prod_nazwa,
                            "liczba": prod_liczba,
                            "cena": prod_cena,
                            "kategorie_id": cat_options[prod_kat_nazwa]
                        }
                        supabase.table("Produkty").insert(product_data).execute()
                        st.success(f"Produkt '{prod_nazwa}' został dodany.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Błąd podczas dodawania produktu: {e}")
                else:
                    st.error("Nazwa produktu jest wymagana!")

# --- PODGLĄD DANYCH ---
with tab3:
    st.header("Aktualny stan bazy")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Kategorie")
        kat_view = supabase.table("Kategorie").select("id, nazwa, opis").execute()
        if kat_view.data:
            st.dataframe(kat_view.data, use_container_width=True, hide_index=True)
        else:
            st.info("Brak kategorii.")
    
    with col2:
        st.subheader("Produkty")
        prod_view = supabase.table("Produkty").select("id, nazwa, liczba, cena, kategorie_id").execute()
        if prod_view.data:
            st.dataframe(prod_view.data, use_container_width=True, hide_index=True)
        else:
            st.info("Brak produktów.")

# --- AKTUALIZACJA ILOŚCI ---
with tab4:
    st.header("Aktualizuj ilość produktu")
    try:
        p_update_res = supabase.table("Produkty").select("id, nazwa, liczba").execute()
        p_update_list = p_update_res.data
    except:
        p_update_list = []

    if p_update_list:
        p_update_options = {item['nazwa']: item for item in p_update_list}
        selected_p_name = st.selectbox("Wybierz produkt do zmiany ilości", options=list(p_update_options.keys()))
        
        selected_item = p_update_options[selected_p_name]
        st.info(f"Obecna ilość w bazie: **{selected_item['liczba']}**")
        
        nowa_ilosc = st.number_input("Nowa liczba (sztuki)", min_value=0, value=int(selected_item['liczba']), step=1)
        
        if st.button("Zatwierdź zmianę", type="primary"):
            try:
                supabase.table("Produkty").update({"liczba": nowa_ilosc}).eq("id", selected_item['id']).execute()
                st.success(f"Zaktualizowano ilość dla: {selected_p_name}")
                st.rerun()
            except Exception as e:
                st.error(f"Błąd podczas aktualizacji: {e}")
    else:
        st.info("Brak produktów do aktualizacji.")

# --- USUWANIE DANYCH ---
with tab5:
    st.header("Usuwanie elementów z bazy")
    col_del1, col_del2 = st.columns(2)
    
    with col_del1:
        st.subheader("Usuń Produkt")
        try:
            p_res = supabase.table("Produkty").select("id, nazwa").execute()
            products_list = p_res.data
        except:
            products_list = []
            
        if products_list:
            p_options = {item['nazwa']: item['id'] for item in products_list}
            p_to_delete = st.selectbox("Wybierz produkt do usunięcia", options=list(p_options.keys()))
            
            if st.button("Usuń produkt", type="primary"):
                try:
                    supabase.table("Produkty").delete().eq("id", p_options[p_to_delete]).execute()
                    st.success(f"Usunięto produkt: {p_to_delete}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Błąd: {e}")
        else:
            st.info("Brak produktów do usunięcia.")

    with col_del2:
        st.subheader("Usuń Kategorię")
        try:
            k_res = supabase.table("Kategorie").select("id, nazwa").execute()
            k_list = k_res.data
        except:
            k_list = []
            
        if k_list:
            k_options = {item['nazwa']: item['id'] for item in k_list}
            k_to_delete = st.selectbox("Wybierz kategorię do usunięcia", options=list(k_options.keys()))
            
            st.warning("Uwaga: Usunięcie kategorii może się nie udać, jeśli są do niej przypisane produkty.")
            if st.button("Usuń kategorię", type="secondary"):
                try:
                    supabase.table("Kategorie").delete().eq("id", k_options[k_to_delete]).execute()
                    st.success(f"Usunięto kategorię: {k_to_delete}")
                    st.rerun()
                except Exception as e:
                    st.error("Nie można usunąć kategorii (prawdopodobnie zawiera produkty).")
        else:
            st.info("Brak kategorii do usunięcia.")
