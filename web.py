import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# Configuración de página
st.set_page_config(page_title="AgroLógica Pro", page_icon="🌱", layout="wide")

st.title("Sistema AgroLógica")
st.markdown("Herramienta digital para el diagnóstico de la salud del suelo y optimización de cultivos.")
st.divider()

tab1, tab2 = st.tabs(["Analizar todos mis terrenos", "Revisar un solo terreno"])

# =====================================================================
# Motor lógico: Analítica prescriptiva
# =====================================================================
def diagnostico_preciso(ph, mo, n, p, k, pendiente, erosion, lluvia, cultivo):
    # Filtro físico
    if pendiente > 35.0 or str(erosion).lower() == "severa":
        return "Riesgo Físico", "Riesgo de deslave: Inclinación o erosión crítica. Te sugerimos no invertir en químicos aquí."
    if lluvia > 1000.0 and pendiente > 25.0:
        return "Riesgo Ambiental", "Riesgo de lavado hídrico: La pendiente y las altas lluvias deslavarán los fertilizantes."

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
    
    # Déficits
    if n < req["n"]: recomendaciones.append(f"Falta {round(req['n'] - n, 1)} N")
    if p < req["p"]: recomendaciones.append(f"Falta {round(req['p'] - p, 1)} P")
    if k < req["k"]: recomendaciones.append(f"Falta {round(req['k'] - k, 1)} K")
    if mo < req["mo"]: recomendaciones.append(f"Falta {round(req['mo'] - mo, 1)}% MO")
    
    # Clima y pH
    if lluvia < req["lluvia_min"]: recomendaciones.append("Sequía: Instalar riego")
    elif lluvia > req["lluvia_max"]: recomendaciones.append("Exceso hídrico: Requiere drenaje")
    if mo > req["mo_max"]: recomendaciones.append(f"Bajar humedad (+{round(mo - req['mo_max'], 1)}% MO)")
    if ph < req["ph_min"]: recomendaciones.append(f"Subir pH (+{round(req['ph_min'] - ph, 1)})")
    elif ph > req["ph_max"]: recomendaciones.append(f"Bajar pH (-{round(ph - req['ph_max'], 1)})")

    # Toxicidad
    if n > req["n_max"]: alertas_exceso_quimico.append(f"Nitrógeno (+{round(n - req['n_max'], 1)})")
    if p > req["p_max"]: alertas_exceso_quimico.append(f"Fósforo (+{round(p - req['p_max'], 1)})")
    if k > req["k_max"]: alertas_exceso_quimico.append(f"Potasio (+{round(k - req['k_max'], 1)})")
        
    # Salidas
    if len(alertas_exceso_quimico) > 0: return "Exceso", "Peligro de toxicidad: " + ", ".join(alertas_exceso_quimico)
    elif len(recomendaciones) == 0: return "Alta", "El terreno tiene condiciones óptimas. No requiere ajustes químicos."
    elif len(recomendaciones) <= 2: return "Media", "Corregir: " + " | ".join(recomendaciones)
    else: return "Baja", "Nivelar: " + " | ".join(recomendaciones)

