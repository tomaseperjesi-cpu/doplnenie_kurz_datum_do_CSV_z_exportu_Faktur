import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET

st.set_page_config(page_title="Dopĺňač dát z XML Pohody", layout="wide")

st.title("Dopĺňanie dát z XML Pohody")
st.write("Nahrajte CSV (hlavný súbor) a XML (export z Pohody).")

# Upload súborov
col1, col2 = st.columns(2)
with col1:
    file1 = st.file_uploader("Nahraj hlavný CSV súbor", type=["csv"])
with col2:
    file2 = st.file_uploader("Nahraj XML export z Pohody", type=["xml"])

if file1 and file2:
    # 1. Načítanie CSV
    df_main = pd.read_csv(file1, sep=';', decimal=',')

    # 2. Načítanie a spracovanie XML
    # Tento blok je potrebné prispôsobiť presnej štruktúre tvojho XML
    tree = ET.parse(file2)
    root = tree.getroot()
    
    data = []
    # Tu musíme iterovať cez faktúry v XML. 
    # V Pohode XML exportoch bývajú faktúry v rôznych menných priestoroch.
    # Toto je všeobecný prístup, možno bude treba upraviť cestu (find/findall)
    for invoice in root.findall(".//{http://www.stormware.cz/schema/version_2/invoice.xsd}invoice"):
        # Nájdenie čísla faktúry (napr. v invoiceHeader/number/numberRequested)
        number_el = invoice.find(".//{http://www.stormware.cz/schema/version_2/invoice.xsd}numberRequested")
        # Nájdenie dátumu a kurzu (uprav podľa reálnych tagov v tvojom XML)
        date_el = invoice.find(".//{http://www.stormware.cz/schema/version_2/invoice.xsd}date")
        rate_el = invoice.find(".//{http://www.stormware.cz/schema/version_2/invoice.xsd}rate")
        
        data.append({
            "Faktura": number_el.text if number_el is not None else None,
            "Datum": date_el.text if date_el is not None else None,
            "Kurz": float(rate_el.text.replace(',', '.')) if rate_el is not None else None
        })
    
    df_pohoda = pd.DataFrame(data)

    # 3. Spojenie dát
    key_col = "Faktura"
    merged_df = df_main.merge(df_pohoda, on=key_col, how="left", suffixes=('', '_new'))

    # Doplnenie dát
    merged_df['Datum'] = merged_df['Datum'].fillna(merged_df['Datum_new'])
    merged_df['Kurz'] = merged_df['Kurz'].fillna(merged_df['Kurz_new'])
    
    merged_df = merged_df.drop(columns=['Datum_new', 'Kurz_new'])

    st.success("Dáta boli úspešne spojené!")
    st.write("Výsledná tabuľka:", merged_df.head())

    # Export
    csv = merged_df.to_csv(index=False, sep=';', decimal=',').encode('utf-8-sig')
    st.download_button("Stiahnuť upravené CSV", data=csv, file_name="faktury_doplnene.csv", mime="text/csv")
