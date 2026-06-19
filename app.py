import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dopĺňač dát do faktúr", layout="wide")

st.title("Dopĺňanie dát do CSV faktúr")
st.write("Nahrajte CSV súbory. Používa sa oddeľovač ';' a desatinná čiarka ','.")

# Upload súborov
col1, col2 = st.columns(2)
with col1:
    file1 = st.file_uploader("Nahraj hlavný CSV súbor", type=["csv"])
with col2:
    file2 = st.file_uploader("Nahraj export z Pohody", type=["csv"])

if file1 and file2:
    # Načítanie dát s parametrami pre slovenský/český formát CSV
    # decimal=',' zabezpečí, že čísla s čiarkou budú správne interpretované ako desatinné čísla
    df_main = pd.read_csv(file1, sep=';', decimal=',')
    df_pohoda = pd.read_csv(file2, sep=';', decimal=',')

    st.write("Ukážka dát hlavného súboru:", df_main.head())

    # Názvy stĺpcov podľa tvojho zadania
    key_col = "Faktura"
    col_datum = "Datum"
    col_kurz = "Kurz"

    if key_col in df_main.columns and key_col in df_pohoda.columns:
        # Zlúčenie súborov
        # Vyberáme len potrebné stĺpce z exportu Pohody
        df_pohoda_subset = df_pohoda[[key_col, col_datum, col_kurz]].copy()
        
        # Spojenie (merge)
        merged_df = df_main.merge(df_pohoda_subset, on=key_col, how="left", suffixes=('', '_new'))

        # Doplnenie dát: ak je pôvodná hodnota prázdna, vezmeme ju z nového stĺpca
        # (Pandas automaticky pridá príponu _new k stĺpcom z druhého súboru pri konflikte názvov)
        merged_df[col_datum] = merged_df[col_datum].fillna(merged_df[col_datum + '_new'])
        merged_df[col_kurz] = merged_df[col_kurz].fillna(merged_df[col_kurz + '_new'])

        # Odstránenie pomocných stĺpcov
        merged_df = merged_df.drop(columns=[col_datum + '_new', col_kurz + '_new'])

        st.success("Dáta boli úspešne spojené!")
        st.write("Výsledná tabuľka:", merged_df.head())

        # Download tlačidlo (pri exporte nastavíme oddeľovač na ';' a desatinnú čiarku na ',')
        csv = merged_df.to_csv(index=False, sep=';', decimal=',').encode('utf-8-sig') # utf-8-sig pomáha správne zobraziť diakritiku v Exceli
        st.download_button(
            "Stiahnuť upravené CSV", 
            data=csv, 
            file_name="faktury_doplnene.csv",
            mime="text/csv"
        )
    else:
        st.error(f"Chyba: Súbory neobsahujú spoločný stĺpec '{key_col}'")