# =====================================================================
# Pestaña 1: Procesamiento masivo
# =====================================================================
with tab1:
    st.header("Revisión de todas mis parcelas")
    st.markdown("Sube tu documento con los datos de tus tierras para decirte qué cuidados exactos necesitan.")
    
    archivo_csv = st.file_uploader("Selecciona el archivo (.CSV)", type=["csv"])
    
    if archivo_csv is not None:
        # Carga de datos originales
        df = pd.read_csv(archivo_csv)
        
        # Limpieza estadística
        df_limpio = df.fillna(df.median(numeric_only=True))
        st.success("El archivo se cargó correctamente.")
        
        # --- Visualización de datos completos y limpieza ---
        with st.expander("Ver la lista de mis tierras y corrección automática de errores", expanded=False):
            st.markdown("A veces olvidamos o no tenemos algún dato del campo. No te preocupes, si dejaste un espacio en blanco, el sistema lo rellena usando un cálculo seguro basado en tus otras tierras para que tu diagnóstico no falle.")
            
            c1, c2 = st.columns(2)
            with c1:
                st.caption("Tus datos originales (Con posibles espacios en blanco):")
                st.dataframe(df, height=250, use_container_width=True)
            with c2:
                st.caption("Datos corregidos (Espacios vacíos rellenados por el sistema):")
                st.dataframe(df_limpio, height=250, use_container_width=True)
        # ------------------------------------------------------------------

        cols_requeridas = ['pH', 'Grado de erosión', 'Pendiente %', 'Materia orgánica %', 'Lluvia mm', 'Fósforo mg/kg', 'Nitrógeno mg/kg', 'Potasio mg/kg', 'Cosecha principal']
        
        if all(col in df_limpio.columns for col in cols_requeridas):
            st.divider()
            st.subheader("Tu Plan de acción y fertilizantes")
            
            with st.spinner("Procesando matriz de datos..."):
                df_limpio[['Diagnóstico_AgroLogica', 'Plan_de_acción']] = df_limpio.apply(
                    lambda f: pd.Series(diagnostico_preciso(
                        f['pH'], f['Materia orgánica %'], f['Nitrógeno mg/kg'], f['Fósforo mg/kg'], 
                        f['Potasio mg/kg'], f['Pendiente %'], f['Grado de erosión'], f['Lluvia mm'], f['Cosecha principal']
                    )), axis=1
                )
            
            # Tabla Resumen
            columnas_vista = ['Parcela', 'Cosecha principal', 'Diagnóstico_AgroLogica', 'Plan_de_acción']
            if 'Parcela' in df_limpio.columns:
                st.dataframe(df_limpio[columnas_vista], use_container_width=True, height=350)
            else:
                st.dataframe(df_limpio[['Cosecha principal', 'Diagnóstico_AgroLogica', 'Plan_de_acción']], use_container_width=True)
            
            # Tarjetas
            total = len(df_limpio)
            riesgos = len(df_limpio[df_limpio['Diagnóstico_AgroLogica'].isin(['Riesgo físico', 'Riesgo ambiental', 'Exceso'])])
            saludables = len(df_limpio[df_limpio['Diagnóstico_AgroLogica'] == 'Alta'])
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Parcelas totales", f"{total}")
            c2.metric("Parcelas óptimas", f"{saludables}")
            c3.metric("Riesgos detectados", f"{riesgos}")
            
            # --- Gráfico de distribución ---
            st.markdown("### Resumen: ¿Cómo están nuestras tierras?")
            
            # Contamos cuántas parcelas hay de cada diagnóstico
            conteo_diagnostico = df_limpio['Diagnóstico_AgroLogica'].value_counts()
            
            # Configuramos los colores según la gravedad
            colores_map = {
                'Alta': '#28a745',          # Verde
                'Media': '#17a2b8',         # Azul claro
                'Baja': '#ffc107',          # Amarillo
                'Exceso': '#dc3545',        # Rojo
                'Riesgo Físico': '#6c757d', # Gris oscuro
                'Riesgo Ambiental': '#343a40' # Negro
            }
            colores = [colores_map.get(x, '#000000') for x in conteo_diagnostico.index]
            
            # Creamos la figura de Matplotlib
            fig, ax = plt.subplots(figsize=(7, 4))
            
            # Dibujamos el gráfico de pastel
            wedges, texts, autotexts = ax.pie(
                conteo_diagnostico, 
                labels=conteo_diagnostico.index, 
                autopct='%1.1f%%', 
                startangle=90, 
                colors=colores,
            )
            
            centro_circulo = plt.Circle((0,0), 0.70, fc='none')
            fig.gca().add_artist(centro_circulo)
            
            ax.axis('equal')  
            plt.setp(texts, size=10, color="#808080", weight="bold")
            plt.setp(autotexts, size=10, color="white", weight="bold")
            # Mostramos el gráfico en Streamlit
            col_espacio1, col_grafica, col_espacio2 = st.columns([1, 2, 1])
            
            with col_grafica:
                st.pyplot(fig, transparent=True, use_container_width=True)
            
            st.divider()
            # Descarga
            csv_export = df_limpio.to_csv(index=False).encode('utf-8')
            st.download_button(label="Descargar reporte de diagnóstico (.CSV)", data=csv_export, file_name="Reporte_AgroLogica_Resultados.csv", mime="text/csv", type="secondary")
        
