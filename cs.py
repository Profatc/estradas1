import math
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st


# --- 1. FUNÇÕES AUXILIARES ---
def formatar_estaca(distancia_m):
  if distancia_m < 0:
    return "0 + 0,000 m"
  num_estaca = int(distancia_m // 20)
  fracao = distancia_m % 20
  return f"Estaca {num_estaca} + {fracao:.3f} m"


def deg_para_dms(deg):
  d = int(deg)
  m_full = (deg - d) * 60
  m = int(m_full)
  s = round((m_full - m) * 60)
  if s == 60:
    s = 0
    m += 1
  if m == 60:
    m = 0
    d += 1
  return f"{d}° {m:02d}' {s:02d}\""


# --- 2. INTERFACE DO APLICATIVO ---
st.title("🛣️ Cálculo de Curvas Simples de Rodovias - UNEMAT")
st.subheader("Prof. Arnaldo Taveira Chioveto")
st.divider()

st.header("📐 1. Dados de Entrada da Curva")

# Entrada do Raio
raio = st.number_input(
    "Raio da curva - R (m):",
    min_value=1.0,
    value=200.0,
    step=10.0,
    format="%.3f",
)

# Entrada do Ângulo de Deflexão em Graus, Minutos e Segundos
st.write("**Ângulo de Deflexão (Δ):**")
col_d, col_m, col_s = st.columns(3)
with col_d:
  delta_deg = st.number_input(
      "Graus (°)", min_value=0, max_value=180, value=24, step=1
  )
with col_m:
  delta_min = st.number_input(
      "Minutos (')", min_value=0, max_value=59, value=12, step=1
  )
with col_s:
  delta_sec = st.number_input(
      'Segundos (")', min_value=0, max_value=59, value=40, step=1
  )

# Conversão do Δ informado em DMS para Graus Decimais
deflexao = delta_deg + (delta_min / 60.0) + (delta_sec / 3600.0)

# Entrada do Estaqueamento do PI
st.subheader("📌 Estaqueamento do PI (Ponto de Interseção)")
col3, col4 = st.columns(2)
with col3:
  estaca_pi_num = st.number_input(
      "Número da Estaca do PI:", min_value=0, value=6, step=1
  )
with col4:
  estaca_pi_frac = st.number_input(
      "Fração da Estaca do PI (m):",
      min_value=0.0,
      max_value=19.999,
      value=13.970,
      step=0.001,
      format="%.3f",
  )

# Seleção da Corda de Locação
st.subheader("📏 Parâmetros de Locação Topográfica")
intervalo_corda = st.selectbox(
    "Tamanho da corda para locação na curva:",
    options=[20.0, 10.0, 5.0],
    index=0,
    format_func=lambda x: f"{int(x)} metros",
)

st.divider()

# --- 3. VALIDAÇÃO DOS CÁLCULOS DO USUÁRIO ---
st.header("✍️ 2. Insira os Seus Resultados para Validação")
st.info(
    "💡 Para visualizar o gabarito completo, desenho e a tabela de locação, "
    "insira os resultados que você calculou. A tolerância de erro máxima "
    "permitida no comprimento é de **0,050 m (5 cm)**."
)

col_u1, col_u2, col_u3 = st.columns(3)
with col_u1:
  user_t = st.number_input(
      "Tangente Externa - T (m):",
      min_value=0.0,
      value=0.0,
      step=0.001,
      format="%.3f",
  )
with col_u2:
  user_d = st.number_input(
      "Desenvolvimento - D (m):",
      min_value=0.0,
      value=0.0,
      step=0.001,
      format="%.3f",
  )
with col_u3:
  user_e = st.number_input(
      "Afastamento - E (m):",
      min_value=0.0,
      value=0.0,
      step=0.001,
      format="%.3f",
  )

col_u4, col_u5 = st.columns(2)
with col_u4:
  user_pc = st.number_input(
      "Estaca do PC (em metros totais):",
      min_value=0.0,
      value=0.0,
      step=0.001,
      format="%.3f",
      help="Exemplo: Estaca 4 + 11,400m = 4*20 + 11.400 = 91.400m",
  )
with col_u5:
  user_pt = st.number_input(
      "Estaca do PT (em metros totais):",
      min_value=0.0,
      value=0.0,
      step=0.001,
      format="%.3f",
      help="Exemplo: Estaca 8 + 16,070m = 8*20 + 16.070 = 176.070m",
  )

st.divider()

# --- 4. PROCESSAMENTO E COMPARAÇÃO ---
if st.button("🔍 Verificar Cálculos e Validar Resultados"):
  if deflexao <= 0:
    st.error("O ângulo de deflexão (Δ) deve ser maior que zero!")
  else:
    # --- VALIDAÇÃO DA CORDA DA CURVA (NORMA DNER/DNIT) ---
    if raio < 100.0:
      corda_permitida = 5.0
    elif raio <= 600.0:
      corda_permitida = 10.0
    else:
      corda_permitida = 20.0

    if intervalo_corda != corda_permitida:
      st.warning(
          "⚠️ **Atenção:** Ver manual de projeto de engenharia rodoviária "
          "(DNER, 1974, v. 3, cap. 9, p. 4)"
      )
    else:
      # Cálculos Geométricos Exatos
      delta_rad = math.radians(deflexao)
      tangente = raio * math.tan(delta_rad / 2)
      desenvolvimento = (math.pi * raio * deflexao) / 180
      afastamento = raio * (1 / math.cos(delta_rad / 2) - 1)
      deflexao_metro_deg = math.degrees(1.0 / (2.0 * raio))
      deflexao_corda_deg = math.degrees(intervalo_corda / (2.0 * raio))

      # Cálculos de Estaqueamento (1 estaca = 20 metros)
      pi_m = (estaca_pi_num * 20) + estaca_pi_frac
      pc_m = pi_m - tangente
      pt_m = pc_m + desenvolvimento

      # Comparação entre o calculado pelo código e o inserido pelo usuário
      metricas = [
          ("Tangente Externa (T)", tangente, user_t),
          ("Desenvolvimento (D)", desenvolvimento, user_d),
          ("Afastamento (E)", afastamento, user_e),
          ("Estaca do PC (m)", pc_m, user_pc),
          ("Estaca do PT (m)", pt_m, user_pt),
      ]

      tabela_comparacao = []
      todos_dentro_da_margem = True

      # Tolerância máxima de 5 cm = 0,050 m
      TOLERANCIA_MAX_M = 0.050

      for nome, calc, user in metricas:
        dif_m = abs(calc - user)
        dentro_margem = dif_m <= TOLERANCIA_MAX_M

        if not dentro_margem:
          todos_dentro_da_margem = False

        # Mostra o valor calculado apenas se estiver dentro da tolerância
        val_calculado_exibicao = (
            f"{calc:.3f} m"
            if dentro_margem
            else "🔒 Oculto (Fora da tolerância)"
        )

        tabela_comparacao.append({
            "Parâmetro": nome,
            "Valor Calculado": val_calculado_exibicao,
            "Seu Valor Inserido": f"{user:.3f} m",
            "Diferença (m)": f"{dif_m:.3f} m",
            "Status (Tolerância ≤ 0,050 m)": (
                "✅ Aprovado" if dentro_margem else "❌ Reprovado (> 0,050 m)"
            ),
        })

      # Exibição da Tabela de Comparação
      st.subheader("📊 Comparação dos Resultados")
      st.dataframe(tabela_comparacao, use_container_width=True)

      # --- VERIFICAÇÃO DA TOLERÂNCIA DE ERRO ---
      if not todos_dentro_da_margem:
        st.error(
            "❌ **Cálculos não validados!** Um ou mais valores inseridos "
            "apresentam diferença superior a **0,050 m (5 cm)** em relação ao"
            " valor exato.\n\n"
            "Revise seus cálculos e tente novamente para liberar a resolução"
            " completa e o gráfico."
        )
      else:
        st.success(
            "🎉 **Parabéns!** Todos os seus resultados estão dentro da"
            " tolerância de erro de **0,050 m (5 cm)**. A resolução completa foi"
            " liberada abaixo:"
        )

        st.divider()

        # Resultados Geométricos (Ordem Solicitada)
        st.subheader("📊 Resultados Geométricos Oficiais")
        st.write(
            f"🔹 **Ângulo de Deflexão (Δ):** `{deg_para_dms(deflexao)}`"
            f" ({deflexao:.4f}°)"
        )
        st.write(f"🔹 **Tangente Externa (T):** `{tangente:.3f} m`")
        st.write(f"🔹 **Desenvolvimento (D):** `{desenvolvimento:.3f} m`")
        st.write(f"🔹 **Afastamento (E):** `{afastamento:.3f} m`")
        st.write(
            f"🔹 **Deflexão da Corda (DC - {int(intervalo_corda)}m):**"
            f" `{deg_para_dms(deflexao_corda_deg)}` ({deflexao_corda_deg:.6f}°)"
        )
        st.write(
            f"🔹 **Deflexão por Metro (dm):**"
            f" `{deg_para_dms(deflexao_metro_deg)}/m` ({deflexao_metro_deg:.6f}°/m)"
        )

        st.divider()

        # Estaqueamento
        st.subheader("📍 Estaqueamento dos Pontos Notáveis")
        st.write(
            f"🔴 **Estaca do PC:** `{formatar_estaca(pc_m)}` ({pc_m:.3f} m)"
        )
        st.write(
            f"🟡 **Estaca do PI:** `{formatar_estaca(pi_m)}` ({pi_m:.3f} m)"
        )
        st.write(
            f"🟢 **Estaca do PT:** `{formatar_estaca(pt_m)}` ({pt_m:.3f} m)"
        )

        st.divider()
        st.subheader("📈 Desenho Esquemático da Curva")

        # Coordenadas do Gráfico
        pc_x, pc_y = 0.0, 0.0
        pi_x, pi_y = tangente, 0.0
        pt_x = raio * math.sin(delta_rad)
        pt_y = raio * (1 - math.cos(delta_rad))

        phi = np.linspace(0, delta_rad, 100)
        arco_x = raio * np.sin(phi)
        arco_y = raio * (1 - np.cos(phi))

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(
            [pc_x, pi_x],
            [pc_y, pi_y],
            "k--",
            label="Tangentes (Diretrizes)",
            linewidth=1.5,
        )
        ax.plot([pi_x, pt_x], [pi_y, pt_y], "k--", linewidth=1.5)
        ax.plot(
            arco_x,
            arco_y,
            "r-",
            label="Arco da Curva (Desenvolvimento)",
            linewidth=2.5,
        )
        ax.scatter(
            [pc_x, pi_x, pt_x], [pc_y, pi_y, pt_y], color="blue", zorder=5
        )

        ax.text(
            pc_x,
            pc_y,
            f" PC ({formatar_estaca(pc_m)})  ",
            fontsize=8,
            fontweight="bold",
            horizontalalignment="right",
        )
        ax.text(
            pi_x,
            pi_y,
            f" PI ({formatar_estaca(pi_m)})",
            fontsize=8,
            fontweight="bold",
            verticalalignment="top",
        )
        ax.text(
            pt_x,
            pt_y,
            f"  PT ({formatar_estaca(pt_m)})",
            fontsize=8,
            fontweight="bold",
            horizontalalignment="left",
        )

        ax.set_aspect("equal", adjustable="datalim")
        ax.set_xlabel("Eixo X (m)")
        ax.set_ylabel("Eixo Y (m)")
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.legend()

        st.pyplot(fig)

        # --- TABELA DE LOCAÇÃO DA CURVA POR DEFLEXÕES ---
        st.divider()
        st.subheader(
            "📋 Tabela de Locação da Curva em Estacas Inteiras (Cordas de"
            f" {int(intervalo_corda)}m)"
        )

        intervalo = intervalo_corda
        lista_pontos_m = [pc_m]

        proxima_estaca = math.ceil(pc_m / intervalo) * intervalo
        if abs(proxima_estaca - pc_m) < 1e-4:
          proxima_estaca += intervalo

        curr = proxima_estaca
        while curr < pt_m:
          lista_pontos_m.append(curr)
          curr += intervalo
        lista_pontos_m.append(pt_m)

        tabela_locacao = []
        prev_dist = 0.0

        for m in lista_pontos_m:
          dist_pc = m - pc_m
          corda_parcial = dist_pc - prev_dist

          deflexao_acum_deg = math.degrees(dist_pc / (2 * raio))
          deflexao_parcial_deg = math.degrees(corda_parcial / (2 * raio))

          if abs(m - pc_m) < 1e-4:
            label = "PC"
          elif abs(m - pt_m) < 1e-4:
            label = "PT"
          else:
            num_est = int(m // 20)
            frac_est = m % 20
            if abs(frac_est) < 1e-4:
              label = f"Estaca {num_est}"
            else:
              label = f"Estaca {num_est}+{frac_est:.3f}m"

          tabela_locacao.append({
              "Ponto": label,
              "Estaca": formatar_estaca(m),
              "Subcorda / Corda (m)": f"{corda_parcial:.3f}",
              "Distância ao PC (m)": f"{dist_pc:.3f}",
              "Deflexão Parcial": deg_para_dms(deflexao_parcial_deg),
              "Deflexão Acumulada": deg_para_dms(deflexao_acum_deg),
          })
          prev_dist = dist_pc

        st.dataframe(tabela_locacao, use_container_width=True)