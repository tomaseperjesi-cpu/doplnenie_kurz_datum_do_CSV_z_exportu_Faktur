import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dopĺňač dát do faktúr", layout="wide")

st.title("Dopĺňanie dát do CSV faktúr")
st.write("Nahrajte CSV so základnými údajmi a CSV export z Pohody.")

# Upload súborov
col1, col2 = st.columns(2)
with col1:
    file1 = st.file_uploader("Nahraj hlavný CSV súbor", type=["csv"])
with col2:
    file2 = st.file_uploader("Nahraj export z Pohody", type=["csv"])

if file1 and file2:
    # Načítanie dát (uprav 'sep', ak súbor nepoužíva čiarku)
    df_main = pd.read_csv(file1)
    df_pohoda = pd.read_csv(file2)

    st.write("Ukážka dát pred spojením:", df_main.head())

    # Predpokladáme, že stĺpec s číslom faktúry sa volá 'CisloFaktury'
    # Ak sa volá inak, zmeň názov v oboch prípadoch
    key_col = "CisloFaktury" 

    if key_col in df_main.columns and key_col in df_pohoda.columns:
        # Zlúčenie súborov (merge)
        # Použijeme ľavé spojenie, aby sme zachovali všetky riadky z hlavného súboru
        merged_df = df_main.merge(
            df_pohoda[[key_col, "DatumVystavenia", "Kurz"]], 
            on=key_col, 
            how="left"
        )

        # Doplnenie chýbajúcich dát
        # Ak boli v pôvodnom súbore prázdne polia, prepíšeme ich novými údajmi
        merged_df['DatumVystavenia'] = merged_df['DatumVystavenia_y'].fillna(merged_df['DatumVystavenia_x'])
        merged_df['Kurz'] = merged_df['Kurz_y'].fillna(merged_df['Kurz_x'])

        st.success("Dáta boli úspešne spojené!")
        st.write("Výsledná tabuľka:", merged_df.head())

        # Download tlačidlo
        csv = merged_df.to_csv(index=False).encode('utf-8')
        st.download_button("Stiahnuť upravené CSV", data=csv, file_name="faktury_doplnene.csv")
    else:
        st.error(f"Chyba: Súbory neobsahujú spoločný stĺpec '{key_col}'")
