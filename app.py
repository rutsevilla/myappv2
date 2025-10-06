# pip install streamlit plotly pandas numpy streamlit-option-menu unidecode
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from streamlit_option_menu import option_menu
from unidecode import unidecode
import os, base64, mimetypes
from  funciones import *
import plotly.io as pio



# ================== CONFIGURACIÓN ==================
st.set_page_config(
    page_title="Encuestas de Opinión • Costa Rica",
    page_icon="TDP",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Paleta (ajusta aquí tus colores)
PRIMARY      = "#15A1E2"   # Azul corporativo
PRIMARY_DARK = "#0F6F9D"
BG_GRAD_A    = "#175CA1"   # Degradado fondo - inicio
BG_GRAD_B    = "#07A9E0"   # Degradado fondo - fin
HEADER_A     = "#2E498A"   # Degradado header - inicio
HEADER_B     = "#2E498A"   # Degradado header - fin
CARD_BG      = "rgba(255,255,255,0.10)"  # fondo semitransparente para .box
TEXT_SOFT    = "#EAF6FF"

LOGO_PATH = "./circle-white.svg"   # ← tu logo
CSV_PATH  = "./encuestas_cr.csv"  # ← tu CSV

# Utilidad: imagen a DataURI (para <img src="..."> dentro de HTML)
logo_data_uri = img_to_data_uri(LOGO_PATH)

# --- (A) Login gate: si no hay sesión, no se muestra el tablero ---
# Usa tu logo_data_uri si quieres que aparezca en la tarjeta de login
if not login(logo_data_uri, "Encuestas de Opinión - Costa Rica"):
    st.stop()

# ================== ESTILOS (UN SOLO BLOQUE) ==================
# ================== ESTILOS (UN SOLO BLOQUE) ==================
st.markdown(f"""
<style>
/* 1) Cargar la fuente local */
@font-face {{
  font-family: 'PoppinsLocal';
  src: url('static/Poppins-Regular.woff2') format('woff2'),
       url('static/Poppins-Regular.ttf') format('truetype');
  font-weight: 400;
  font-style: normal;
  font-display: swap;
}}
/* 2) Forzar tipografía global con la local primero */
[data-testid="stAppViewContainer"] * {{
  font-family: 'PoppinsLocal','Poppins',sans-serif !important;
}}

/* ===== Fondo y contenedor principal ===== */
[data-testid="stAppViewContainer"] {{
  background: linear-gradient(90deg, {BG_GRAD_A}, {BG_GRAD_B} 140%);
  background-attachment: fixed;
}}
[data-testid="stHeader"] {{
  background: transparent;
  box-shadow: none;
}}

/* ===== Cabecera (logo + título) ===== */
.header-row {{
  display: flex;
  align-items: center;
  gap: 12px;
}}
.header-row h1 {{
  margin: 0;
  font-size: 2rem;
  font-weight: 400;   /* sin negrita extrema */
  color: white;
}}
.header-row img {{
  height: 40px;
  width: auto;
}}

/* ===== Título estilizado tipo control ===== */
:root {{
  --ctrl-h: 44px;
  --ctrl-bg: rgba(255,255,255,0.10);
  --ctrl-br: 12px;
  --ctrl-bd: 1px solid rgba(255,255,255,0.18);
  --ctrl-fg: #EAF4FA;
}}
.box-title{{
  height: var(--ctrl-h);
  background: var(--ctrl-bg);
  border-radius: var(--ctrl-br);
  border: var(--ctrl-bd);
  color: var(--ctrl-fg);
  display: flex;
  align-items: center;
  padding: 0 14px;
  font-weight: 400;
  line-height: 1;
}}

/* ===== Selectbox (Periodo) ===== */
.stSelectbox > div {{
  height: var(--ctrl-h) !important;
  background: var(--ctrl-bg);
  border-radius: var(--ctrl-br);
  border: var(--ctrl-bd);
  padding: 0 10px !important;
  display: flex;
  align-items: center;
}}
[data-testid="stSelectbox"] > div {{
  background-color: rgba(255,255,255,0.1);
  border-radius: 10px;
  border: 1px solid rgba(255,255,255,0.2);
  color: white;
}}
.stSelectbox [data-baseweb="select"] {{ height: 100% !important; }}
.stSelectbox [data-baseweb="select"] > div {{
  min-height: calc(var(--ctrl-h) - 2px) !important;
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  color: var(--ctrl-fg) !important;
}}
.stSelectbox [data-baseweb="select"] input,
.stSelectbox [data-baseweb="select"] div {{ color: var(--ctrl-fg) !important; }}
.stSelectbox svg{{ width:18px; height:18px; }}

/* ===== Ajustes generales ===== */
.block-container label:empty {{ margin:0; padding:0; }}
.main .block-container {{ padding-top: 1.2rem; }}
footer {{ visibility: hidden; }}
section[data-testid="stSidebar"] {{ display:none !important; }}
header[data-testid="stHeader"] {{ display:none !important; }}
MainMenu {{ visibility: hidden; }}
main blockquote, .block-container {{ padding-top: 0.6rem; padding-bottom: 0.6rem; }}
html, body, [data-testid="stAppViewContainer"] {{ height: 100%; overflow: hidden; }}
</style>
""", unsafe_allow_html=True)


# ================== CARGA ==================
df = cargar_csv(CSV_PATH)

# Periodos
periodos = sorted(df["Periodo"].dropna().unique())
labels_por_periodo = (df.drop_duplicates("Periodo")[["Periodo","Fecha"]]
                        .set_index("Periodo")["Fecha"].to_dict())


# ================== CABECERA ==================
st.markdown(
    f"""
    <div class="header-box">
      <div class="header-row">
        <img src="{logo_data_uri}" alt="TDP Logo" />
        <h1>Costa Rica - Encuestas de Opinión</h1>
      </div>
    </div>
    """,
    unsafe_allow_html=True
)
    
col1, col2 = st.columns([3,5])
with col1:
    with st.container():
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown('<div class="box-title">Selector de Encuesta</div>', unsafe_allow_html=True)

        with c2:
            idx_def = len(periodos)-1 if len(periodos) > 0 else 0
            periodo_sel = st.selectbox(
            label="",
            options=periodos,
            index=idx_def,
            format_func=lambda d: labels_por_periodo.get(d, pd.to_datetime(d).strftime("%b-%Y")),
            key="selector_encuestas",
            label_visibility="collapsed",   # ← importante
        )
        st.markdown('</div>', unsafe_allow_html=True)

        # Filtrar datos al periodo elegido
        df_per = filtrar_periodo(df, periodo_sel)
            
        with st.container(border=True):        

            st.markdown('##### Características demográficas de la muestra')

            c1, c2, c3 = st.columns([1,1,1])
            # --- Género ---
            with c1:
                st.caption("Género")
                df_gen = df_per[df_per["seccion_norm"] == "genero"].sort_values("Item")
                if not df_gen.empty:
                    fig_g = px.pie(
                        df_gen, names="Item", values="Valor",
                        color_discrete_sequence=[PRIMARY, "#8FBAD3", "#9DBFD3"]
                    )
                    fig_g.update_layout(
                        height=200, showlegend=False, margin=dict(l=0, r=0, t=0, b=0),
                        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
                    )
                    st.plotly_chart(fig_g, use_container_width=True)
                else:
                    st.info("Sin datos de Género para este período.")

            # --- Edad ---
            with c2:
                st.caption("Edad")
                df_edad = df_per[df_per["seccion_norm"] == "edad"]
                if not df_edad.empty:
                    fig_ed = px.pie(
                        df_edad, names="Item", values="Valor",
                        color_discrete_sequence=["#7CC4E8", PRIMARY_DARK, "#79A6C7", "#B5D6EA"]
                    )
                    fig_ed.update_layout(
                        height=200, showlegend=False, margin=dict(l=0, r=0, t=0, b=0),
                        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
                    )
                    st.plotly_chart(fig_ed, use_container_width=True)
                else:
                    st.info("Sin datos de Edad para este período.")

            # --- Educación (robusto a typos en CSV) ---
            with c3:
                st.caption("Nivel de educación")
                edu_norms = {"nivel de educacion", "nivel de eduacion", "nivel de eduación"}
                df_edu = df_per[df_per["seccion_norm"].isin({limpiar_txt(s) for s in edu_norms})]
                if not df_edu.empty:
                    fig_e = px.pie(
                        df_edu, names="Item", values="Valor",
                        color_discrete_sequence=["#4FC3F7", "#1E88E5", "#90CAF9"]
                    )
                    fig_e.update_layout(
                        height=200, showlegend=False, margin=dict(l=0, r=0, t=0, b=0),
                        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
                    )
                    st.plotly_chart(fig_e, use_container_width=True)
                else:
                    st.info("Sin datos de Educación para este período.")

with col2:
    seccion_val = pick_valoracion_sections(df)
    df_per = filtrar_periodo(df, periodo_sel)

    with st.container(border=True):
        st.markdown("##### Valoración de la gestión del gobierno/presidente")
        # --------- Gráfico 'Resultados' (periodo seleccionado) ---------
        if seccion_val is not None:
            df_val_per = df_per[df_per["Seccion"] == seccion_val].copy()

            if df_val_per.empty:
                fig_resultados = px.bar(pd.DataFrame({"Respuesta": [], "Porcentaje": []}), x="Porcentaje", y="Respuesta")
            else:
                # Normalizador (usa tu helper si existe)
                try:
                    normalizador = limpiar_txt
                except NameError:
                    normalizador = lambda s: str(s).strip().lower()

                df_val_per["item_norm"] = df_val_per["Item"].map(lambda s: normalizador(s) if pd.notna(s) else None)

                # Mapear a 3 grupos (acepta singular/plural)
                mapa = {
                    "positivo": "Positivos", "positiva": "Positivos", "positivos": "Positivos", "positivas": "Positivos",
                    "neutral": "Neutros",   "neutra": "Neutros",     "neutros": "Neutros",       "neutras": "Neutros",
                    "negativo": "Negativos","negativa": "Negativos","negativos": "Negativos","negativas": "Negativos",
                }
                df_val_per["grupo"] = df_val_per["item_norm"].map(mapa)

                res = (df_val_per.dropna(subset=["grupo"])
                                .groupby("grupo", as_index=False)["Valor"].sum())

                # Asegura las 3 barras y el orden
                res = (res.set_index("grupo")
                        .reindex(["Positivos", "Neutros", "Negativos"])
                        .fillna(0)
                        .reset_index()
                        .rename(columns={"grupo": "Respuesta", "Valor": "Porcentaje"}))

                # Por si vienen como string
                res["Porcentaje"] = pd.to_numeric(res["Porcentaje"], errors="coerce").fillna(0)

                fig_resultados = px.bar(
                    res, x="Porcentaje", y="Respuesta", orientation="h",
                    color="Respuesta",
                    color_discrete_map={"Positivos": PRIMARY, "Neutros": "#8FBAD3", "Negativos": "#F07B7B"},
                    text="Porcentaje"
                )
                fig_resultados.update_traces(texttemplate="%{x:.1f}%", textposition="outside")
                fig_resultados.update_layout(
                    height=275, showlegend=False, margin=dict(l=0, r=0, t=0, b=0),
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", xaxis_title=None, yaxis_title=None
                )
                fig_resultados.update_xaxes(ticksuffix="%")
        else:
            fig_resultados = px.bar(pd.DataFrame({"Respuesta": [], "Porcentaje": []}), x="Porcentaje", y="Respuesta")
        # --------- Gráfico 'Evolución' (toda la serie) ---------
        if seccion_val is not None:
            df_val = df[df["Seccion"] == seccion_val].copy()
            df_val["item_norm"] = df_val["Item"].map(limpiar_txt)

            # Mapeo robusto a 3 series (acepta singular/plural)
            mapa = {
                "positiva": "positiva",
                "positivos": "positiva",
                "neutra": "neutral",
                "neutros": "neutral",
                "negativa": "negativa",
                "negativos": "negativa",
            }
            df_val["tipo"] = df_val["item_norm"].map(mapa)

            df_val = df_val.dropna(subset=["tipo"]).sort_values("Periodo")
            df_val["Periodo_str"] = df_val["Periodo"].dt.strftime("%Y-%m")

            fig_evol = px.line(
                df_val,
                x="Periodo_str",
                y="Valor",
                color="tipo",
                category_orders={"tipo": ["positiva", "neutral", "negativa"]},
                color_discrete_map={"positiva": PRIMARY, "neutral": "#8FBAD3", "negativa": "#F07B7B"},
            )
            fig_evol.update_layout(
                height=275,
                margin=dict(l=0, r=0, t=8, b=0),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)", xaxis_title=None, yaxis_title=None, legend_title_text=None
            )
        else:
            fig_evol = px.line(pd.DataFrame({"Periodo_str": [], "Valor": [], "tipo": []}))

        # Render columnas
        colA, colB = st.columns([1.2, 1.8])
        with colA:
            st.markdown('Resultados')
            st.plotly_chart(fig_resultados, use_container_width=True)

        with colB:
            st.markdown('Evolución de los reultados')
            st.plotly_chart(fig_evol, use_container_width=True)


