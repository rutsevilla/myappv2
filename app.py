# pip install streamlit plotly pandas numpy streamlit-option-menu unidecode
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from streamlit_option_menu import option_menu
from unidecode import unidecode
import os, base64, mimetypes
from funciones import *    
import plotly.io as pio

st.set_page_config(
    page_title="Encuestas de Opinión • Costa Rica",
    page_icon="./circle-white.svg",
    layout="wide",
    initial_sidebar_state="collapsed",
)

LOGO_PATH = "./TDP_Logo_White.svg"   # ← tu logo
CSV_PATH  = "./encuestas_cr.csv"  # ← tu CSV

# Utilidad: imagen a DataURI (para <img src="..."> dentro de HTML)
logo_data_uri = img_to_data_uri(LOGO_PATH)

# --- (A) Login gate: si no hay sesión, no se muestra el tablero ---
# Usa tu logo_data_uri si quieres que aparezca en la tarjeta de login
if not login(logo_data_uri, "Encuestas de Opinión - Costa Rica"):
    st.stop()

# --- (B) Ya hay sesión: muestra user-box y el tablero ---
# user_header()

# Paleta (ajusta aquí tus colores)
PRIMARY      = "#15A1E2"   # Azul corporativo
PRIMARY_DARK = "#0F6F9D"
BG_GRAD_A    = "#175CA1"   # Degradado fondo - inicio
BG_GRAD_B    = "#07A9E0"   # Degradado fondo - fin
HEADER_A     = "#2E498A"   # Degradado header - inicio
HEADER_B     = "#2E498A"   # Degradado header - fin
CARD_BG      = "rgba(255,255,255,0.10)"  # fondo semitransparente para .box
TEXT_SOFT    = "#EAF6FF"


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
    
# ================== LAYOUT A DOS COLUMNAS ==================
colL, colR = st.columns([3, 5])  # ajusta proporciones a gusto