# =====================================================================
# Pestaña 2: Diagnóstico manual
# =====================================================================
with tab2:
    st.header("Revisar un terreno paso a paso")
    
    st.subheader("1. ¿Cómo es el terreno y el clima?")
    col1, col2, col3, col4 = st.columns(4)
    with col1: cultivo_input = st.selectbox("Cultivo a sembrar:", ["Maíz", "Frijol", "Nopal", "Aguacate"])
    with col2: erosion_input = st.selectbox("Nivel de erosión:", ["Leve", "Moderada", "Severa"])
    with col3: pendiente_input = st.number_input("Pendiente (%):", 0.0, 90.0, 10.0, step=1.0)
    with col4: lluvia_input = st.number_input("Lluvia anual (mm):", 0.0, 3000.0, 750.0, step=10.0)

    st.divider()

    st.subheader("2. Resultados de tu estudio de tierra")
    col5, col6, col7, col8 = st.columns(4)
    with col5: ph_input = st.slider("Acidez (pH):", 0.0, 14.0, 6.5, step=0.1)
    with col6: n_input = st.number_input("Nitrógeno (mg/kg):", 0.0, 150.0, 30.0, step=1.0)
    with col7: p_input = st.number_input("Fósforo (mg/kg):", 0.0, 150.0, 15.0, step=1.0)
    with col8: k_input = st.number_input("Potasio (mg/kg):", 0.0, 300.0, 150.0, step=1.0)
    mo_input = st.number_input("Materia orgánica (%):", 0.0, 15.0, 3.0, step=0.1)
        
    st.markdown(" ")
    if st.button("Obtener consejos para mi tierra", type="primary", use_container_width=True):
        nivel, mensaje = diagnostico_preciso(ph_input, mo_input, n_input, p_input, k_input, pendiente_input, erosion_input, lluvia_input, cultivo_input)
        
        st.subheader("Lo que tu tierra necesita:")
        if nivel == "Alta": st.success(f"**Fertilidad alta:** {mensaje}")
        elif nivel == "Media": st.info(f"**Fertilidad media:** {mensaje}")
        elif nivel in ["Riesgo Físico", "Riesgo Ambiental"]: st.error(f"**Terreno no apto:** {mensaje}")
        elif nivel == "Exceso": st.error(f"**{mensaje}**")
        else: st.warning(f"**Atención requerida:** {mensaje}")
        
        # --- Gráfico comparativo de barras ---
        # Solo mostramos la gráfica química si el terreno pasó el filtro físico
        if nivel not in ["Riesgo físico", "Riesgo ambiental"]:
            st.markdown("### Comparativa: Tu suelo vs. Requerimiento ideal")
            
            # Diccionario base para extraer los ideales rápidamente
            ideales_grafica = {
                "maíz": {"n": 30.0, "p": 15.0, "k": 150.0},
                "frijol": {"n": 15.0, "p": 12.0, "k": 120.0},
                "nopal": {"n": 10.0, "p": 10.0, "k": 100.0},
                "aguacate": {"n": 20.0, "p": 20.0, "k": 150.0}
            }
            
            cultivo_key = cultivo_input.lower()
            if cultivo_key not in ideales_grafica: cultivo_key = "maíz"
            
            ideal_n = ideales_grafica[cultivo_key]["n"]
            ideal_p = ideales_grafica[cultivo_key]["p"]
            ideal_k = ideales_grafica[cultivo_key]["k"]
            
            # Datos para la gráfica
            etiquetas = ['Nitrógeno (N)', 'Fósforo (P)', 'Potasio (K)']
            valores_actuales = [n_input, p_input, k_input]
            valores_ideales = [ideal_n, ideal_p, ideal_k]
            
            x = np.arange(len(etiquetas))
            ancho_barra = 0.35
            
            fig2, ax2 = plt.subplots(figsize=(8, 4))
            barras_actuales = ax2.bar(x - ancho_barra/2, valores_actuales, ancho_barra, label='Tu Parcela', color='#17a2b8')
            barras_ideales = ax2.bar(x + ancho_barra/2, valores_ideales, ancho_barra, label=f'Ideal ({cultivo_input})', color='#28a745')
            
            # Definimos el color Gris Neutro para que funcione en Modo Claro y Oscuro
            color_texto = '#808080'
            
            # Aplicamos el color a todos los elementos del contorno
            ax2.set_ylabel('Concentración (mg/kg)', color=color_texto, weight='bold')
            ax2.set_title('Análisis de macronutrientes (NPK)', color=color_texto, weight='bold')
            ax2.set_xticks(x)
            ax2.set_xticklabels(etiquetas, color=color_texto, weight='bold')
            ax2.tick_params(axis='y', colors=color_texto)
            
            # Aplicamos el color al texto de la leyenda
            leyenda = ax2.legend()
            for text in leyenda.get_texts():
                text.set_color(color_texto)
                
            # Aplicamos el color a los bordes de la gráfica (las espinas)
            for spine in ax2.spines.values():
                spine.set_edgecolor(color_texto)
            
            # Añadimos los números encima de las barras también en gris
            ax2.bar_label(barras_actuales, padding=3, color=color_texto, weight='bold')
            ax2.bar_label(barras_ideales, padding=3, color=color_texto, weight='bold')
            
            fig2.tight_layout()
            
            # Renderizamos con fondo transparente
            col_izq, col_centro, col_der = st.columns([1, 2, 1])

            with col_centro:
                st.pyplot(fig2, use_container_width=True, transparent=True)
           
