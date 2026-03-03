/**
 * EduPrompt — Frontend Application
 * Autor: Leonardo Gonçalves Sobral
 */

const API_BASE = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
  ? `http://${window.location.hostname}:5001`
  : "";

const state = {
  perfis: [],
  versaoPrompt: "v1",
  gerando: false
};

// ─── Utilitários ───

function $(sel) { return document.querySelector(sel); }
function $$(sel) { return document.querySelectorAll(sel); }

function toast(msg, tipo = "info") {
  const container = $("#toastContainer");
  const el = document.createElement("div");
  el.className = `toast toast-${tipo}`;
  el.textContent = msg;
  container.appendChild(el);
  setTimeout(() => { el.classList.add("toast-exit"); }, 3000);
  setTimeout(() => { el.remove(); }, 3400);
}

function renderMarkdown(text) {
  if (typeof marked !== "undefined") {
    return marked.parse(text);
  }
  return text.replace(/\n/g, "<br>");
}

async function api(endpoint, opts = {}) {
  const url = `${API_BASE}${endpoint}`;
  const config = { headers: { "Content-Type": "application/json" }, ...opts };
  const res = await fetch(url, config);
  const data = await res.json();
  if (!data.sucesso) throw new Error(data.erro || "Erro desconhecido");
  return data;
}

// ─── Navbar ───

function initNavbar() {
  const navbar = $("#navbar");
  window.addEventListener("scroll", () => {
    navbar.classList.toggle("scrolled", window.scrollY > 50);
  });

  $$(".navbar-nav a").forEach(link => {
    link.addEventListener("click", () => {
      $$(".navbar-nav a").forEach(l => l.classList.remove("active"));
      link.classList.add("active");
    });
  });
}

// ─── Perfis (Gerador) ───

async function carregarPerfis() {
  try {
    const data = await api("/api/perfis");
    state.perfis = data.dados;
    popularSelectPerfis();
    renderPerfisGrid();
    const el = $("#statPerfis");
    if (el) el.textContent = state.perfis.length;
  } catch (e) {
    toast("Erro ao carregar perfis: " + e.message, "error");
  }
}

function popularSelectPerfis() {
  const select = $("#perfilSelect");
  const atual = select.value;
  select.innerHTML = '<option value="">Selecione um aluno...</option>';
  state.perfis.forEach(p => {
    const opt = document.createElement("option");
    opt.value = p.id;
    opt.textContent = `${p.nome} (${p.idade} anos, ${p.nivel})`;
    select.appendChild(opt);
  });
  if (atual) select.value = atual;
}

function mostrarPerfilCard(perfilId) {
  const card = $("#perfilCard");
  const info = $("#perfilInfo");
  const perfil = state.perfis.find(p => p.id == perfilId);

  if (!perfil) {
    card.classList.remove("visible");
    return;
  }

  info.innerHTML = `
    <span class="perfil-tag">&#128100; ${perfil.nome}</span>
    <span class="perfil-tag">&#127874; ${perfil.idade} anos</span>
    <span class="perfil-tag">&#128218; ${perfil.nivel}</span>
    <span class="perfil-tag">&#127912; ${perfil.estilo_aprendizado}</span>
  `;
  card.classList.add("visible");
}

// ─── Gerador ───

function validarFormulario() {
  const perfil = $("#perfilSelect").value;
  const topico = $("#topicoInput").value.trim();
  const tipo = $("#tipoSelect").value;
  const valido = perfil && topico && tipo;
  $("#btnGerar").disabled = !valido;
  $("#btnGerarTodos").disabled = !(perfil && topico);
  $("#btnComparar").disabled = !valido;
}

function mostrarLoading(msg = "Gerando conteúdo...") {
  const area = $("#resultArea");
  area.innerHTML = `
    <div class="loading-container">
      <div class="loading-spinner"></div>
      <div class="loading-text">${msg}</div>
      <div class="loading-subtext">Isso pode levar alguns segundos...</div>
    </div>
  `;
}

