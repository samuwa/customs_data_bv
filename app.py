import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(layout="wide")

st.subheader("Customs Data :boat:")
# st.write("**Importadores Pequeños**")

data = st.sidebar.file_uploader("Data")

if data:

    df = pd.read_excel(data, header=5, sheet_name=0)

    # Limpieza
    df["Código SAC"] = df["Código SAC"].astype(str)
    df["Fecha"] = pd.to_datetime(df["Fecha"]).dt.date
    cols_to_int = ['Cantidad', 'Bultos', 'U$S FOB', 'U$S CIF']
    df[cols_to_int] = df[cols_to_int].apply(lambda x: pd.to_numeric(x, errors='coerce').round().astype('Int64'))


    # Filtrar descripciones
    descs = st.sidebar.multiselect("Descripciones", df['Descripción de Mercadería'].unique(), df['Descripción de Mercadería'].unique())

    df = df[df['Descripción de Mercadería'].isin(descs)]


    # Filtro pequeños
    cantidad_min = 500000
    bultos_min = 500000
    pequenos = df[(df["Cantidad"] <= cantidad_min) | (df["Bultos"] <= bultos_min)]

    pequenos['Fecha'] = pd.to_datetime(pequenos['Fecha'])
    summary = pequenos.groupby('Importador').agg(
        Fecha_Count       = ('Fecha',  'count'),
        CIF_Sum       = ('U$S CIF',  'sum'),
        Cantidad_Sum      = ('Cantidad','sum'),
        Cantidad_Max      = ('Cantidad','max'),
        Bultos_Sum        = ('Bultos', 'sum'),
        Bultos_Max        = ('Bultos', 'max'),
        Avg_Days_Between  = ('Fecha',   lambda x: x.sort_values().diff().dt.days.mean()),
    ).reset_index().sort_values(by="CIF_Sum", ascending=False)

    st.dataframe(summary, use_container_width=True, hide_index=True)

    # View Details

    imp = st.selectbox("Ver detalles", summary["Importador"].unique())

    # filter
    sub = df[df['Importador'] == imp]

    # aggregations
    sum_cantidad = sub['Cantidad'].sum()
    sum_cif      = sub['U$S CIF'].sum()
    unique_pais  = sub.groupby('País de Origen')["Fecha"].count().reset_index().sort_values(by="Fecha", ascending=False).rename(columns={"Fecha": "# de importaciones"})
    unique_prov  = sub.groupby('Proveedor')["Fecha"].count().reset_index().sort_values(by="Fecha", ascending=False).rename(columns={"Fecha": "# de importaciones"})
    unique_desc  = sub.groupby('Descripción de Mercadería')["Fecha"].count().reset_index().sort_values(by="Fecha", ascending=False).rename(columns={"Fecha": "# de importaciones"})

    col1, col2= st.columns(2)

    col1.metric("Total Cantidad", f"{sum_cantidad:,}")
    col2.metric("Total U$S CIF", f"${sum_cif:,.2f}")


    # line plot Fecha vs U$S CIF
    fig = px.line(
        sub.sort_values('Fecha'),
        x='Fecha',
        y='U$S CIF',
        title=f'U$S CIF over time for {imp}'
    )

    col1, col2= st.columns(2)

    col1.plotly_chart(fig)
    col2.dataframe(df[df["Importador"] == imp], hide_index=True)

    col1, col2, col3 = st.columns(3)

    col1.dataframe(unique_pais, hide_index=True)
    col2.dataframe(unique_prov, hide_index=True)
    col3.dataframe(unique_desc, hide_index=True)
