import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET

st.set_page_config(page_title="Dopĺňač dát z Pohody", layout="wide")

st.title("Dopĺňanie dát z XML Pohody")

col1, col2 = st.columns(2)
with col1:
    file1 = st.file_uploader("Nahraj hlavný CSV súbor", type=["csv"])
with col2:
    file2 = st.file_uploader("Nahraj XML export z Pohody", type=["xml"])

if file1 and file2:
    # 1. Načítanie CSV
    df_main = pd.read_csv(file1, sep=';', decimal=',')

    # 2. Spracovanie XML - extrahujeme len to, čo potrebujeme
    tree = ET.parse(file2)
    root = tree.getroot()
    
    # Definícia namespace (Pohoda ich používa)
    ns = {
        'dat': 'http://www.stormware.cz/schema/version_2/data.xsd',
        'inv': 'http://www.stormware.cz/schema/version_2/invoice.xsd',
        'typ': 'http://www.stormware.cz/schema/version_2/type.xsd'
    }
    
    invoices = []
    for item in root.findall(".//dat:dataPackItem/inv:invoice", ns):
        header = item.find("inv:invoiceHeader", ns)
        number = header.findtext(".//typ:numberRequested", namespaces=ns)
        date = header.findtext("inv:date", namespaces=ns)
        
        # Kurz je v niektorých faktúrach v sekcii inv:foreignCurrency
        # Ak tam nie je (faktúra v EUR), nastavíme kurz na 1.0
        foreign_currency = item.find(".//inv:invoiceSummary/inv:foreignCurrency", ns)
        if foreign_currency is not None:
            rate = foreign_currency.findtext("typ:rate", namespaces=ns)
        else:
            rate = "1.0"
            
        invoices.append({
            "Faktura": number,
            "Pohoda_Datum": date,
            "Pohoda_Kurz": float(rate.replace(',', '.'))
        })
    
    df_pohoda = pd.DataFrame(invoices)

    # 3. Zlúčenie (Merge) len na základe stĺpca 'Faktura'
    # Predpokladám, že v CSV sa stĺpec s číslom volá 'Faktura'
    merged_df = df_main.merge(df_pohoda, on="Faktura", how="left")

    # 4. Doplnenie dát len tam, kde sú prázdne
    # Uprav si názvy stĺpcov podľa toho, ako sa volajú v tvojom CSV
    if 'Datum' in merged_df.columns:
        merged_df['Datum'] = merged_df['Datum'].fillna(merged_df['Pohoda_Datum'])
    
    if 'Kurz' in merged_df.columns:
        merged_df['Kurz'] = merged_df['Kurz'].fillna(merged_df['Pohoda_Kurz'])
    
    # Odstránenie pomocných stĺpcov z XML
    merged_df = merged_df.drop(columns=['Pohoda_Datum', 'Pohoda_Kurz'], errors='ignore')

    st.success("Dáta úspešne spracované!")
    st.write(merged_df.head())

    # Export
    csv = merged_df.to_csv(index=False, sep=';', decimal=',').encode('utf-8-sig')
    st.download_button("Stiahnuť výsledné CSV", data=csv, file_name="faktury_opravene.csv", mime="text/csv")