function renderResultado(resultado) {
  const icones = {
    explicacao_conceitual: "&#128218;",
    exemplos_praticos: "&#128736;",
    perguntas_reflexao: "&#10067;",
    resumo_visual: "&#128202;"
  };

  const meta = resultado.metadados || {};
  return `
    <div class="result-card">
      <div class="result-card-header">
        <div class="result-card-title">
          <span>${icones[resultado.tipo_conteudo] || "&#128196;"}</span>
          ${resultado.tipo_conteudo_nome || resultado.tipo_conteudo}
        </div>
        <div class="result-card-meta">
          <span class="result-meta-item">&#128100; ${resultado.perfil?.nome || ""}</span>
          <span class="result-meta-item">&#9889; ${resultado.versao_prompt}</span>
          <span class="result-meta-item">&#128337; ${meta.tempo_resposta_ms || 0}ms</span>
          <span class="result-meta-item">${meta.tokens_resposta || 0} tokens</span>
        </div>
      </div>
      <div class="result-card-body">
        <div class="result-content">${renderMarkdown(resultado.conteudo_gerado)}</div>
      </div>
    </div>
  `;
}

async function gerarConteudo() {
  if (state.gerando) return;
  state.gerando = true;
  mostrarLoading();

  try {
    const data = await api("/api/gerar", {
      method: "POST",
      body: JSON.stringify({
        perfil_id: parseInt($("#perfilSelect").value),
        topico: $("#topicoInput").value.trim(),
        tipo_conteudo: $("#tipoSelect").value,
        versao_prompt: state.versaoPrompt
      })
    });
    $("#resultArea").innerHTML = renderResultado(data.dados);
    toast("Conteúdo gerado com sucesso!", "success");
    carregarHistorico();
  } catch (e) {
    toast("Erro: " + e.message, "error");
    $("#resultArea").innerHTML = `<div class="result-placeholder"><div class="result-placeholder-icon">&#9888;</div><h3>Erro na geração</h3><p>${e.message}</p></div>`;
  } finally {
    state.gerando = false;
  }
}

async function gerarTodos() {
  if (state.gerando) return;
  state.gerando = true;
  mostrarLoading("Gerando todos os 4 tipos de conteúdo...");

  try {
    const data = await api("/api/gerar-todos", {
      method: "POST",
      body: JSON.stringify({
        perfil_id: parseInt($("#perfilSelect").value),
        topico: $("#topicoInput").value.trim(),
        versao_prompt: state.versaoPrompt
      })
    });
    $("#resultArea").innerHTML = data.dados.map(r => renderResultado(r)).join("");
    toast("Todos os conteúdos gerados!", "success");
    carregarHistorico();
  } catch (e) {
    toast("Erro: " + e.message, "error");
    $("#resultArea").innerHTML = `<div class="result-placeholder"><div class="result-placeholder-icon">&#9888;</div><h3>Erro na geração</h3><p>${e.message}</p></div>`;
  } finally {
    state.gerando = false;
  }
}

async function compararVersoes() {
  if (state.gerando) return;
  state.gerando = true;
  mostrarLoading("Comparando versões v1 e v2...");

  try {
    const data = await api("/api/comparar", {
      method: "POST",
      body: JSON.stringify({
        perfil_id: parseInt($("#perfilSelect").value),
        topico: $("#topicoInput").value.trim(),
        tipo_conteudo: $("#tipoSelect").value
      })
    });

    const comp = data.dados;
    $("#resultArea").innerHTML = `
      <div class="comparison-container">
        <div class="comparison-card comparison-v1">
          <div class="comparison-card-header">
            <strong>v1 — Padrão</strong>
            <span>${comp.versao_v1.tokens_resposta} tokens | ${comp.versao_v1.tempo_ms}ms</span>
          </div>
          <div class="comparison-card-body result-content">${renderMarkdown(comp.versao_v1.conteudo)}</div>
        </div>
        <div class="comparison-card comparison-v2">
          <div class="comparison-card-header">
            <strong>v2 — Avançado</strong>
            <span>${comp.versao_v2.tokens_resposta} tokens | ${comp.versao_v2.tempo_ms}ms</span>
          </div>
          <div class="comparison-card-body result-content">${renderMarkdown(comp.versao_v2.conteudo)}</div>
        </div>
      </div>
    `;
    toast("Comparação concluída!", "success");
    carregarHistorico();
  } catch (e) {
    toast("Erro: " + e.message, "error");
    $("#resultArea").innerHTML = `<div class="result-placeholder"><div class="result-placeholder-icon">&#9888;</div><h3>Erro na comparação</h3><p>${e.message}</p></div>`;
  } finally {
    state.gerando = false;
  }
}

