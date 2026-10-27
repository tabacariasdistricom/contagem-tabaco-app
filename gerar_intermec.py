"""Gera intermec.html (versão para o Honeywell CK65) a partir de index.html.

Uso: python gerar_intermec.py   (correr depois de cada alteração ao index.html)
O CK65 tem leitor integrado que escreve o código no campo focado (DataWedge/«teclado» + Enter) e teclado físico,
por isso a versão Intermec esconde a câmara e a voz, mantém o foco no campo de leitura e não abre o teclado do ecrã.
"""
from pathlib import Path

AQUI = Path(__file__).parent
h = (AQUI / "index.html").read_text(encoding="utf-8")


def trocar(velho, novo):
    global h
    assert h.count(velho) == 1, velho
    h = h.replace(velho, novo)


trocar("<title>Contagem de tabaco</title>", "<title>Contagem de tabaco (Intermec)</title>")
trocar('href="manifest.webmanifest"', 'href="manifest-intermec.webmanifest"')
trocar("register(\"sw.js\")", "register(\"sw.js\")")  # mesmo service worker (mesma origem e catálogo)
trocar(':root{--dock-h:clamp(84px,20vh,170px)}', ':root{--dock-h:0px}')
trocar('<button class="btn principal" id="b-cam" aria-label="Ler com a câmara">📷 Picar</button>',
       '<button class="btn principal" id="b-cam" aria-label="Ler com a câmara" hidden>📷 Picar</button>'
       )
for velho, novo in ((">+ Artigo fora da lista<", ">+ Artigo novo<"), (">Enviar contagem<", ">Enviar<"), (">↩ Desfazer última<", ">↩ Desfazer<"), (">Limpar tudo<", ">Limpar<")):
    trocar(velho, novo)
trocar('<div class="sub" id="r-art">0 artigos</div>',
       '<div class="sub" id="r-art">0 artigos</div>'
       '<button id="b-teclado" aria-pressed="false" title="Teclado do ecrã" aria-label="Teclado do ecrã: desligado">⌨ OFF</button>')
trocar('inputmode="search" enterkeyhint="search"', 'inputmode="none" enterkeyhint="enter"')
for i in ("s-qtd", "s-vol", "s-mpv"):
    trocar(f'<input id="{i}" inputmode="numeric"', f'<input id="{i}" inputmode="none"')

