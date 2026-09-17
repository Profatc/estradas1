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
    "Velocidade Diretriz - V (km/h):", min_value=0.0, value=0.0, step=5.0
)
raio = st.sidebar.number_input(
    "Raio da Curva Circular - R (m):", min_value=0.0, value=0.0, step=10.0
)
largura_faixa = st.sidebar.number_input(
    "Largura da Faixa - LF (m):", min_value=0.0, value=0.0, step=0.10
)
e_r_pct = st.sidebar.number_input(
    "Superelevação - eR (%):", min_value=0.0, max_value=12.0, value=0.0, step=0.5
)
f_m = st.sidebar.number_input(
    "Fator Multiplicador - Fm:",
    min_value=0.0,
    value=0.0,
    step=0.1,
    help="Para pista simples de 2 faixas girando pelo eixo/greide, Fm = 1,0.",
)

# Validação do preenchimento dos parâmetros de entrada
dados_entrada_validos = all([v_diretriz > 0, raio > 0, largura_faixa > 0, e_r_pct > 0, f_m > 0])

# --- 4. LANÇAMENTO DOS DADOS DO ALUNO (COLUNAS FIXAS) ---
st.subheader("✍️ Lançamento dos Cálculos do Aluno")

col_left, col_right = st.columns(2)

with col_left:
    st.markdown("### 📉 **Critérios de Mínimo ($L_{c,min}$)**")
    user_l_abs = st.number_input("1. Mínimo Absoluto (m):", min_value=0.0, value=0.0, step=0.01, format="%.2f", help="Tolerância de erro: máx ±0,05 m (5 cm)", key="user_l_abs")
    user_l_otica = st.number_input("2. Fluência Ótica (m):", min_value=0.0, value=0.0, step=0.01, format="%.2f", help="Informe 0,00 se R ≤ 800m. Tolerância de erro: máx ±0,05 m (5 cm)", key="user_l_otica")
    user_l_conforto = st.number_input("3. Conforto Centrífugo (m):", min_value=0.0, value=0.0, step=0.01, format="%.2f", help="Tolerância de erro: máx ±0,05 m (5 cm)", key="user_l_conforto")
    user_l_rampa = st.number_input("4. Máxima Rampa de Superelevação (m):", min_value=0.0, value=0.0, step=0.01, format="%.2f", help="Tolerância de erro: máx ±0,05 m (5 cm)", key="user_l_rampa")
    user_lc_min_adotado = st.number_input("🎯 Lc,min Final na Faixa (múltiplo de 10m):", min_value=0.0, value=0.0, step=10.0, format="%.2f", help="Tolerância de erro: máx ±0,05 m (5 cm)", key="user_lc_min_adotado")

with col_right:
    st.markdown("### 📈 **Critérios de Máximo ($L_{c,max}$)**")
    user_l_angulo = st.number_input("1. Máximo Ângulo Central (m):", min_value=0.0, value=0.0, step=0.01, format="%.2f", help="Tolerância de erro: máx ±0,05 m (5 cm)", key="user_l_angulo")
    user_l_tempo = st.number_input("2. Tempo de Percurso (m):", min_value=0.0, value=0.0, step=0.01, format="%.2f", help="Tolerância de erro: máx ±0,50 m (0,5 m)", key="user_l_tempo")
    user_lc_max_adotado = st.number_input("🎯 Lc,max Final na Faixa (múltiplo de 10m):", min_value=0.0, value=0.0, step=10.0, format="%.2f", help="Tolerância de erro: máx ±0,05 m (5 cm)", key="user_lc_max_adotado")

# --- 5. BOTÃO DE CÁLCULO E MEMÓRIA DE ESTADO ---
st.divider()

if "calcular_executado" not in st.session_state:
    st.session_state.calcular_executado = False

if st.button("🔍 Verificar Cálculos", type="primary", use_container_width=True):
    st.session_state.calcular_executado = True

