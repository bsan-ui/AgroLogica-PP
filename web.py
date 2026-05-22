import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="AgroLógica Pro", page_icon="🌱", layout="wide")

st.title("🌱 Sistema AgroLógica")
st.markdown("Herramienta digital para el diagnóstico de la salud del suelo y optimización de cultivos.")
st.divider()

tab1, tab2 = st.tabs(["📊 Análisis Masivo de Parcelas", "🧪 Diagnosticar Nueva Muestra"])

# =====================================================================
# MOTOR LÓGICO: ANALÍTICA PRESCRIPTIVA
# =====================================================================
def diagnostico_preciso(ph, mo, n, p, k, pendiente, erosion, lluvia, cultivo):
    if pendiente > 35.0 or str(erosion).lower() == "severa":
        return "Riesgo Físico", "🚨 RIESGO DE DESLAVE: Inclinación/erosión crítica. No invertir en químicos."
    if lluvia > 1000.0 and pendiente > 25.0:
        return "Riesgo Ambiental", "⛈️ RIESGO DE LAVADO: La pendiente y altas lluvias deslavarán los químicos."

    cultivo = str(cultivo).lower().strip()
    ideales = {
        "maíz": {"lluvia_min": 600, "lluvia_max": 1200, "ph_min": 5.5, "ph_max": 7.2, "n": 30.0, "n_max": 70.0, "p": 15.0, "p_max": 50.0, "k": 150.0, "k_max": 250.0, "mo": 3.0, "mo_max": 8.0},
        "maiz": {"lluvia_min": 600, "lluvia_max": 1200, "ph_min": 5.5, "ph_max": 7.2, "n": 30.0, "n_max": 70.0, "p": 15.0, "p_max": 50.0, "k": 150.0, "k_max": 250.0, "mo": 3.0, "mo_max": 8.0},
        "frijol": {"lluvia_min": 400, "lluvia_max": 800, "ph_min": 6.0, "ph_max": 7.5, "n": 15.0, "n_max": 40.0, "p": 12.0, "p_max": 35.0, "k": 120.0, "k_max": 200.0, "mo": 2.5, "mo_max": 6.0},
        "nopal": {"lluvia_min": 200, "lluvia_max": 600, "ph_min": 5.0, "ph_max": 8.5, "n": 10.0, "n_max": 30.0, "p": 10.0, "p_max": 30.0, "k": 100.0, "k_max": 180.0, "mo": 1.5, "mo_max": 5.0},
        "aguacate": {"lluvia_min": 800, "lluvia_max": 1500, "ph_min": 5.5, "ph_max": 7.0, "n": 20.0, "n_max": 60.0, "p": 20.0, "p_max": 60.0, "k": 150.0, "k_max": 300.0, "mo": 3.5, "mo_max": 10.0}
    }
    
    if cultivo not in ideales: cultivo = "maíz"
    req = ideales[cultivo]
    recomendaciones = []
    alertas_exceso_quimico = []
    
    if n < req["n"]: recomendaciones.append(f"Falta {round(req['n'] - n, 1)} N")
    if p < req["p"]: recomendaciones.append(f"Falta {round(req['p'] - p, 1)} P")
    if k < req["k"]: recomendaciones.append(f"Falta {round(req['k'] - k, 1)} K")
    if mo < req["mo"]: recomendaciones.append(f"Falta {round(req['mo'] - mo, 1)}% MO")
    
    if lluvia < req["lluvia_min"]: recomendaciones.append("Sequía: Instalar riego")
    elif lluvia > req["lluvia_max"]: recomendaciones.append("Exceso Hídrico: Requiere drenaje")
    if mo > req["mo_max"]: recomendaciones.append(f"Bajar Humedad (+{round(mo - req['mo_max'], 1)}% MO)")
    if ph < req["ph_min"]: recomendaciones.append(f"Subir pH (+{round(req['ph_min'] - ph, 1)})")
    elif ph > req["ph_max"]: recomendaciones.append(f"Bajar pH (-{round(ph - req['ph_max'], 1)})")

    if n > req["n_max"]: alertas_exceso_quimico.append(f"Nitrógeno (+{round(n - req['n_max'], 1)})")
    if p > req["p_max"]: alertas_exceso_quimico.append(f"Fósforo (+{round(p - req['p_max'], 1)})")
    if k > req["k_max"]: alertas_exceso_quimico.append(f"Potasio (+{round(k - req['k_max'], 1)})")
        
    if len(alertas_exceso_quimico) > 0:
        return "Exceso", "🚨 TOXICIDAD: " + ", ".join(alertas_exceso_quimico)
    elif len(recomendaciones) == 0:
        return "Alta", "✅ Condiciones óptimas. Sin ajustes."
    elif len(recomendaciones) <= 2:
        return "Media", "💡 Corregir: " + " | ".join(recomendaciones)
    else:
        return "Baja", "⚠️ Nivelar: " + " | ".join(recomendaciones)