// ─── Histórico ───

async function carregarHistorico() {
  try {
    const data = await api("/api/historico");
    const lista = $("#historicoList");
    const items = data.dados;

    if (!items || items.length === 0) {
      lista.innerHTML = '<div class="historico-empty"><p>Nenhuma geração registrada ainda.</p></div>';
      return;
    }

    lista.innerHTML = items.slice(0, 20).map(item => {
      const perfil = item.perfil || {};
      const ts = item.timestamp ? new Date(item.timestamp).toLocaleString("pt-BR") : "";
      return `
        <div class="historico-item" onclick='mostrarNoModal("${(item.tipo_conteudo_nome || item.tipo_conteudo).replace(/'/g, "\\'")} — ${(item.topico || "").replace(/'/g, "\\'")}", ${JSON.stringify(JSON.stringify(item.conteudo_gerado))})'>
          <div class="historico-item-info">
            <div class="historico-item-title">${item.topico || "Sem tópico"}</div>
            <div class="historico-item-meta">
              <span>&#128100; ${perfil.nome || "N/A"}</span>
              <span>&#128197; ${ts}</span>
              <span>&#9889; ${item.versao_prompt || ""}</span>
            </div>
          </div>
          <span class="historico-item-badge">${item.tipo_conteudo_nome || item.tipo_conteudo}</span>
        </div>
      `;
    }).join("");
  } catch {
    // silencioso
  }
}

// ─── Perfis Grid (CRUD) ───

function renderPerfisGrid() {
  const grid = $("#perfisGrid");
  if (!state.perfis.length) {
    grid.innerHTML = '<div class="historico-empty"><p>Nenhum perfil encontrado.</p></div>';
    return;
  }

  grid.innerHTML = state.perfis.map(p => {
    const isCustom = p.customizado;
    const badgeClass = isCustom ? "custom" : "";
    const badgeText = isCustom ? "Customizado" : "Padrão";
    const deleteBtn = isCustom
      ? `<button class="btn-delete" onclick="event.stopPropagation(); deletarPerfil(${p.id})" title="Remover perfil">&#128465;</button>`
      : "";

    return `
      <div class="perfil-grid-card">
        ${deleteBtn}
        <div class="perfil-grid-card-name">
          ${p.nome}
          <span class="perfil-grid-card-badge ${badgeClass}">${badgeText}</span>
        </div>
        <div class="perfil-grid-card-tags">
          <span class="perfil-tag">&#127874; ${p.idade} anos</span>
          <span class="perfil-tag">&#128218; ${p.nivel}</span>
          <span class="perfil-tag">&#127912; ${p.estilo_aprendizado}</span>
        </div>
        ${p.descricao ? `<div class="perfil-grid-card-desc">${p.descricao}</div>` : ""}
      </div>
    `;
  }).join("");
}

async function criarPerfil() {
  const nome = $("#novoNome").value.trim();
  const idade = parseInt($("#novoIdade").value);
  const nivel = $("#novoNivel").value;
  const estilo = $("#novoEstilo").value;
  const descricao = $("#novoDescricao").value.trim();

  if (!nome || !idade || !nivel || !estilo) {
    toast("Preencha todos os campos obrigatórios", "error");
    return;
  }

  try {
    await api("/api/perfis", {
      method: "POST",
      body: JSON.stringify({
        nome, idade, nivel,
        estilo_aprendizado: estilo,
        descricao
      })
    });
    toast("Perfil criado com sucesso!", "success");
    $("#novoNome").value = "";
    $("#novoIdade").value = "";
    $("#novoNivel").value = "";
    $("#novoEstilo").value = "";
    $("#novoDescricao").value = "";
    await carregarPerfis();
  } catch (e) {
    toast("Erro ao criar perfil: " + e.message, "error");
  }
}

async function deletarPerfil(id) {
  if (!confirm("Deseja realmente remover este perfil?")) return;
  try {
    await api(`/api/perfis/${id}`, { method: "DELETE" });
    toast("Perfil removido", "success");
    await carregarPerfis();
  } catch (e) {
    toast("Erro: " + e.message, "error");
  }
}

// ─── Samples ───

