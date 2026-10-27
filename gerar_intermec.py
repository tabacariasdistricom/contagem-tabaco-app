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
trocar(':root{--dock-h:clamp(84px,20vh,170px)}', ':root{--dock-h:52px}')
trocar('<button class="btn principal" id="b-cam" aria-label="Ler com a câmara">📷 Picar</button>',
       '<button class="btn principal" id="b-cam" aria-label="Ler com a câmara" hidden>📷 Picar</button>'
       '<button class="btn" id="b-teclado" aria-pressed="false" style="flex:1;height:var(--dock-h)">⌨ Teclado do ecrã: OFF</button>')
trocar('inputmode="search" enterkeyhint="search"', 'inputmode="none" enterkeyhint="enter"')
for i in ("s-qtd", "s-vol", "s-mpv"):
    trocar(f'<input id="{i}" inputmode="numeric"', f'<input id="{i}" inputmode="none"')

extra = r"""
<style>
.dock #b-cam,.dock #b-voz{display:none!important}
.dock{display:flex}
</style>
<script>
// ---- versão Intermec CK65: leitor integrado + teclado físico ----
(function(){
  const campos = ["leitura", "s-qtd", "s-vol", "s-mpv"].map(i => $(i));
  $("dock").hidden = false;
  let tecl = false;
  $("b-teclado").addEventListener("click", () => {
    tecl = !tecl; $("b-teclado").setAttribute("aria-pressed", tecl);
    $("b-teclado").textContent = "⌨ Teclado do ecrã: " + (tecl ? "ON" : "OFF");
    campos.forEach(c => c.setAttribute("inputmode", tecl ? (c.id === "leitura" ? "search" : "numeric") : "none"));
    $("leitura").blur(); $("leitura").focus();
  });
  // um código lido quando o cursor está nas quantidades (≥ 8 dígitos) é um novo artigo, não uma quantidade
  for (const id of ["s-qtd", "s-vol", "s-mpv"]) $(id).addEventListener("keydown", e => {
    const v = e.target.value.trim();
    if (e.key === "Enter" && /^\d{8,}$/.test(v)){ e.stopImmediatePropagation(); e.preventDefault(); e.target.value = ""; procurar(v); }
  }, true);
  // o foco volta sempre ao campo de leitura quando não se está a escrever noutro campo
  const livre = () => !document.querySelector("dialog[open]") && !/^(INPUT|SELECT|TEXTAREA)$/.test(document.activeElement.tagName);
  document.addEventListener("click", e => { if (livre() && !e.target.closest("button,a,label")) $("leitura").focus(); });
  document.addEventListener("keydown", e => { if (livre() && e.key.length === 1 && !e.ctrlKey && !e.altKey) $("leitura").focus(); });
  setInterval(() => { if (livre()) $("leitura").focus(); }, 1500);
  $("leitura").focus();
})();
</script>
</body>"""
trocar("</body>", extra)
(AQUI / "intermec.html").write_text(h, encoding="utf-8")

m = (AQUI / "manifest.webmanifest").read_text(encoding="utf-8")
m = (m.replace('"Contagem de tabaco"', '"Contagem de tabaco (Intermec)"').replace('"short_name": "Tabaco"', '"short_name": "Tabaco CK65"')
      .replace('./index.html', './intermec.html'))
(AQUI / "manifest-intermec.webmanifest").write_text(m, encoding="utf-8")
print("intermec.html e manifest-intermec.webmanifest gerados")