# ---------------------- COLUMNA IZQUIERDA ----------------------
with colL:
    # (1) Selector de encuesta
    with st.container(border=False):
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown('<div class="box-title">Selector de Encuesta</div>', unsafe_allow_html=True)
        with c2:
            idx_def = len(periodos)-1 if len(periodos) > 0 else 0
            periodo_sel = st.selectbox(
                label="", options=periodos, index=idx_def,
                format_func=lambda d: labels_por_periodo.get(d, pd.to_datetime(d).strftime("%b-%Y")),
                key="selector_encuestas", label_visibility="collapsed"
            )
        df_per = filtrar_periodo(df, periodo_sel)

    # (2) Características demográficas
    with st.container(border=True):
        st.markdown('##### Características demográficas de la muestra')
        c1, c2, c3 = st.columns(3)

        # --- Género ---
        with c1:
            st.caption("Género")
            df_gen = df_per[df_per["seccion_norm"] == "genero"].sort_values("Item")
            if not df_gen.empty:
                fig_g = px.pie(df_gen, names="Item", values="Valor",
                               color_discrete_sequence=[PRIMARY, "#8FBAD3", "#9DBFD3"])
                fig_g.update_traces(textinfo="label+percent", textposition="inside")
                fig_g.update_layout(height=200, showlegend=False, margin=dict(l=0,r=0,t=0,b=0),
                                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_g, use_container_width=True)
            else:
                st.info("Sin datos de Género para este período.")

        # --- Edad ---
        with c2:
            st.caption("Edad")
            df_edad = df_per[df_per["seccion_norm"] == "edad"]
            if not df_edad.empty:
                fig_ed = px.pie(df_edad, names="Item", values="Valor",
                                color_discrete_sequence=["#7CC4E8", PRIMARY_DARK, "#79A6C7", "#B5D6EA"])
                fig_ed.update_traces(textinfo="label+percent", textposition="inside")
                fig_ed.update_layout(height=200, showlegend=False, margin=dict(l=0,r=0,t=0,b=0),
                                     plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_ed, use_container_width=True)
            else:
                st.info("Sin datos de Edad para este período.")

        # --- Educación ---
        with c3:
            st.caption("Nivel de educación")
            edu_norms = {"nivel de educacion", "nivel de eduacion", "nivel de eduación"}
            df_edu = df_per[df_per["seccion_norm"].isin({limpiar_txt(s) for s in edu_norms})]
            if not df_edu.empty:
                fig_e = px.pie(df_edu, names="Item", values="Valor",
                               color_discrete_sequence=["#4FC3F7", "#1E88E5", "#90CAF9"])
                fig_e.update_traces(textinfo="label+percent", textposition="inside")
                fig_e.update_layout(height=200, showlegend=False, margin=dict(l=0,r=0,t=0,b=0),
                                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_e, use_container_width=True)
            else:
                st.info("Sin datos de Educación para este período.")

    # (3) Simpatía / Confianza (toggle con 2 gráficos)
    # Prepara datasets una sola vez
    df_sim_per  = df_per[df_per["seccion_norm"] == "simpatia electoral"].copy()
    df_sim_all  = df[df["seccion_norm"] == "simpatia electoral"].copy()
    df_sim_all  = df_sim_all.sort_values("Periodo")
    df_sim_all["Periodo_str"] = df_sim_all["Periodo"].dt.strftime("%Y-%m")

    mask_conf_per = df_per["seccion_norm"].str.startswith("nivel de confianza", na=False)
    mask_conf_all = df["seccion_norm"].str.startswith("nivel de confianza", na=False)
    df_conf_per   = df_per[mask_conf_per].copy()
    df_conf_all   = df[mask_conf_all].copy()
    df_conf_all   = df_conf_all.sort_values("Periodo")
    df_conf_all["Periodo_str"] = df_conf_all["Periodo"].dt.strftime("%Y-%m")

    with st.container(border=True):
        st.markdown("##### Simpatía Política y Confianza en el Gobierno")
        try:
            elegido = st.segmented_control("", ["Simpatía", "Confianza"], default="Simpatía",
                                           key="toggle_sim_conf", label_visibility="collapsed")
        except Exception:
            elegido = st.radio("", ["Simpatía", "Confianza"], index=0, horizontal=True,
                               key="toggle_sim_conf_radio", label_visibility="collapsed")

        c1, c2 = st.columns([0.7, 1.3])

        if elegido == "Simpatía":
            with c1:
                st.markdown("Simpatía Política")
                if not df_sim_per.empty:
                    fig_sim_pie = px.pie(df_sim_per, names="Item", values="Valor",
                                         hole=0.2, color_discrete_sequence=["#E57373", "#8FC97E"])
                    fig_sim_pie.update_traces(textinfo="label+percent", textposition="inside")
                    fig_sim_pie.update_layout(showlegend=False, height=220,
                                              margin=dict(l=0,r=0,t=10,b=10),
                                              plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig_sim_pie, use_container_width=True)
                else:
                    st.info("Sin datos de simpatía en este periodo.")
            with c2:
                if not df_sim_all.empty:
                    fig_sim_hist = bar_100_stacked(
                        df_long=df_sim_all, x_col="Periodo_str", y_col="Valor", color_col="Item",
                        color_order=["No simpatizan", "Simpatizan"],
                        color_map={"No simpatizan":"#E57373", "Simpatizan":"#8FC97E"},
                    )
                    fig_sim_hist.update_layout(
                        height=280, margin=dict(l=0,r=0,t=10,b=40),
                        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                        xaxis_title=None, yaxis_title="%",
                        legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center"),
                        xaxis=dict(tickangle=-30)
                    )
                    st.plotly_chart(fig_sim_hist, use_container_width=True, theme=None)
                else:
                    st.info("Sin serie histórica de simpatía.")
        else:
            with c1:
                st.markdown("Confianza en el gobierno")
                if not df_conf_per.empty:
                    fig_conf_pie = px.pie(
                        df_conf_per, names="Item", values="Valor", hole=0.2,
                        color_discrete_sequence=["#E57373", "#FFD54F", "#64B5F6", "#81C784"]
                    )
                    fig_conf_pie.update_traces(textinfo="label+percent", textposition="inside")
                    fig_conf_pie.for_each_trace(lambda t: t.update(labels=[
                        {"Ninguna confianza":"Ninguna","Poca confianza":"Poca",
                         "Alguna confianza":"Alguna","Mucha confianza":"Mucha"}.get(lbl, lbl)
                        for lbl in t.labels
                    ]))
                    fig_conf_pie.update_layout(showlegend=False, height=220,
                                               margin=dict(l=0,r=0,t=10,b=10),
                                               plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig_conf_pie, use_container_width=True)
                else:
                    st.info("Sin datos de confianza en este periodo.")
            with c2:
                if not df_conf_all.empty:
                    fig_conf_hist = bar_100_stacked(
                        df_long=df_conf_all, x_col="Periodo_str", y_col="Valor", color_col="Item",
                        color_order=["Ninguna confianza","Poca confianza","Alguna confianza","Mucha confianza"],
                        color_map={"Ninguna confianza":"#E57373","Poca confianza":"#FFD54F",
                                   "Alguna confianza":"#64B5F6","Mucha confianza":"#81C784"},
                    )
                    fig_conf_hist.update_layout(
                        height=270, margin=dict(l=0,r=0,t=10,b=30),
                        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                        xaxis_title=None, yaxis_title="%",
                        legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center")
                    )
                    st.plotly_chart(fig_conf_hist, use_container_width=True, theme=None)
                else:
                    st.info("Sin serie histórica de confianza.")