col1, col2 = st.columns([3, 5])


# ---------- FILTROS ----------
df_per = filtrar_periodo(df, periodo_sel)

# Simpatía (periodo y serie)
df_sim_per  = df_per[df_per["seccion_norm"] == "simpatia electoral"].copy()
df_sim_all  = df[df["seccion_norm"] == "simpatia electoral"].copy()
df_sim_all = df_sim_all.sort_values("Periodo")
df_sim_all["Periodo_str"] = df_sim_all["Periodo"].dt.strftime("%Y-%m")
# Confianza (periodo y serie) -> usar startswith porque el nombre es largo
mask_conf_per  = df_per["seccion_norm"].str.startswith("nivel de confianza", na=False)
mask_conf_all  = df["seccion_norm"].str.startswith("nivel de confianza", na=False)
df_conf_per = df_per[mask_conf_per].copy()
df_conf_all = df[mask_conf_all].copy()
df_conf_all = df_conf_all.sort_values("Periodo")
df_conf_all["Periodo_str"] = df_conf_all["Periodo"].dt.strftime("%Y-%m")

# ---------- FILA 1: dos pies del periodo seleccionado ----------
with col1:
    with st.container(border=True):
        st.markdown("##### Simpatía Política y Confianza en el Gobierno")
        c1, c2 = st.columns([0.7, 1.3])
        with c1:
            st.markdown("Simpatía Política")
            if not df_sim_per.empty:
                fig_sim_pie = px.pie(
                    df_sim_per, names="Item", values="Valor",
                    hole=0.2, color_discrete_sequence=["#E57373", "#8FC97E" ]
                )
                fig_sim_pie.update_traces(textinfo="label+percent", textposition="inside")
                fig_sim_pie.update_layout(
                    showlegend=False, height=240, margin=dict(l=0, r=0, t=10, b=10),
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
                )
                st.plotly_chart(fig_sim_pie, use_container_width=True)
            else:
                st.info("Sin datos de simpatía en este periodo.")
        with c2:
            # --- HISTÓRICO SIMPATÍA (una barra dividida por periodo) ---
            if not df_sim_all.empty:
                # df_sim_all debe tener Periodo_str, Item, Valor
                fig_sim_hist = bar_100_stacked(
                    df_long=df_sim_all,
                    x_col="Periodo_str", y_col="Valor", color_col="Item",
                    color_order=["No simpatizan", "Simpatizan"],
                    color_map={"No simpatizan":"#E57373", "Simpatizan":"#8FC97E"},
                )
                fig_sim_hist.update_layout(
                    height=300,
                    margin=dict(l=0, r=0, t=10, b=40),
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    xaxis_title=None, yaxis_title="%",
                    legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center"),
                    xaxis=dict(tickangle=-30)
                )
                st.plotly_chart(fig_sim_hist, use_container_width=True, theme=None)
            else:
                st.info("Sin serie histórica de simpatía.")

        # ---------- FILA 2: dos barras apiladas con histórico ----------
        c3, c4 = st.columns([0.7,1.3])

        with c3:
            st.markdown("Confianza en el gobierno")
            if not df_conf_per.empty:
                fig_conf_pie = px.pie(
                    df_conf_per, names="Item", values="Valor",
                    hole=0.2, color_discrete_sequence=["#E57373", "#FFD54F", "#64B5F6", "#81C784"]
                )
                fig_conf_pie.update_traces(textinfo="label+percent", textposition="inside")
                fig_conf_pie.for_each_trace(
                    lambda t: t.update(labels=[
                        {
                            "Ninguna confianza": "Ninguna",
                            "Poca confianza": "Poca",
                            "Alguna confianza": "Alguna",
                            "Mucha confianza": "Mucha"
                        }.get(lbl, lbl)
                        for lbl in t.labels
                    ])
                )
                fig_conf_pie.update_layout(
                    showlegend=False, height=293, margin=dict(l=0, r=0, t=10, b=10),
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
                )
                st.plotly_chart(fig_conf_pie, use_container_width=True)  # <-- aquí el correcto
            else:
                st.info("Sin datos de confianza en este periodo.")

            with c4:
                if not df_conf_all.empty:
                    fig_conf_hist = bar_100_stacked(
                        df_long=df_conf_all,
                        x_col="Periodo_str", y_col="Valor", color_col="Item",
                        color_order=[
                            "Ninguna confianza","Poca confianza","Alguna confianza","Mucha confianza"
                        ],
                        color_map={
                            "Ninguna confianza":"#E57373",
                            "Poca confianza":"#FFD54F",
                            "Alguna confianza":"#64B5F6",
                            "Mucha confianza":"#81C784",
                        },
                    )
                    fig_conf_hist.update_layout(
                        height=320,
                        margin=dict(l=0, r=0, t=10, b=30),
                        plot_bgcolor="rgba(0,0,0,0)",
                        paper_bgcolor="rgba(0,0,0,0)",
                        xaxis_title=None,       # quita título eje X
                        yaxis_title="%",        # cambia título eje Y
                        legend=dict(
                            orientation="h",
                            yanchor="top", y=-0.2,
                            xanchor="center"
                        )
                    )
                    st.plotly_chart(fig_conf_hist, use_container_width=True, theme=None)
                else:
                    st.info("Sin serie histórica de confianza.")

    with col2:
        with st.container(border=True):
            st.markdown("##### Principal Problema del País")
            # Ranking del periodo
            st.markdown('Resultados')
            df_pp = df_per[df_per["seccion_norm"]=="principal problema del pais"].copy()
            if not df_pp.empty:
                df_pp = df_pp.sort_values("Valor", ascending=True)
                figp = px.bar(df_pp, x="Valor", y="Item", orientation="h",
                            text="Valor", color="Valor", color_continuous_scale="Blues")
                figp.update_traces(texttemplate="%{x:.1f}%", textposition="outside")
                figp.update_layout(height=240, coloraxis_showscale=False,
                                margin=dict(l=0,r=0,t=8,b=0), xaxis_title='%', yaxis_title=None,
                                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(figp, use_container_width=True)
            else:
                st.info("No hay 'Principal problema del país' para este periodo.")

            # Evolución de los top-N (por defecto top 5 del último periodo)
            st.markdown('Evolución de los resultados')
            df_pp_all = df[df["seccion_norm"]=="principal problema del pais"].copy()
            if not df_pp_all.empty:
                # top-N del periodo seleccionado
                c1, c2 = st.columns([1,7])
                with c1:
                    st.caption('Top N problemas')
                with c2:
                    topN = st.slider("", 3, 10, 5, key="topN_pp", label_visibility="collapsed")
                
                top_items = df_pp.sort_values("Valor", ascending=False)["Item"].head(topN).tolist()
                serie = df_pp_all[df_pp_all["Item"].isin(top_items)].copy()
                serie = serie.sort_values("Periodo")
                serie["Periodo_str"] = serie["Periodo"].dt.strftime("%Y-%m")
                fig_evo = px.line(serie, x="Periodo_str", y="Valor", color="Item")
                fig_evo.update_layout(height=240, margin=dict(l=0,r=0,t=0,b=0), xaxis_title=None, yaxis_title='%',
                                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", legend_title_text=None)
                st.plotly_chart(fig_evo, use_container_width=True)
            else:
                st.info("Sin serie histórica de problemas.")
            st.markdown('</div>', unsafe_allow_html=True)







