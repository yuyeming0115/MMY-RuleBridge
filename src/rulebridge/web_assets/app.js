const state = {
  root: new URLSearchParams(location.search).get('root') || '.',
  target: '',
  theme: new URLSearchParams(location.search).get('theme') || 'dark',
  action: 'inspect',
  force: false,
  insertManagedBlock: false,
  data: null,
};

const $ = (id) => document.getElementById(id);
const esc = (value) => String(value ?? '').replace(/[&<>"']/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

function badge(text, kind='info') { return `<span class="badge ${kind}">${esc(text)}</span>`; }
function metric(label, value) { return `<div class="metric"><span>${esc(label)}</span><b>${esc(value)}</b></div>`; }
function severityCounts(items=[]) {
  const counts = {ERROR:0, WARN:0, INFO:0};
  for (const item of items) counts[item.severity] = (counts[item.severity] || 0) + 1;
  return counts;
}
function statusKind(items=[]) {
  const counts = severityCounts(items);
  if (counts.ERROR) return 'error';
  if (counts.WARN) return 'warn';
  return 'ok';
}
function statusText(kind) { return kind === 'error' ? 'ERROR' : kind === 'warn' ? 'WARN' : 'OK'; }

function table(headers, rows, empty='No data.') {
  if (!rows || !rows.length) return `<p class="muted">${esc(empty)}</p>`;
  const head = headers.map(h => `<th>${esc(h)}</th>`).join('');
  const body = rows.map(row => `<tr>${row.map(cell => `<td>${cell}</td>`).join('')}</tr>`).join('');
  return `<div class="table-wrap"><table><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table></div>`;
}

function apiUrl(path, params={}) {
  const url = new URL(path, location.origin);
  for (const [key, value] of Object.entries(params)) if (value !== undefined && value !== null && value !== '') url.searchParams.set(key, value);
  return url.toString();
}
async function getJson(path, params={}) {
  const res = await fetch(apiUrl(path, params));
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
async function postJson(path, body={}) {
  const res = await fetch(path, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)});
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

function readControls() {
  state.root = $('rootInput').value || '.';
  state.target = $('targetSelect').value || '';
  state.force = $('forceInput').checked;
  state.insertManagedBlock = $('insertInput').checked;
}

async function inspect() {
  readControls();
  state.data = await getJson('/api/inspect', {root: state.root, target: state.target});
  render(state.data);
}

async function runAction(action) {
  readControls();
  state.action = action;
  let result;
  if (action === 'inspect') result = await getJson('/api/inspect', {root: state.root, target: state.target});
  else if (action === 'validate') result = await getJson('/api/validate', {root: state.root, target: state.target});
  else if (action === 'doctor') result = await getJson('/api/doctor', {root: state.root, target: state.target});
  else if (action === 'diff') result = await postJson('/api/diff', payload());
  else if (action === 'dry-run') result = await postJson('/api/sync', {...payload(), dry_run: true});
  else if (action === 'sync') {
    if (!confirm('确认要写入生成文件吗？建议先 Dry Run。')) return;
    result = await postJson('/api/sync', {...payload(), dry_run: false});
  }
  if (action === 'inspect') state.data = result;
  else if (state.data) Object.assign(state.data, result);
  else state.data = await getJson('/api/inspect', {root: state.root, target: state.target});
  render(state.data, result);
}
function payload() { return {root: state.root, target: state.target, force: state.force, insert_managed_block: state.insertManagedBlock}; }

function render(data, result={}) {
  const source = data.source || {project:{name:'RuleBridge Project'}, rules:[], skills:[], commands:[], hooks:[], mcpServers:[]};
  const diagnostics = result.diagnostics || data.diagnostics || [];
  const counts = severityCounts(diagnostics);
  const kind = statusKind(diagnostics);
  const packs = data.packs || [];
  const files = data.files || [];
  const enabledPacks = packs.filter(p => p.enabled).length;

  document.body.className = `theme-${state.theme === 'light' ? 'light' : 'dark'}`;
  $('topstats').innerHTML = [
    topStat('Rules', source.rules.length), topStat('Errors', counts.ERROR, 'error'), topStat('Warnings', counts.WARN, 'warn'), badge(statusText(kind), kind), `<button class="secondary" id="themeBtn">${state.theme === 'dark' ? '浅色' : '深色'}</button>`
  ].join('');
  $('themeBtn').onclick = () => { state.theme = state.theme === 'dark' ? 'light' : 'dark'; render(state.data || data, result); };

  const targetSelect = $('targetSelect');
  targetSelect.innerHTML = `<option value="">all targets</option>` + (data.targets || []).map(t => `<option value="${esc(t)}" ${state.target===t?'selected':''}>${esc(t)}</option>`).join('');
  $('rootInput').value = state.root;
  $('forceInput').checked = state.force;
  $('insertInput').checked = state.insertManagedBlock;

  $('monitor').innerHTML = metric('Action', state.action) + metric('Status', statusText(kind)) + metric('Files', files.length) + metric('Packs', `${enabledPacks}/${packs.length}`);
  $('dashboardMetrics').innerHTML = [
    metric('Project', source.project?.name || ''), metric('Rules', source.rules.length), metric('Skills', source.skills.length), metric('Commands', source.commands.length), metric('Hooks', source.hooks.length), metric('MCP Servers', source.mcpServers.length), metric('Generated Files', files.length), metric('Errors', counts.ERROR), metric('Warnings', counts.WARN)
  ].join('');
  renderResources(source);
  $('generatedBody').innerHTML = table(['Path','Category','Mode'], files.map(f => [`<code>${esc(f.path)}</code>`, badge(category(f.path),'neutral'), badge(f.managed?'managed':'unmanaged', f.managed?'ok':'warn')]), 'No generated files.');
  $('diagnosticsBody').innerHTML = table(['Severity','Message','Path'], diagnostics.map(d => [badge(d.severity, d.severity.toLowerCase()), esc(d.message), `<code>${esc(d.path)}</code>`]), 'No diagnostics.');
  $('packsBody').innerHTML = table(['Name','State','Title','Targets','License'], packs.map(p => [esc(p.name), badge(p.enabled?'enabled':'disabled', p.enabled?'ok':'neutral'), esc(p.title), esc((p.targets||[]).join(', ')), esc(p.license)]), 'No packs found.');
  $('writeResultsBody').innerHTML = table(['Status','Path','Message'], (result.results||[]).map(r => [badge(r.status, r.status === 'skipped' ? 'warn' : 'ok'), `<code>${esc(r.path)}</code>`, esc(r.message)]), 'No write results yet.');
  $('diffBody').innerHTML = renderDiffs(result.diffs || []);
}

function renderResources(source) {
  const rules = table(['Name','Title','Path','Source','Pack'], source.rules.map(r => [esc(r.name), esc(r.title), `<code>${esc(r.path)}</code>`, esc(r.source), esc(r.pack)]), 'No rules loaded.');
  const skills = table(['Name','Path','Source','Pack'], source.skills.map(s => [esc(s.name), `<code>${esc(s.path)}</code>`, esc(s.source), esc(s.pack)]), 'No skills loaded.');
  const commands = table(['Name','Path','Source','Pack'], source.commands.map(c => [esc(c.name), `<code>${esc(c.path)}</code>`, esc(c.source), esc(c.pack)]), 'No commands loaded.');
  const hooks = table(['Event','Steps','Targets','Path','Source'], source.hooks.map(h => [esc(h.event), esc(h.steps), esc((h.targets||[]).join(', ') || 'all'), `<code>${esc(h.path)}</code>`, esc(h.source)]), 'No hooks loaded.');
  const mcp = table(['Name','State','Command','Targets','Path','Source'], source.mcpServers.map(m => [esc(m.name), badge(m.enabled?'enabled':'disabled', m.enabled?'ok':'neutral'), `<code>${esc(m.command)}</code>`, esc((m.targets||[]).join(', ') || 'all'), `<code>${esc(m.path)}</code>`, esc(m.source)]), 'No MCP servers loaded.');
  $('resourcesBody').innerHTML = `<div class="resource-grid"><section class="mini-card"><h3>Rules</h3>${rules}</section><section class="mini-card"><h3>Skills</h3>${skills}</section><section class="mini-card"><h3>Commands</h3>${commands}</section><section class="mini-card"><h3>Hooks</h3>${hooks}</section><section class="mini-card wide"><h3>MCP Servers</h3>${mcp}</section></div>`;
}
function renderDiffs(diffs) {
  if (!diffs.length) return '<p class="muted">No diff preview yet.</p>';
  return diffs.map((item, idx) => `<details ${idx < 2 ? 'open' : ''}><summary><code>${esc(item.file.path)}</code></summary><pre>${esc(item.diff || '# no changes\n')}</pre></details>`).join('');
}
function topStat(label, value, kind='neutral') { return `<div class="top-stat ${kind}"><b>${esc(value)}</b><span>${esc(label)}</span></div>`; }
function category(path) {
  const p = String(path).replace(/\\/g, '/');
  if (p === 'AGENTS.md') return 'codex'; if (p === 'CLAUDE.md' || p.startsWith('.claude/')) return 'claude'; if (p.startsWith('.cursor/')) return 'cursor'; if (p.startsWith('.zcode/')) return 'zcode'; if (p.startsWith('.trae/')) return 'trae'; if (p.startsWith('.githooks/')) return 'git'; if (p === '.mcp.json') return 'mcp'; if (p.startsWith('.codebuddy-plugin/')) return 'codebuddy'; if (p.startsWith('.workbuddy-plugin/')) return 'workbuddy'; return 'generic';
}

document.querySelectorAll('button[data-action]').forEach(btn => btn.addEventListener('click', () => runAction(btn.dataset.action).catch(showError)));
function showError(err) { $('diagnosticsBody').innerHTML = table(['Severity','Message','Path'], [[badge('ERROR','error'), esc(err.message || err), '']], ''); }
inspect().catch(showError);