# =====================================================================
# PESTAÑA 1: PROCESAMIENTO Y ANÁLISIS MASIVO DE DATOS
# =====================================================================
with tab1:
    st.header("Análisis de Parcelas Registradas")
    st.markdown("Sube el archivo de datos recopilados para generar el plan de acción de todas las parcelas.")
    
    archivo_csv = st.file_uploader("Selecciona el archivo de la parcela (Formato .CSV)", type=["csv"])
    
    if archivo_csv is not None:
        df = pd.read_csv(archivo_csv)
        df_limpio = df.fillna(df.median(numeric_only=True))
        st.success("✅ El archivo se cargó correctamente y los datos incompletos fueron corregidos.")
        
        # Nombres exactos de las columnas según tu archivo CSV
        cols_requeridas = ['pH', 'Grado de erosión', 'Pendiente %', 'Materia orgánica %', 'Lluvia mm', 'Fósforo mg/kg', 'Nitrógeno mg/kg', 'Potasio mg/kg', 'Cosecha principal']
        
        # Validamos que el archivo tenga la información necesaria
        if all(col in df_limpio.columns for col in cols_requeridas):
            st.divider()
            st.subheader("🤖 Plan de Optimización Generado")
            
            # MAGIA DE PANDAS: Aplicamos la función y dividimos el resultado en 2 columnas nuevas
            with st.spinner("Procesando matriz de datos..."):
                df_limpio[['Diagnóstico_AgroLogica', 'Plan_de_Acción']] = df_limpio.apply(
                    lambda f: pd.Series(diagnostico_preciso(
                        f['pH'], f['Materia orgánica %'], f['Nitrógeno mg/kg'], f['Fósforo mg/kg'], 
                        f['Potasio mg/kg'], f['Pendiente %'], f['Grado de erosión'], f['Lluvia mm'], f['Cosecha principal']
                    )), axis=1
                )
            
            # Mostramos una tabla solo con lo que le importa al agricultor
            columnas_vista = ['Parcela', 'Cosecha principal', 'Diagnóstico_AgroLogica', 'Plan_de_Acción']
            if 'Parcela' in df_limpio.columns:
                st.dataframe(df_limpio[columnas_vista], use_container_width=True, height=350)
            else:
                st.dataframe(df_limpio[['Cosecha principal', 'Diagnóstico_AgroLogica', 'Plan_de_Acción']], use_container_width=True)
            
            # Tarjetas de resumen
            total = len(df_limpio)
            riesgos = len(df_limpio[df_limpio['Diagnóstico_AgroLogica'].isin(['Riesgo Físico', 'Riesgo Ambiental', 'Exceso'])])
            saludables = len(df_limpio[df_limpio['Diagnóstico_AgroLogica'] == 'Alta'])
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Parcelas Totales", f"{total}")
            c2.metric("Parcelas Óptimas", f"{saludables}")
            c3.metric("Riesgos Detectados", f"{riesgos}")
            
            # BOTÓN DE DESCARGA DEL REPORTE
            st.markdown("### 📥 Exportar Resultados")
            csv_export = df_limpio.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Descargar Reporte de Diagnóstico (.CSV)",
                data=csv_export,
                file_name="Reporte_AgroLogica_Resultados.csv",
                mime="text/csv",
                type="secondary"
            )

            st.divider()
            
            with st.expander("🔬 CLIC AQUÍ: Ver justificación matemática y académica (Rúbrica)"):
                cols_num = ['pH', 'Pendiente %', 'Materia orgánica %', 'Nitrógeno mg/kg']
                st.markdown("### 1. Estadística: Estandarización (Z-Score)")
                df_std = (df_limpio[cols_num] - df_limpio[cols_num].mean()) / df_limpio[cols_num].std()
                st.write(df_std.head(3))
                
                st.markdown("### 2. Álgebra Lineal: Similitud y Distancia Vectorial")
                st.latex(r"\|\vec{v}_{parcela} - \vec{v}_{ideal}\|")
                vector_ideal = np.array([6.5, 10.0, 4.0, 40.0])
                df_limpio['Distancia_al_Ideal'] = df_limpio[cols_num].apply(
                    lambda fila: np.linalg.norm(fila.values - vector_ideal), axis=1
                )
                st.write(df_limpio[['Distancia_al_Ideal']].head(3))
                
                st.markdown("### 3. Cálculo Diferencial: Optimización")
                st.latex(r"f'(x) = -0.10x + 5 = 0 \implies x = 50 \text{ mg/kg}")
                st.info("La derivada primera determina que 50 mg/kg es el punto óptimo.")
        else:
            st.error("⚠️ El archivo CSV no contiene las columnas necesarias. Verifica que los nombres de las columnas coincidan exactamente con la base de datos original.")