extra = r"""
<style>
.dock{display:none!important}
.acoes{display:flex;flex-wrap:wrap;justify-content:flex-start;gap:4px;padding:2px 8px 6px}
.acoes .btn{min-height:0;height:24px;padding:0 8px;font-size:.68rem;line-height:1;border-radius:6px}
.linha{grid-template-columns:minmax(0,1fr) 48px 30px;gap:4px;padding:3px 6px;margin:3px 0;border-radius:8px}
.linha .n{font-size:.78rem;line-height:1.2}
.linha .n small{display:inline;margin-left:4px;font-size:.7rem}
.linha .cod{font-size:.78rem;padding:0 5px}
.linha input{min-height:32px;font-size:.9rem;border-radius:6px;padding:0 2px}
.linha .x{min-height:30px;min-width:30px;font-size:.9rem}
main{padding:2px 8px}
.controlos select,.controlos input{min-height:36px;font-size:.9rem}
.controlos #leitura{min-height:40px}
header h1{font-size:1rem;margin:0 0 4px}
.sel .qtd input{min-height:44px;font-size:1.2rem}
.sel .qtd .btn,.sel .vol .btn{min-height:40px;font-size:.85rem}
.sel .vol input{min-height:40px;font-size:1rem}
#b-teclado{min-height:32px;min-width:32px;padding:0 8px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--muted);font:inherit;font-size:.75rem;margin-left:8px}
#b-teclado[aria-pressed="true"]{background:var(--ok);color:#fff;border-color:var(--ok)}
</style>
<script>
// mostra no ecrã qualquer erro de JavaScript (para diagnosticar no CK65)
window.addEventListener("error", e => {
  let b = document.getElementById("erro-js");
  if (!b){ b = document.createElement("div"); b.id = "erro-js"; b.style.cssText = "position:fixed;top:0;left:0;right:0;z-index:99;background:#b00020;color:#fff;font:12px monospace;padding:6px;white-space:pre-wrap"; document.body.appendChild(b); }
  b.textContent += (e.message || "erro") + " [" + String(e.filename || "").split("/").pop() + ":" + e.lineno + "] ";
});
// ---- versão Intermec CK65: leitor integrado + teclado físico ----
try { (function(){
  const campos = ["leitura", "s-qtd", "s-vol", "s-mpv"].map(i => $(i));
  let tecl = false;
  $("b-teclado").addEventListener("click", () => {
    tecl = !tecl; $("b-teclado").setAttribute("aria-pressed", tecl);
    $("b-teclado").textContent = "⌨ " + (tecl ? "ON" : "OFF"); $("b-teclado").setAttribute("aria-label", "Teclado do ecrã: " + (tecl ? "ligado" : "desligado"));
    campos.forEach(c => c.setAttribute("inputmode", tecl ? (c.id === "leitura" ? "search" : "numeric") : "none"));
    $("leitura").blur(); $("leitura").focus();
  });
  // o leitor integrado escreve o código sem Enter: um código completo (≥ 8 dígitos) parado 150 ms é submetido sozinho
  let esp;
  $("leitura").addEventListener("input", e => {
    clearTimeout(esp); const v = e.target.value.trim();
    const m = v.match(/\d{8,}/);
    if (m) esp = setTimeout(() => { if ($("leitura").value.trim() === v) procurar(m[0]); }, 200);
  });
  $("leitura").addEventListener("keydown", e => {
    if (e.key === "Enter" || e.key === "Tab"){ clearTimeout(esp); const m = e.target.value.match(/\d{8,}/); if (m){ e.preventDefault(); procurar(m[0]); } }
  });
  // Enter (ou Tab) enviado pelo leitor logo depois de abrir o artigo não deve gravar a quantidade vazia
  let abriu = 0; const escolherOrig = escolher;
  escolher = function(a){ abriu = Date.now(); return escolherOrig.apply(this, arguments); };
  $("s-qtd").addEventListener("keydown", e => {
    if ((e.key === "Enter" || e.key === "Tab") && !e.target.value && Date.now() - abriu < 600){ e.stopImmediatePropagation(); e.preventDefault(); }
  }, true);
  // um código lido quando o cursor está nas quantidades (≥ 8 dígitos) é um novo artigo, não uma quantidade
  for (const id of ["s-qtd", "s-vol", "s-mpv"]) $(id).addEventListener("keydown", e => {
    const v = e.target.value.trim();
    if (e.key === "Enter" && /^\d{8,}$/.test(v)){ e.stopImmediatePropagation(); e.preventDefault(); e.target.value = ""; procurar(v); }
  }, true);
  // o foco volta sempre ao campo de leitura quando não se está a escrever noutro campo
  const livre = () => !document.querySelector("dialog[open]") && !/^(INPUT|SELECT|TEXTAREA)$/.test(document.activeElement.tagName);
  document.addEventListener("click", e => { if (livre() && !e.target.closest("button,a,label")) $("leitura").focus(); });
  document.addEventListener("keydown", e => { if (livre() && e.key && e.key.length === 1 && !e.ctrlKey && !e.altKey) $("leitura").focus(); });
  setInterval(() => { if (livre()) $("leitura").focus(); }, 1500);
  $("leitura").focus();
})(); } catch (err) { window.dispatchEvent(new ErrorEvent("error", {message: "intermec: " + err.message})); }
</script>
</body>"""
trocar("</body>", extra)
(AQUI / "intermec.html").write_text(h, encoding="utf-8")

m = (AQUI / "manifest.webmanifest").read_text(encoding="utf-8")
m = (m.replace('"Contagem de tabaco"', '"Contagem de tabaco (Intermec)"').replace('"short_name": "Tabaco"', '"short_name": "Tabaco CK65"')
      .replace('./index.html', './intermec.html'))
(AQUI / "manifest-intermec.webmanifest").write_text(m, encoding="utf-8")
print("intermec.html e manifest-intermec.webmanifest gerados")
