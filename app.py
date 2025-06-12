import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# Configuración de la página
st.set_page_config(
    page_title="Visualizador de Deformación del Espacio-Tiempo",
    layout="wide"
)

def espacio_tiempo_deformado_logaritmico(masa):
    """
    Calcula la deformación del espacio-tiempo causada por una masa
    utilizando una aproximación simplificada y escala logarítmica.
    
    Args:
        masa (float): Masa del cuerpo en kilogramos
    
    Returns:
        tuple: Coordenadas X, Y y curvatura Z normalizadas
    """
    G = 6.67430e-11  # Constante gravitacional
    
    # Crear la malla de coordenadas
    x = np.linspace(-50, 50, 100)
    y = np.linspace(-50, 50, 100)
    X, Y = np.meshgrid(x, y)
    
    # Calcular distancia radial (agregando pequeño valor para evitar división por cero)
    R = np.sqrt(X**2 + Y**2) + 1e-10
    
    # Calcular la curvatura usando aproximación newtoniana
    Z = -(G * masa) / R
    
    # Transformar a escala logarítmica para mejor visualización
    Z_log = np.log(np.abs(Z) + 1e-10)
    
    # Normalización de los datos
    Z_log_normalized = Z_log - np.min(Z_log)  # Restar valor mínimo
    if np.max(Z_log_normalized) > 0:
        Z_log_normalized /= np.max(Z_log_normalized)  # Escalar de 0 a 1
    
    # Enfatizar la curvatura basada en la masa
    Z_log_normalized *= (masa / 1e30)
    
    return X, Y, Z_log_normalized

def crear_grafico_3d(masa):
    """
    Crea un gráfico 3D interactivo de la deformación del espacio-tiempo.
    
    Args:
        masa (float): Masa del cuerpo en kilogramos
    
    Returns:
        plotly.graph_objects.Figure: Figura 3D de Plotly
    """
    # Obtener coordenadas de la curvatura
    X, Y, Z_log = espacio_tiempo_deformado_logaritmico(masa)
    
    # Crear el gráfico 3D con Plotly
    fig = go.Figure(data=[go.Surface(
        x=X,
        y=Y,
        z=Z_log,
        colorscale='Viridis',
        opacity=0.8,
        colorbar=dict(
            title=dict(text="Curvatura (log)"),
            thickness=15,
            len=0.5
        )
    )])
    
    # Configurar el layout del gráfico
    fig.update_layout(
        title=f'Deformación del Espacio-Tiempo<br>Masa: {masa:.2e} kg',
        scene=dict(
            xaxis_title='X (km)',
            yaxis_title='Y (km)',
            zaxis_title='Curvatura (log)',
            xaxis=dict(range=[-50, 50]),
            yaxis=dict(range=[-50, 50]),
            zaxis=dict(range=[-1, 1]),
            camera=dict(
                eye=dict(x=1.2, y=1.2, z=0.8)
            ),
            aspectmode='cube'
        ),
        width=800,
        height=600,
        margin=dict(l=0, r=0, t=50, b=0)
    )
    
    return fig

def validar_masa(masa_str):
    """
    Valida y convierte la entrada de masa a float.
    
    Args:
        masa_str (str): Valor de masa como string
    
    Returns:
        tuple: (is_valid, masa_float, mensaje_error)
    """
    try:
        masa = float(masa_str)
        if masa <= 0:
            return False, None, "La masa debe ser un valor positivo mayor que cero."
        if masa > 1e50:
            return False, None, "La masa es demasiado grande. Por favor, ingrese un valor menor."
        return True, masa, ""
    except ValueError:
        return False, None, "Por favor, ingrese un número válido."

# Interfaz principal de la aplicación
def main():
    # Título y descripción
    st.title("Visualizador de Deformación del Espacio-Tiempo")
    
    st.markdown("""
    Esta aplicación visualiza cómo una masa deforma el espacio-tiempo según la teoría de la relatividad general.
    La visualización utiliza una aproximación simplificada y escala logarítmica para mejor comprensión.
    """)
    
    # Crear dos columnas para el layout
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Parámetros")
        
        # Campo de entrada para la masa
        masa_input = st.text_input(
            "Masa del cuerpo (kg):",
            value="5.972e24",
            help="Ingrese la masa en kilogramos. Ejemplo: 5.972e24 (masa de la Tierra)"
        )
        
        # Ejemplos predefinidos
        st.subheader("Ejemplos comunes:")
        ejemplos = {
            "Sol": 1.989e30,
            "Tierra": 5.972e24,
            "Luna": 7.342e22,
            "Júpiter": 1.898e27,
            "Agujero Negro Estelar": 2e31
        }
        
        ejemplo_seleccionado = st.selectbox(
            "Seleccionar ejemplo:",
            ["Personalizado"] + list(ejemplos.keys())
        )
        
        if ejemplo_seleccionado != "Personalizado":
            masa_input = str(ejemplos[ejemplo_seleccionado])
            st.info(f"Masa seleccionada: {ejemplos[ejemplo_seleccionado]:.2e} kg")
        
        # Botón para generar visualización
        generar = st.button("Generar Visualización", type="primary")
    
    with col2:
        st.subheader("Visualización 3D")
        
        # Validar entrada y mostrar gráfico
        is_valid, masa, error_msg = validar_masa(masa_input)
        
        if generar or (is_valid and masa):
            if is_valid:
                try:
                    with st.spinner("Generando visualización..."):
                        fig = crear_grafico_3d(masa)
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Información adicional
                    st.info(f"""
                    **Información de la simulación:**
                    - Masa: {masa:.2e} kg
                    - Rango espacial: -50 km a +50 km
                    - Resolución: 100x100 puntos
                    - Escala: Logarítmica normalizada
                    """)
                    
                except Exception as e:
                    st.error(f"Error al generar la visualización: {str(e)}")
            else:
                st.error(error_msg)
        else:
            # Mostrar gráfico por defecto con masa de la Tierra
            if not generar:
                try:
                    default_mass = 5.972e24
                    fig = crear_grafico_3d(default_mass)
                    st.plotly_chart(fig, use_container_width=True)
                    st.info("Visualización por defecto: Masa de la Tierra (5.972×10²⁴ kg)")
                except Exception as e:
                    st.error(f"Error al mostrar visualización por defecto: {str(e)}")
    
    # Información educativa
    st.markdown("---")
    st.subheader("Información Científica")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("""
        **Conceptos Clave:**
        - **Curvatura del espacio-tiempo**: Las masas deforman la geometría del espacio-tiempo
        - **Constante gravitacional (G)**: 6.674×10⁻¹¹ m³/(kg·s²)
        - **Escala logarítmica**: Permite visualizar rangos amplios de valores
        - **Aproximación newtoniana**: Simplificación para fines educativos
        """)
    
    with col4:
        st.markdown("""
        **Masas de Referencia:**
        - **Sol**: 1.989×10³⁰ kg
        - **Tierra**: 5.972×10²⁴ kg
        - **Luna**: 7.342×10²² kg
        - **Júpiter**: 1.898×10²⁷ kg
        - **Agujero Negro típico**: ~2×10³¹ kg
        """)
    
    st.markdown("""
    ---
    *Nota: Esta visualización utiliza una aproximación simplificada de la relatividad general 
    para fines educativos. La deformación real del espacio-tiempo es más compleja.*
    """)

if __name__ == "__main__":
    main()
