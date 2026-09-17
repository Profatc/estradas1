import math
import numpy as np
import streamlit as st

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Cálculo de Lc - UNEMAT", layout="wide")

# --- 2. INTERFACE DO APLICATIVO ---
st.title("🛣️ Cálculo de Curva Transição de Rodovias - UNEMAT")
st.subheader("Prof. Arnaldo Taveira Chioveto")
st.divider()

# --- FUNÇÃO: TABELA DE RAMPAS DE SUPERELEVAÇÃO (DNER 1999, p. 107) ---
def obter_rmax(v: float):
    """
    Retorna r_máx em decimal e o denominador (1:X) com base na velocidade V (km/h).
    Realiza interpolação linear para velocidades intermediárias.
    """
    v_tab = [40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]
    den_tab = [137.0, 154.0, 169.0, 185.0, 200.0, 213.0, 233.0]
    
    denominador = float(np.interp(v, v_tab, den_tab))
    r_max = 1.0 / denominador
    return r_max, denominador

# --- 3. DADOS DE ENTRADA DA CURVA ---
st.sidebar.header("📐 Dados de Entrada da Curva")

v_diretriz = st.sidebar.number_input(
    "Velocidade Diretriz - V (km/h):", min_value=20.0, value=80.0, step=5.0
)
raio = st.sidebar.number_input(
    "Raio da Curva Circular - R (m):", min_value=10.0, value=250.0, step=10.0
)
largura_faixa = st.sidebar.number_input(
    "Largura da Faixa - LF (m):", min_value=2.0, value=3.60, step=0.10
)
e_r_pct = st.sidebar.number_input(
    "Superelevação - eR (%):", min_value=0.0, max_value=12.0, value=8.0, step=0.5
)
f_m = st.sidebar.number_input(
    "Fator Multiplicador - Fm:",
    min_value=0.5,
    value=1.0,
    step=0.1,
    help="Para pista simples de 2 faixas girando pelo eixo/greide, Fm = 1,0.",
)

# Cálculo automático de r_máx pela tabela do DNER
r_max_dec, den_rmax = obter_rmax(v_diretriz)

# Conversão da superelevação para decimal
e_r_dec = e_r_pct / 100.0

# --- 4. CRITÉRIOS DE COMPRIMENTO MÍNIMO (Lc_min) ---

# 4.1 Mínimo Absoluto
l_abs_calc = 0.56 * v_diretriz
l_min_abs = max(l_abs_calc, 30.0)

# 4.2 Fluência Ótica (apenas para R > 800m)
if raio > 800:
    l_min_otica = (1 / 9) * raio
    status_otica = "Aplicado"
else:
    l_min_otica = 0.0
    status_otica = "Não aplicável (R ≤ 800m)"

# 4.3 Conforto Centrífugo
c_taxa = 1.5 - (0.009 * v_diretriz)
l_min_conforto = (v_diretriz**3 / (46.656 * c_taxa * raio)) - ((e_r_dec * v_diretriz) / (0.367 * c_taxa))
l_min_conforto = max(l_min_conforto, 0.0)

# 4.4 Máxima Rampa de Superelevação
l_min_rampa = (f_m * largura_faixa * e_r_dec) / r_max_dec

# Governante Mínimo Exato e Arredondado (para cima em múltiplos de 10m)
lc_min_governante = max(l_min_abs, l_min_otica, l_min_conforto, l_min_rampa)
lc_min_arred = math.ceil(lc_min_governante / 10.0) * 10.0

# --- 5. CRITÉRIOS DE COMPRIMENTO MÁXIMO (Lc_max) ---

# 5.1 Máximo Ângulo Central (θs ≤ 0.5 rad / Lc ≤ R)
l_max_angulo = raio

# 5.2 Tempo de Percurso (máx 8 segundos em V)
l_max_tempo = 2.2 * v_diretriz

# Governante Máximo Exato e Arredondado (para baixo em múltiplos de 10m)
lc_max_calculado = min(l_max_angulo, l_max_tempo)
lc_max_arred = math.floor(lc_max_calculado / 10.0) * 10.0

# --- 6. FORMULÁRIOS DE VALIDAÇÃO (SEPARADOS) ---
st.subheader("✍️ Validação dos Cálculos do Aluno")
st.write("Insira os valores calculados nos formulários abaixo e clique no botão de cada critério para verificar:")

col_left, col_right = st.columns(2)

