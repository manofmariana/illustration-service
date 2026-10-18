"""管理页:一个自包含的 HTML(无构建步骤、无外部依赖),由网关在 / 提供。

刻意只留两个下拉:选服务(模式)、选 harness(后端)。
"""

PAGE = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Illustration Gateway</title>
<style>
  :root {
    --bg: #14161a; --panel: #1b1e24; --panel2: #22262e; --line: #2c313a;
    --text: #e6e9ef; --dim: #8d95a3; --accent: #6ea8fe; --ok: #4ade80; --warn: #fbbf24; --bad: #f87171;
  }
  * { box-sizing: border-box; }
  body { margin: 0; background: var(--bg); color: var(--text);
         font: 14px/1.6 -apple-system, "Segoe UI", "Microsoft YaHei", sans-serif; }
  main { max-width: 720px; margin: 0 auto; padding: 28px 20px 60px; }
  h1 { font-size: 19px; margin: 0 0 4px; }
  .sub { color: var(--dim); font-size: 12px; margin-bottom: 20px; }
  section { background: var(--panel); border: 1px solid var(--line); border-radius: 10px;
            padding: 16px 18px; margin-bottom: 14px; }
  h2 { font-size: 12px; margin: 0 0 12px; color: var(--dim); font-weight: 600;
       text-transform: uppercase; letter-spacing: .8px; }
  .pills { display: flex; gap: 22px; flex-wrap: wrap; }
  .pill { display: inline-flex; align-items: center; gap: 7px; font-size: 12px; }
  .dot { width: 8px; height: 8px; border-radius: 50%; background: var(--dim); }
  .dot.ok { background: var(--ok); } .dot.warn { background: var(--warn); } .dot.bad { background: var(--bad); }
  .controls { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
  .controls .grow { flex: 1; min-width: 200px; }
  .field { display: flex; flex-direction: column; gap: 6px; }
  .field label { font-size: 12px; color: var(--dim); }
  select, input, button {
    font: inherit; color: var(--text); background: var(--panel2);
    border: 1px solid var(--line); border-radius: 7px; padding: 7px 10px; outline: none;
  }
  select { min-width: 210px; }
  select:focus, input:focus { border-color: var(--accent); }
  button { cursor: pointer; }
  button:hover { border-color: var(--accent); }
  button.primary { background: var(--accent); color: #10151f; border-color: var(--accent); font-weight: 600; }
  button.ghost { background: transparent; }
  .msg { font-size: 12px; color: var(--dim); }
  .grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
  .actions { display: flex; gap: 10px; align-items: center; margin-top: 12px; flex-wrap: wrap; }
  .hint { color: var(--dim); font-size: 12px; margin-top: 8px; }
  @media (max-width: 640px) { .grid2 { grid-template-columns: 1fr; } }
</style>
</head>
<body>
<main>
  <h1>Illustration Gateway</h1>
  <div class="sub">一个服务跑全部生图提示词分支</div>

  <section>
    <h2>状态</h2>
    <div class="pills">
      <div class="pill"><span class="dot" id="d-kimi"></span><span id="t-kimi">kimi web</span></div>
      <div class="pill"><span class="dot" id="d-dsh"></span><span id="t-dsh">DSH</span></div>
      <div class="pill"><span class="dot ok" id="d-port"></span><span id="t-port">端口</span></div>
    </div>
  </section>

  <section>
    <h2>服务</h2>
    <div class="controls">
      <select id="mode-select" class="grow"></select>
      <select id="backend-select">
        <option value="kimi">kimi</option>
        <option value="dsh">DSH</option>
      </select>
      <button class="primary" id="save">保存</button>
      <span class="msg" id="msg"></span>
    </div>
  </section>

  <section>
    <h2>DSH</h2>
    <div class="grid2">
      <div class="field">
        <label>API key <span id="key-state" class="desc"></span></label>
        <input id="dsh-key" type="password" placeholder="sk-... 留空表示不修改" autocomplete="off">
      </div>
      <div class="field">
        <label>模型</label>
        <input id="dsh-model" type="text" placeholder="deepseek-flash">
      </div>
    </div>
    <div class="actions">
      <button class="primary" id="save-dsh">保存</button>
      <button class="ghost" id="clear-key">清除 key</button>
      <span class="msg" id="msg-dsh"></span>
    </div>
    <div class="hint" id="dsh-hint"></div>
  </section>
</main>

<script>
const $ = (id) => document.getElementById(id);
let state = null;

function pill(dotId, textId, cls, text) {
  $(dotId).className = "dot " + cls;
  $(textId).textContent = text;
}

function syncBackend() {
  const mode = $("mode-select").value;
  const found = (state.modes || []).find(m => m.key === mode);
  $("backend-select").value = found ? found.backend : "kimi";
}

async function loadStatus() {
  const res = await fetch("/api/status");
  if (!res.ok) { throw new Error(await res.text()); }
  state = await res.json();

  pill("d-kimi", "t-kimi", state.kimi.reachable ? "ok" : "bad",
       state.kimi.reachable ? "kimi web 在线" : "kimi web 未连接");
  pill("d-dsh", "t-dsh", state.dsh.ready ? "ok" : "warn",
       state.dsh.ready ? "DSH 就绪 · " + state.dsh.model : "DSH 未就绪");
  pill("d-port", "t-port", "ok", "端口 " + state.port);

  $("mode-select").innerHTML = state.modes
    .map(m => `<option value="${m.key}">${m.title}</option>`).join("");
  $("mode-select").value = state.default_mode;
  syncBackend();

  $("dsh-model").value = state.dsh.model || "";
  $("key-state").textContent = state.dsh.key ? "已配置 " + state.dsh.key : "未配置";
  $("dsh-hint").textContent = state.dsh.ready ? "" : state.dsh.reason;
}

async function postJSON(url, body) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) { throw new Error(data.detail || JSON.stringify(data)); }
  return data;
}

$("mode-select").onchange = syncBackend;

$("save").onclick = async () => {
  const mode = $("mode-select").value;
  const backends = {};
  backends[mode] = $("backend-select").value;
  try {
    await postJSON("/api/settings", { default_mode: mode, backends });
    $("msg").textContent = "已保存";
    await loadStatus();
    setTimeout(() => { $("msg").textContent = ""; }, 2000);
  } catch (e) { $("msg").textContent = "失败: " + e.message; }
};

$("save-dsh").onclick = async () => {
  const payload = { dsh_model: $("dsh-model").value };
  const key = $("dsh-key").value.trim();
  if (key) { payload.dsh_api_key = key; }
  try {
    await postJSON("/api/settings", payload);
    $("dsh-key").value = "";
    $("msg-dsh").textContent = "已保存";
    await loadStatus();
    setTimeout(() => { $("msg-dsh").textContent = ""; }, 2000);
  } catch (e) { $("msg-dsh").textContent = "失败: " + e.message; }
};

$("clear-key").onclick = async () => {
  try {
    await postJSON("/api/settings", { clear_key: true });
    $("msg-dsh").textContent = "key 已清除";
    await loadStatus();
  } catch (e) { $("msg-dsh").textContent = "失败: " + e.message; }
};

loadStatus().catch(e => {
  document.body.insertAdjacentHTML("afterbegin",
    `<div style="padding:12px;color:#f87171">状态读取失败: ${e.message}</div>`);
});
</script>
</body>
</html>
"""