# ---------------------- COLUMNA DERECHA ----------------------
with colR:

    # ===== helpers locales para no repetir código =====
    def _find_section(df, needle: str):
        """Devuelve el nombre exacto de la sección que contenga 'needle' (en minúsculas)."""
        needle = needle.lower()
        for s in df["Seccion"].dropna().unique():
            if needle in str(s).lower():
                return s
        return None

    def render_valoracion(df, df_per, seccion_label: str, titulo_bloque: str):
        """Pinta Resultados (barras) + Evolución (línea) con el estilo actual."""
        st.markdown(f"##### {titulo_bloque}")

        # --- Resultados del periodo seleccionado ---
        df_val_per = df_per[df_per["Seccion"] == seccion_label].copy()
        if df_val_per.empty:
            fig_resultados = px.bar(pd.DataFrame({"Respuesta": [], "Porcentaje": []}),
                                    x="Porcentaje", y="Respuesta")
        else:
            normalizador = limpiar_txt if 'limpiar_txt' in globals() else lambda s: str(s).strip().lower()
            df_val_per["item_norm"] = df_val_per["Item"].map(lambda s: normalizador(s) if pd.notna(s) else None)
            mapa = {
                "positivo":"Positivos","positiva":"Positivos","positivos":"Positivos","positivas":"Positivos",
                "neutral":"Neutros","neutra":"Neutros","neutros":"Neutros","neutras":"Neutros",
                "negativo":"Negativos","negativa":"Negativos","negativos":"Negativos","negativas":"Negativos",
            }
            df_val_per["grupo"] = df_val_per["item_norm"].map(mapa)
            res = (df_val_per.dropna(subset=["grupo"]).groupby("grupo", as_index=False)["Valor"].sum())
            res = (res.set_index("grupo").reindex(["Positivos","Neutros","Negativos"]).fillna(0)
                     .reset_index().rename(columns={"grupo":"Respuesta","Valor":"Porcentaje"}))
            res["Porcentaje"] = pd.to_numeric(res["Porcentaje"], errors="coerce").fillna(0)

            fig_resultados = px.bar(
                res, x="Porcentaje", y="Respuesta", orientation="h",
                color="Respuesta",
                color_discrete_map={"Positivos": PRIMARY, "Neutros": "#8FBAD3", "Negativos": "#F07B7B"},
                text="Porcentaje"
            )
            fig_resultados.update_traces(texttemplate="%{x:.1f}%", textposition="outside")
            fig_resultados.update_layout(
                height=226, showlegend=False, margin=dict(l=0,r=0,t=0,b=0),
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                xaxis_title=None, yaxis_title=None
            )
            fig_resultados.update_xaxes(ticksuffix="%")

        # --- Evolución serie completa ---
        df_val = df[df["Seccion"] == seccion_label].copy()
        if df_val.empty:
            fig_evol = px.line(pd.DataFrame({"Periodo_str": [], "Valor": [], "tipo": []}))
        else:
            df_val["item_norm"] = df_val["Item"].map(limpiar_txt)
            mapa_tipo = {
                "positiva":"positiva","positivos":"positiva",
                "neutral":"neutral","neutros":"neutral",
                "negativa":"negativa","negativos":"negativa"
            }
            df_val["tipo"] = df_val["item_norm"].map(mapa_tipo)
            df_val = df_val.dropna(subset=["tipo"]).sort_values("Periodo")
            df_val["Periodo_str"] = df_val["Periodo"].dt.strftime("%Y-%m")
            fig_evol = px.line(
                df_val, x="Periodo_str", y="Valor", color="tipo",
                category_orders={"tipo":["positiva","neutral","negativa"]},
                color_discrete_map={"positiva":PRIMARY,"neutral":"#8FBAD3","negativa":"#F07B7B"},
            )
            fig_evol.update_layout(
                height=226, margin=dict(l=0,r=0,t=8,b=0),
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                xaxis_title=None, yaxis_title=None, legend_title_text=None
            )

        # render lado a lado como antes
        colA, colB = st.columns([1.2, 1.8])
        with colA:
            st.markdown('Resultados')
            st.plotly_chart(fig_resultados, use_container_width=True)
        with colB:
            st.markdown('Evolución de los resultados')
            st.plotly_chart(fig_evol, use_container_width=True)


    # ===== pestañas =====
    tab_val, tab_prob, tab_inst = st.tabs(["Gestión del Gobierno y del Presidente", "Principales Problemas del País", "Labor de las Instituciones"])

    # ---------- TAB: VALORACIÓN (Gobierno + Presidente) ----------
    with tab_val:
        with st.container(border=True):
            # Detecta nombres exactos de secciones en tu CSV
            sec_gob  = _find_section(df, "gestión del gobierno") or _find_section(df, "gestion del gobierno")
            sec_pres = _find_section(df, "gestión del presidente") or _find_section(df, "gestion del presidente")

            if sec_gob is None and sec_pres is None:
                st.info("No se encontraron variables de valoración para Gobierno ni Presidente.")
            else:
                if sec_gob is not None:
                    render_valoracion(df, df_per, sec_gob, "Valoración de la gestión del Gobierno")
                else:
                    st.info("No hay datos de valoración del Gobierno para este periodo/serie.")
                
                st.divider()

                if sec_pres is not None:
                    render_valoracion(df, df_per, sec_pres, "Valoración de la gestión del Presidente")
                else:
                    st.info("No hay datos de valoración del Presidente para este periodo/serie.")

    # ---------- TAB: PROBLEMAS DEL PAÍS (barras + evolución) ----------
    with tab_prob:
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
                figp.update_layout(height=261, coloraxis_showscale=False,
                                   margin=dict(l=0,r=0,t=8,b=0), xaxis_title='%', yaxis_title=None,
                                   plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(figp, use_container_width=True)
            else:
                st.info("No hay 'Principal problema del país' para este periodo.")

            # Evolución de los top-N
            st.markdown('Evolución de los resultados')
            df_pp_all = df[df["seccion_norm"]=="principal problema del pais"].copy()
            if not df_pp_all.empty:
                c1, c2 = st.columns([1,7])
                with c1:
                    st.caption('Top N problemas')
                with c2:
                    topN = st.slider("", 3, 10, 5, key="topN_pp", label_visibility="collapsed")

                top_items = df_pp.sort_values("Valor", ascending=False)["Item"].head(topN).tolist()
                serie = df_pp_all[df_pp_all["Item"].isin(top_items)].copy()
                serie = serie.sort_values("Periodo")
                serie["Periodo_str"] = serie["Periodo"].dt.strftime("%Y-%m")

                fig_evo_pp = px.line(serie, x="Periodo_str", y="Valor", color="Item")
                fig_evo_pp.update_layout(
                    height=246, margin=dict(l=0,r=0,t=0,b=0),
                    xaxis_title=None, yaxis_title='%',
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                    legend_title_text=None
                )
                st.plotly_chart(fig_evo_pp, use_container_width=True)
            else:
                st.info("Sin serie histórica de problemas.")

    # ---------- TAB: INSTITUCIONES (barras + evolución) ----------
with tab_inst:
    with st.container(border=True):
        st.markdown("##### Evaluación de la labor de las instituciones")

        # --- Normalización robusta de la sección (con/ sin tildes y con el typo 'insituciones')
        variants = {
            "evaluación de la labor de las instituciones",
            "evaluacion de la labor de las instituciones",
            "evaluación de la labor de las insituciones",
            "evaluacion de la labor de las insituciones",
        }
        try:
            variants_norm = {limpiar_txt(v) for v in variants}
            seccion_norm_col = "seccion_norm"
        except Exception:
            # fallback por si no tienes limpiar_txt
            variants_norm = {v.lower() for v in variants}
            seccion_norm_col = "Seccion"

        # --- Datos del periodo seleccionado (ranking)
        if seccion_norm_col == "seccion_norm":
            df_inst_per = df_per[df_per["seccion_norm"].isin(variants_norm)].copy()
            df_inst_all = df[df["seccion_norm"].isin(variants_norm)].copy()
        else:
            # fallback buscando 'contains'
            df_inst_per = df_per[df_per["Seccion"].str.lower().str.contains("evaluaci") & 
                                 df_per["Seccion"].str.lower().str.contains("instituc")].copy()
            df_inst_all = df[df["Seccion"].str.lower().str.contains("evaluaci") & 
                             df["Seccion"].str.lower().str.contains("instituc")].copy()

        st.markdown("Resultados")
        if not df_inst_per.empty:
            df_inst_per = df_inst_per.sort_values("Valor", ascending=True)
            fig_inst = px.bar(
                df_inst_per, x="Valor", y="Item", orientation="h",
                text="Valor", color="Valor", color_continuous_scale="Blues"
            )
            fig_inst.update_traces(texttemplate="%{x:.1f}", textposition="outside")
            fig_inst.update_layout(
                height=260, coloraxis_showscale=False,
                margin=dict(l=0, r=0, t=8, b=0),
                xaxis_title="Puntuación (0-10)", yaxis_title=None,
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig_inst, use_container_width=True)
        else:
            st.info("No hay evaluación de instituciones para este periodo.")

        # --- Evolución (elige top N del periodo actual)
        st.markdown("Evolución de los resultados")
        if not df_inst_all.empty and not df_inst_per.empty:
            c1, c2 = st.columns([1, 7])
            with c1:
                st.caption("Top N instituciones")
            with c2:
                topN_inst = st.slider("", 3, 12, 6, key="topN_inst", label_visibility="collapsed")

            top_items = df_inst_per.sort_values("Valor", ascending=False)["Item"].head(topN_inst).tolist()
            serie = df_inst_all[df_inst_all["Item"].isin(top_items)].copy()
            serie = serie.sort_values("Periodo")
            serie["Periodo_str"] = serie["Periodo"].dt.strftime("%Y-%m")

            fig_inst_evo = px.line(serie, x="Periodo_str", y="Valor", color="Item")
            fig_inst_evo.update_layout(
                height=242, margin=dict(l=0, r=0, t=0, b=0),
                xaxis_title=None, yaxis_title="Puntuación (0-10)",
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                legend_title_text=None
            )
            st.plotly_chart(fig_inst_evo, use_container_width=True)
        else:
            st.info("Sin serie histórica de instituciones.")