# --- BLOCO Lc,min ---
with col_left:
    with st.form(key="form_min"):
        st.markdown("### 📉 **Critérios de Mínimo ($L_{c,min}$)**")
        user_l_abs = st.number_input(
            "1. Mínimo Absoluto (m):",
            min_value=0.0, value=0.0, step=0.01, format="%.2f",
            help="Tolerância de erro: máx ±0,05 m (5 cm)"
        )
        user_l_otica = st.number_input(
            "2. Fluência Ótica (m):",
            min_value=0.0, value=0.0, step=0.01, format="%.2f",
            help="Informe 0,00 se R ≤ 800m. Tolerância de erro: máx ±0,05 m (5 cm)"
        )
        user_l_conforto = st.number_input(
            "3. Conforto Centrífugo (m):",
            min_value=0.0, value=0.0, step=0.01, format="%.2f",
            help="Tolerância de erro: máx ±0,05 m (5 cm)"
        )
        user_l_rampa = st.number_input(
            "4. Máxima Rampa de Superelevação (m):",
            min_value=0.0, value=0.0, step=0.01, format="%.2f",
            help="Tolerância de erro: máx ±0,05 m (5 cm)"
        )
        user_lc_min_adotado = st.number_input(
            "🎯 Lc,min Final na Faixa (múltiplo de 10m):",
            min_value=0.0, value=0.0, step=10.0, format="%.2f",
            help="Tolerância de erro: máx ±0,05 m (5 cm)"
        )

        btn_min = st.form_submit_button("🔍 Verificar Lc,min", type="primary")

    if btn_min:
        # Estrutura das checagens: (valor_usuario, valor_esperado, nome_criterio, tolerancia)
        checagens_min = [
            (user_l_abs, l_min_abs, "Mínimo Absoluto", 0.05),
            (user_l_otica, l_min_otica, "Fluência Ótica", 0.05),
            (user_l_conforto, l_min_conforto, "Conforto Centrífugo", 0.05),
            (user_l_rampa, l_min_rampa, "Máxima Rampa de Superelevação", 0.05),
            (user_lc_min_adotado, lc_min_arred, "Lc,min Final da Faixa (múltiplo de 10m)", 0.05)
        ]
        
        erros_min = [
            f"• **{nome}**: inserido {val_user:.2f} m (Tolerância permitida: ±{tol:.2f} m)."
            for val_user, val_esp, nome, tol in checagens_min
            if abs(val_user - val_esp) > tol
        ]

        if erros_min:
            st.error(
                "⚠️ **Atenção aos erros em $L_{c,min}$:**\n\n"
                + "\n".join(erros_min)
                + "\n\nPor favor, reveja os cálculos apontados."
            )
        else:
            st.success("✅ **Cálculos de $L_{c,min}$ corretos!**")
            st.write(f"* **Mínimo Absoluto:** {l_min_abs:.2f} m _(tol: ±0,05 m)_")
            st.write(f"* **Fluência Ótica:** {l_min_otica:.2f} m _({status_otica} | tol: ±0,05 m)_")
            st.write(f"* **Conforto Centrífugo (C={c_taxa:.3f}):** {l_min_conforto:.2f} m _(tol: ±0,05 m)_")
            st.write(f"* **Máxima Rampa de Superelevação ($1:{den_rmax:.1f}$):** {l_min_rampa:.2f} m _(tol: ±0,05 m)_")
            st.info(f"▶ **Mínimo Exato:** {lc_min_governante:.2f} m | **Adotado:** {lc_min_arred:.0f} m")

# --- BLOCO Lc,max ---
with col_right:
    with st.form(key="form_max"):
        st.markdown("### 📈 **Critérios de Máximo ($L_{c,max}$)**")
        user_l_angulo = st.number_input(
            "1. Máximo Ângulo Central (m):",
            min_value=0.0, value=0.0, step=0.01, format="%.2f",
            help="Tolerância de erro: máx ±0,05 m (5 cm)"
        )
        user_l_tempo = st.number_input(
            "2. Tempo de Percurso (m):",
            min_value=0.0, value=0.0, step=0.01, format="%.2f",
            help="Tolerância de erro: máx ±0,50 m (0,5 m)"
        )
        user_lc_max_adotado = st.number_input(
            "🎯 Lc,max Final na Faixa (múltiplo de 10m):",
            min_value=0.0, value=0.0, step=10.0, format="%.2f",
            help="Tolerância de erro: máx ±0,05 m (5 cm)"
        )

        btn_max = st.form_submit_button("🔍 Verificar Lc,max", type="primary")

    if btn_max:
        # Estrutura das checagens: (valor_usuario, valor_esperado, nome_criterio, tolerancia)
        checagens_max = [
            (user_l_angulo, l_max_angulo, "Máximo Ângulo Central", 0.05),
            (user_l_tempo, l_max_tempo, "Tempo de Percurso", 0.50),
            (user_lc_max_adotado, lc_max_arred, "Lc,max Final da Faixa (múltiplo de 10m)", 0.05)
        ]

        erros_max = [
            f"• **{nome}**: inserido {val_user:.2f} m (Tolerância permitida: ±{tol:.2f} m)."
            for val_user, val_esp, nome, tol in checagens_max
            if abs(val_user - val_esp) > tol
        ]

        if erros_max:
            st.error(
                "⚠️ **Atenção aos erros em $L_{c,max}$:**\n\n"
                + "\n".join(erros_max)
                + "\n\nPor favor, reveja os cálculos apontados."
            )
        else:
            st.success("✅ **Cálculos de $L_{c,max}$ corretos!**")
            st.write(f"* **Máximo Ângulo Central ($L_c = R$):** {l_max_angulo:.2f} m _(tol: ±0,05 m)_")
            st.write(f"* **Tempo de Percurso ($2,2 \\cdot V$):** {l_max_tempo:.2f} m _(tol: ±0,50 m)_")
            st.info(f"▶ **Máximo Exato:** {lc_max_calculado:.2f} m | **Adotado:** {lc_max_arred:.0f} m")