# =====================================================================
# PESTAÑA 2: CLASIFICADOR DE NUEVAS MUESTRAS (Interfaz de usuario)
# =====================================================================
with tab2:
    st.header("Analizar un Nuevo Terreno Manualmente")
    st.markdown("Introduce las lecturas del terreno y del análisis químico para obtener una recomendación precisa.")
    
    st.subheader("🌍 1. Datos Físicos y Climáticos")
    col1, col2, col3, col4 = st.columns(4)
    with col1: cultivo_input = st.selectbox("Cultivo a sembrar:", ["Maíz", "Frijol", "Nopal", "Aguacate"])
    with col2: erosion_input = st.selectbox("Nivel de Erosión:", ["Leve", "Moderada", "Severa"])
    with col3: pendiente_input = st.number_input("Pendiente (%):", 0.0, 90.0, 10.0, step=1.0)
    with col4: lluvia_input = st.number_input("Lluvia anual (mm):", 0.0, 3000.0, 750.0, step=10.0)

    st.divider()

    st.subheader("🧪 2. Datos Químicos (Laboratorio)")
    col5, col6, col7, col8 = st.columns(4)
    with col5: ph_input = st.slider("Acidez (pH):", 0.0, 14.0, 6.5, step=0.1)
    with col6: n_input = st.number_input("Nitrógeno (mg/kg):", 0.0, 150.0, 30.0, step=1.0)
    with col7: p_input = st.number_input("Fósforo (mg/kg):", 0.0, 150.0, 15.0, step=1.0)
    with col8: k_input = st.number_input("Potasio (mg/kg):", 0.0, 300.0, 150.0, step=1.0)
    mo_input = st.number_input("Materia Orgánica (%):", 0.0, 15.0, 3.0, step=0.1)
        
    st.markdown(" ")
    if st.button("Generar Diagnóstico Integral", type="primary", use_container_width=True):
        nivel, mensaje = diagnostico_preciso(ph_input, mo_input, n_input, p_input, k_input, pendiente_input, erosion_input, lluvia_input, cultivo_input)
        
        st.subheader("📢 Diagnóstico y Plan de Acción:")
        if nivel == "Alta": st.success(f"✨ **FERTILIDAD ALTA:** {mensaje}")
        elif nivel == "Media": st.info(f"💡 **FERTILIDAD MEDIA:** {mensaje}")
        elif nivel in ["Riesgo Físico", "Riesgo Ambiental"]: st.error(f"🏔️ **TERRENO NO APTO:** {mensaje}")
        elif nivel == "Exceso": st.error(f"☠️ **{mensaje}**")
        else: st.warning(f"⚠️ **ATENCIÓN REQUERIDA:** {mensaje}")