# --- 6. EXIBIÇÃO DOS RESULTADOS ---
if st.session_state.calcular_executado:
    st.subheader("🔍 Resultado da Verificação")
    
    if not dados_entrada_validos:
        st.warning("⚠️ **Atenção:** Preencha todos os **Dados de Entrada da Curva** na barra lateral com valores maiores que zero para realizar a verificação.")
    else:
        # Cálculo dos parâmetros com dados de entrada válidos (> 0)
        r_max_dec, den_rmax = obter_rmax(v_diretriz)
        e_r_dec = e_r_pct / 100.0

        # Critérios de Mínimo
        l_abs_calc = 0.56 * v_diretriz
        l_min_abs = max(l_abs_calc, 30.0)

        if raio > 800:
            l_min_otica = (1 / 9) * raio
            status_otica = "Aplicado"
        else:
            l_min_otica = 0.0
            status_otica = "Não aplicável (R ≤ 800m)"

        c_taxa = 1.5 - (0.009 * v_diretriz)
        l_min_conforto = (v_diretriz**3 / (46.656 * c_taxa * raio)) - ((e_r_dec * v_diretriz) / (0.367 * c_taxa))
        l_min_conforto = max(l_min_conforto, 0.0)

        l_min_rampa = (f_m * largura_faixa * e_r_dec) / r_max_dec
        lc_min_governante = max(l_min_abs, l_min_otica, l_min_conforto, l_min_rampa)
        lc_min_arred = math.ceil(lc_min_governante / 10.0) * 10.0

        # Critérios de Máximo
        l_max_angulo = raio
        l_max_tempo = 2.2 * v_diretriz
        lc_max_calculado = min(l_max_angulo, l_max_tempo)
        lc_max_arred = math.floor(lc_max_calculado / 10.0) * 10.0

        # Validação do preenchimento dos campos do aluno para o Critério Mínimo (Fluência Ótica pode ser 0)
        tem_dados_min = all([
            user_l_abs > 0,
            user_l_conforto > 0,
            user_l_rampa > 0,
            user_lc_min_adotado > 0
        ])

        # Validação do preenchimento dos campos do aluno para o Critério Máximo
        tem_dados_max = all([
            user_l_angulo > 0,
            user_l_tempo > 0,
            user_lc_max_adotado > 0
        ])

        # Funções de verificação dos valores inseridos pelo aluno
        def verificar_lc_min():
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

        def verificar_lc_max():
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

        # Exibição nas colunas
        res_left, res_right = st.columns(2)
        with res_left:
            if tem_dados_min:
                verificar_lc_min()
            else:
                st.warning("⚠️ **Critério Mínimo Incompleto:** Preencha todos os campos do $L_{c,min}$ (valores > 0, exceto Fluência Ótica).")

        with res_right:
            if tem_dados_max:
                verificar_lc_max()
            else:
                st.warning("⚠️ **Critério Máximo Incompleto:** Preencha todos os campos do $L_{c,max}$ com valores maiores que zero.")

        val_faixa_min = user_lc_min_adotado if user_lc_min_adotado > 0 else lc_min_arred
        val_faixa_max = user_lc_max_adotado if user_lc_max_adotado > 0 else lc_max_arred

        st.write("")

        # Exibição condicional da Faixa Admissível
        if tem_dados_min and tem_dados_max:
            st.markdown("### 🎯 **Faixa Admissível (Múltiplos de 10m)**")
            st.success(f"**Comprimentos de transição:** {val_faixa_min:.0f} m $\\le L_c \\le$ {val_faixa_max:.0f} m")

        elif tem_dados_min:
            st.markdown("### 🎯 **Faixa Admissível (Múltiplos de 10m)**")
            st.success(f"**Comprimento mínimo de transição:** $L_c \\ge$ {val_faixa_min:.0f} m")

        elif tem_dados_max:
            st.markdown("### 🎯 **Faixa Admissível (Múltiplos de 10m)**")
            st.success(f"**Comprimento máximo de transição:** $L_c \\le$ {val_faixa_max:.0f} m")