async function carregarSamples() {
  try {
    const data = await api("/api/samples");
    const grid = $("#samplesGrid");
    const samples = data.dados;

    if (!samples || samples.length === 0) {
      grid.innerHTML = '<div class="historico-empty"><p>Nenhum sample disponível.</p></div>';
      return;
    }

    grid.innerHTML = samples.map(s => `
      <div class="sample-card" onclick="abrirSample('${s.arquivo}')">
        <div class="sample-card-header">
          <span class="sample-card-tipo">${s.tipo_conteudo_nome || s.tipo_conteudo}</span>
          <span class="sample-card-versao">${s.versao_prompt}</span>
        </div>
        <div class="sample-card-topico">${s.topico}</div>
        <div class="sample-card-perfil">&#128100; ${s.perfil_nome}</div>
      </div>
    `).join("");
  } catch {
    const grid = $("#samplesGrid");
    grid.innerHTML = '<div class="historico-empty"><p>Erro ao carregar samples.</p></div>';
  }
}

async function abrirSample(arquivo) {
  try {
    const data = await api(`/api/samples/${arquivo}`);
    const s = data.dados;
    const titulo = `${s.tipo_conteudo_nome || s.tipo_conteudo} — ${s.topico}`;
    const meta = s.metadados || {};

    const html = `
      <div style="margin-bottom: 1rem; display: flex; flex-wrap: wrap; gap: 0.5rem;">
        <span class="perfil-tag">&#128100; ${s.perfil?.nome || ""}</span>
        <span class="perfil-tag">&#127874; ${s.perfil?.idade || ""} anos</span>
        <span class="perfil-tag">&#128218; ${s.perfil?.nivel || ""}</span>
        <span class="perfil-tag">&#127912; ${s.perfil?.estilo_aprendizado || ""}</span>
        <span class="perfil-tag">&#9889; ${s.versao_prompt}</span>
        <span class="perfil-tag">&#128337; ${meta.tempo_resposta_ms || 0}ms</span>
      </div>
      <div class="result-content">${renderMarkdown(s.conteudo_gerado)}</div>
    `;

    abrirModal(titulo, html);
  } catch (e) {
    toast("Erro ao carregar sample: " + e.message, "error");
  }
}

// ─── Modal ───

function abrirModal(titulo, htmlContent) {
  $("#modalTitle").textContent = titulo;
  $("#modalBody").innerHTML = htmlContent;
  $("#modalOverlay").classList.add("active");
  document.body.style.overflow = "hidden";
}

function fecharModal() {
  $("#modalOverlay").classList.remove("active");
  document.body.style.overflow = "";
}

function mostrarNoModal(titulo, conteudoJson) {
  const conteudo = JSON.parse(conteudoJson);
  abrirModal(titulo, `<div class="result-content">${renderMarkdown(conteudo)}</div>`);
}

// ─── Status ───

async function verificarStatus() {
  try {
    const data = await api("/api/status");
    const dbEl = $("#statDB");
    if (dbEl) {
      dbEl.textContent = data.dados.banco_de_dados ? "ON" : "OFF";
      dbEl.style.color = data.dados.banco_de_dados ? "#4CAF50" : "rgba(255,255,255,0.3)";
    }
  } catch {
    // silencioso
  }
}

// ─── Inicialização ───

document.addEventListener("DOMContentLoaded", () => {
  initNavbar();

  // Versão do prompt
  $$(".version-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      $$(".version-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      state.versaoPrompt = btn.dataset.version;
    });
  });

  // Formulário
  $("#perfilSelect").addEventListener("change", (e) => {
    mostrarPerfilCard(e.target.value);
    validarFormulario();
  });
  $("#topicoInput").addEventListener("input", validarFormulario);
  $("#tipoSelect").addEventListener("change", validarFormulario);

  // Botões do gerador
  $("#btnGerar").addEventListener("click", gerarConteudo);
  $("#btnGerarTodos").addEventListener("click", gerarTodos);
  $("#btnComparar").addEventListener("click", compararVersoes);

  // Perfis
  $("#btnCriarPerfil").addEventListener("click", criarPerfil);

  // Modal
  $("#modalClose").addEventListener("click", fecharModal);
  $("#modalOverlay").addEventListener("click", (e) => {
    if (e.target === e.currentTarget) fecharModal();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") fecharModal();
  });

  // Carregar dados
  carregarPerfis();
  carregarSamples();
  carregarHistorico();
  verificarStatus();
});
