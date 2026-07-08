// ===== i18n 字典 =====
const I18N = {
  zh: {
    'ui.lang': 'EN', 'ui.light': '浅色', 'ui.dark': '深色', 'ui.stop': '停止服务',
    'brand.tagline': 'AI Agent 配置桥接控制台',
    'nav.dashboard': '概览', 'nav.operations': '操作', 'nav.resources': '资源', 'nav.generated': '生成文件',
    'nav.diagnostics': '诊断', 'nav.packs': '经验包', 'nav.results': '结果',
    'settings.title': '项目设置', 'settings.root': '项目目录', 'settings.target': '目标',
    'settings.allTargets': '全部目标', 'settings.force': '强制覆盖', 'settings.insert': '插入托管区块',
    'ops.title': '操作', 'ops.safeChecks': '安全检查', 'ops.inspect': '检查', 'ops.validate': '校验',
    'ops.doctor': '诊断', 'ops.preview': '预览', 'ops.previewDiff': '预览差异', 'ops.dryRun': '试运行同步',
    'ops.write': '写入', 'ops.sync': '同步', 'monitor.title': '监控',
    'guide.title': '小白引导', 'packs.title': 'Packs 经验包', 'dashboard.title': '仪表盘',
    'resources.title': '资源', 'generated.title': '生成文件', 'diagnostics.title': '诊断',
    'results.title': '结果', 'results.writeTitle': '写入结果', 'results.diffTitle': '差异预览',
    // 顶部统计
    'stat.rules': '规则', 'stat.errors': '错误', 'stat.warnings': '警告',
    // 监控指标
    'mon.action': '操作', 'mon.status': '状态', 'mon.files': '文件', 'mon.packs': '经验包',
    // Dashboard 指标
    'dash.project': '项目', 'dash.rules': '规则', 'dash.skills': '技能', 'dash.commands': '命令',
    'dash.hooks': '钩子', 'dash.mcp': 'MCP 服务', 'dash.generated': '生成文件',
    'dash.errors': '错误', 'dash.warnings': '警告',
    // 资源表格
    'res.rules': '规则', 'res.skills': '技能', 'res.commands': '命令', 'res.hooks': '钩子', 'res.mcp': 'MCP 服务',
    'res.name': '名称', 'res.title': '标题', 'res.path': '路径', 'res.source': '来源', 'res.pack': '经验包',
    'res.event': '事件', 'res.steps': '步骤', 'res.targets': '目标', 'res.state': '状态', 'res.command': '命令',
    'res.enabled': '已启用', 'res.disabled': '已禁用',
    'res.noRules': '未加载任何规则。', 'res.noSkills': '未加载任何技能。', 'res.noCommands': '未加载任何命令。',
    'res.noHooks': '未加载任何钩子。', 'res.noMcp': '未加载任何 MCP 服务。',
    // Packs
    'pack.empty': '还没有经验包。在 <code>.ai-agent/packs/&lt;name&gt;/pack.yaml</code> 放入可选规则/技能包后，可在这里一键启用或禁用。',
    'pack.enabled': '已启用', 'pack.disabled': '已禁用', 'pack.review': '需审查',
    'pack.name': '名称', 'pack.target': '目标', 'pack.license': '许可',
    'pack.preview': '预览内容', 'pack.disable': '禁用', 'pack.enable': '启用',
    // 差异
    'diff.empty': '暂无差异预览。',
    // 生成文件表格
    'gen.path': '路径', 'gen.category': '类别', 'gen.mode': '模式',
    'gen.managed': '托管', 'gen.unmanaged': '非托管', 'gen.empty': '暂无生成文件。',
    // 诊断表格
    'diag.severity': '级别', 'diag.message': '信息', 'diag.path': '路径', 'diag.empty': '暂无诊断信息。',
    // 写入结果表格
    'wr.status': '状态', 'wr.path': '路径', 'wr.message': '信息', 'wr.empty': '暂无写入结果。',
    // 错误标签
    'err.error': '错误',
    // Wizard 步骤
    'wiz.dir': '选目录', 'wiz.init': '初始化', 'wiz.validate': '校验', 'wiz.diff': '预览',
    'wiz.dryrun': '试运行', 'wiz.sync': '同步', 'wiz.done': '完成',
    'wiz.init.title': '初始化 RuleBridge 配置',
    'wiz.init.desc': '当前目录还没有 <code>.ai-agent/rulebridge.yaml</code>。先确认左上角 <b>Project Root</b> 指向你要管理的项目目录，然后点击下方按钮生成示例配置（rules / skills / commands / hooks / mcp / packs）。',
    'wiz.init.dirhint': '当前项目目录：<code>{root}</code>。在左上角 <b>Project Root</b> 修改后点刷新。',
    'wiz.init.btn': '初始化 .ai-agent 配置', 'wiz.init.refresh': '刷新状态',
    'wiz.validate.title': '校验配置',
    'wiz.validate.desc': '配置存在错误，需要先修复。运行 <b>Doctor</b> 查看详细诊断，或运行 <b>Validate</b> 做基础校验。修复 <code>.ai-agent</code> 源文件后刷新即可。',
    'wiz.validate.doctor': 'Doctor 深度诊断', 'wiz.validate.validate': 'Validate 校验', 'wiz.validate.refresh': '刷新',
    'wiz.diff.title': '预览将生成的内容',
    'wiz.diff.desc': '配置已就绪。点击 <b>Preview Diff</b> 查看 RuleBridge 将为每个目标 Agent 写入哪些文件及内容差异。可选：先在下方 <b>Packs</b> 区启用经验包再预览。',
    'wiz.diff.btn': 'Preview Diff', 'wiz.diff.doctor': '再次 Doctor',
    'wiz.dryrun.title': '试运行同步',
    'wiz.dryrun.desc': '预览确认无误后，先 <b>Dry Run Sync</b> 模拟一次写入，确认文件列表和写入策略（托管区块 / 覆盖）符合预期，不会真的写盘。',
    'wiz.dryrun.btn': 'Dry Run Sync', 'wiz.dryrun.back': '回到预览',
    'wiz.sync.title': '正式同步写入',
    'wiz.sync.desc': '试运行通过后，点击 <b>Sync</b> 真正写入目标文件，写入前会再次弹窗确认。建议保留 <code>force</code> 关闭，<code>insert managed block</code> 按需勾选。',
    'wiz.sync.btn': 'Sync 正式写入', 'wiz.sync.dryrun': '再试运行一次',
    'wiz.done.title': '全部完成',
    'wiz.done.desc': '配置已同步且无错误/警告。后续若修改了 <code>.ai-agent</code> 源文件，回到第 3 步重新预览并同步即可。',
    'wiz.done.hint': '当前项目状态良好，可以开始使用各 Agent 读取生成好的规则文件。',
    'wiz.done.refresh': '刷新状态', 'wiz.done.repreview': '重新预览',
    // 确认 / 遮罩 / 关闭提醒
    'confirm.sync': '确认要写入生成文件吗？建议先 Dry Run。',
    'confirm.shutdown': '确认停止 RuleBridge Web 服务？\n停止后需要重新双击 rulebridge.exe 启动。',
    'shutdown.title': '服务已停止',
    'shutdown.msg': 'RuleBridge Web 服务已关闭，可关闭此浏览器标签页。',
    'shutdown.hint': '如需再次使用，请双击 <code>rulebridge.exe</code>。',
    'unload': 'RuleBridge 服务仍在运行中。建议先点击「停止服务」按钮正常关闭进程。\n\n如直接关闭，服务将在 5 分钟无活动后自动退出。',
  },
  en: {
    'ui.lang': '中文', 'ui.light': 'Light', 'ui.dark': 'Dark', 'ui.stop': 'Stop Service',
    'brand.tagline': 'AI Agent Config Bridge Console',
    'nav.dashboard': 'Dashboard', 'nav.operations': 'Operations', 'nav.resources': 'Resources', 'nav.generated': 'Generated',
    'nav.diagnostics': 'Diagnostics', 'nav.packs': 'Packs', 'nav.results': 'Results',
    'settings.title': 'Project Settings', 'settings.root': 'Project Root', 'settings.target': 'Target',
    'settings.allTargets': 'all targets', 'settings.force': 'force overwrite', 'settings.insert': 'insert managed block',
    'ops.title': 'Operations', 'ops.safeChecks': 'Safe Checks', 'ops.inspect': 'Inspect', 'ops.validate': 'Validate',
    'ops.doctor': 'Doctor', 'ops.preview': 'Preview', 'ops.previewDiff': 'Preview Diff', 'ops.dryRun': 'Dry Run Sync',
    'ops.write': 'Write', 'ops.sync': 'Sync', 'monitor.title': 'Monitor',
    'guide.title': 'Quick Start', 'packs.title': 'Packs', 'dashboard.title': 'Dashboard',
    'resources.title': 'Resources', 'generated.title': 'Generated Files', 'diagnostics.title': 'Diagnostics',
    'results.title': 'Results', 'results.writeTitle': 'Write Results', 'results.diffTitle': 'Diff Preview',
    'stat.rules': 'Rules', 'stat.errors': 'Errors', 'stat.warnings': 'Warnings',
    'mon.action': 'Action', 'mon.status': 'Status', 'mon.files': 'Files', 'mon.packs': 'Packs',
    'dash.project': 'Project', 'dash.rules': 'Rules', 'dash.skills': 'Skills', 'dash.commands': 'Commands',
    'dash.hooks': 'Hooks', 'dash.mcp': 'MCP Servers', 'dash.generated': 'Generated Files',
    'dash.errors': 'Errors', 'dash.warnings': 'Warnings',
    'res.rules': 'Rules', 'res.skills': 'Skills', 'res.commands': 'Commands', 'res.hooks': 'Hooks', 'res.mcp': 'MCP Servers',
    'res.name': 'Name', 'res.title': 'Title', 'res.path': 'Path', 'res.source': 'Source', 'res.pack': 'Pack',
    'res.event': 'Event', 'res.steps': 'Steps', 'res.targets': 'Targets', 'res.state': 'State', 'res.command': 'Command',
    'res.enabled': 'enabled', 'res.disabled': 'disabled',
    'res.noRules': 'No rules loaded.', 'res.noSkills': 'No skills loaded.', 'res.noCommands': 'No commands loaded.',
    'res.noHooks': 'No hooks loaded.', 'res.noMcp': 'No MCP servers loaded.',
    'pack.empty': 'No experience packs yet. Place optional rule/skill packs under <code>.ai-agent/packs/&lt;name&gt;/pack.yaml</code> to enable or disable here.',
    'pack.enabled': 'Enabled', 'pack.disabled': 'Disabled', 'pack.review': 'Review',
    'pack.name': 'Name', 'pack.target': 'Target', 'pack.license': 'License',
    'pack.preview': 'Preview', 'pack.disable': 'Disable', 'pack.enable': 'Enable',
    'diff.empty': 'No diff preview yet.',
    'gen.path': 'Path', 'gen.category': 'Category', 'gen.mode': 'Mode',
    'gen.managed': 'managed', 'gen.unmanaged': 'unmanaged', 'gen.empty': 'No generated files.',
    'diag.severity': 'Severity', 'diag.message': 'Message', 'diag.path': 'Path', 'diag.empty': 'No diagnostics.',
    'wr.status': 'Status', 'wr.path': 'Path', 'wr.message': 'Message', 'wr.empty': 'No write results yet.',
    'err.error': 'ERROR',
    'wiz.dir': 'Set Dir', 'wiz.init': 'Init', 'wiz.validate': 'Validate', 'wiz.diff': 'Preview',
    'wiz.dryrun': 'Dry Run', 'wiz.sync': 'Sync', 'wiz.done': 'Done',
    'wiz.init.title': 'Initialize RuleBridge Config',
    'wiz.init.desc': 'The current directory has no <code>.ai-agent/rulebridge.yaml</code>. Confirm <b>Project Root</b> at top-left points to the project you want to manage, then click below to generate a sample config (rules / skills / commands / hooks / mcp / packs).',
    'wiz.init.dirhint': 'Current project root: <code>{root}</code>. Edit <b>Project Root</b> at top-left then refresh.',
    'wiz.init.btn': 'Initialize .ai-agent Config', 'wiz.init.refresh': 'Refresh',
    'wiz.validate.title': 'Validate Config',
    'wiz.validate.desc': 'There are errors in the config that must be fixed. Run <b>Doctor</b> for detailed diagnostics, or <b>Validate</b> for a basic check. Fix the <code>.ai-agent</code> sources then refresh.',
    'wiz.validate.doctor': 'Doctor Diagnose', 'wiz.validate.validate': 'Validate', 'wiz.validate.refresh': 'Refresh',
    'wiz.diff.title': 'Preview Generated Content',
    'wiz.diff.desc': 'Config is ready. Click <b>Preview Diff</b> to see which files and content diffs RuleBridge will write for each target Agent. Optional: enable experience packs in the <b>Packs</b> section below first.',
    'wiz.diff.btn': 'Preview Diff', 'wiz.diff.doctor': 'Doctor Again',
    'wiz.dryrun.title': 'Dry Run Sync',
    'wiz.dryrun.desc': 'After confirming the preview, run <b>Dry Run Sync</b> to simulate a write — verify the file list and write strategy (managed block / overwrite) without actually writing to disk.',
    'wiz.dryrun.btn': 'Dry Run Sync', 'wiz.dryrun.back': 'Back to Preview',
    'wiz.sync.title': 'Sync to Write',
    'wiz.sync.desc': 'After a successful dry run, click <b>Sync</b> to actually write target files; a confirmation dialog appears first. Keep <code>force</code> off, and check <code>insert managed block</code> as needed.',
    'wiz.sync.btn': 'Sync to Write', 'wiz.sync.dryrun': 'Dry Run Again',
    'wiz.done.title': 'All Done',
    'wiz.done.desc': 'Config is synced with no errors/warnings. If you later modify the <code>.ai-agent</code> sources, return to step 3 to re-preview and sync.',
    'wiz.done.hint': 'The project is in good shape. Each Agent can now read the generated rule files.',
    'wiz.done.refresh': 'Refresh', 'wiz.done.repreview': 'Re-preview',
    'confirm.sync': 'Confirm writing generated files? A Dry Run is recommended first.',
    'confirm.shutdown': 'Stop the RuleBridge Web service?\nYou will need to double-click rulebridge.exe again to restart.',
    'shutdown.title': 'Service Stopped',
    'shutdown.msg': 'The RuleBridge Web service is stopped. You may close this browser tab.',
    'shutdown.hint': 'To use it again, double-click <code>rulebridge.exe</code>.',
    'unload': 'The RuleBridge service is still running. It is recommended to click "Stop Service" to shut down cleanly.\n\nIf you close directly, the service auto-exits after 5 minutes of inactivity.',
  },
};

// ===== 持久化辅助 =====
const THEME_KEY = 'rb_theme';
const LANG_KEY = 'rb_lang';
const flagsKey = (root) => `rb_flags_${root}`;
function loadFlags(root) {
  try { const v = localStorage.getItem(flagsKey(root)); if (v) return JSON.parse(v); } catch(e) {}
  return { diff: false, dryrun: false, sync: false };
}
function saveFlags(root, flags) {
  try { localStorage.setItem(flagsKey(root), JSON.stringify(flags)); } catch(e) {}
}
function loadLang() {
  try { const v = localStorage.getItem(LANG_KEY); if (v === 'zh' || v === 'en') return v; } catch(e) {}
  return (navigator.language || 'zh').toLowerCase().startsWith('zh') ? 'zh' : 'en';
}
function saveLang(lang) { try { localStorage.setItem(LANG_KEY, lang); } catch(e) {} }
function loadTheme() {
  try { return localStorage.getItem(THEME_KEY) || (new URLSearchParams(location.search).get('theme') || 'dark'); } catch(e) { return 'dark'; }
}
function saveTheme(theme) {
  try { localStorage.setItem(THEME_KEY, theme); } catch(e) {}
}
function t(key, vars={}) {
  const dict = I18N[state.lang] || I18N.zh;
  let s = dict[key] !== undefined ? dict[key] : (I18N.zh[key] !== undefined ? I18N.zh[key] : key);
  for (const [k, v] of Object.entries(vars)) s = s.replace(new RegExp('\\{' + k + '\\}', 'g'), v);
  return s;
}
function applyStaticI18n() {
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (key) el.textContent = t(key);
  });
}

const initRoot = new URLSearchParams(location.search).get('root') || '.';
const state = {
  root: initRoot,
  defaultRoot: initRoot,
  target: '',
  theme: loadTheme(),
  lang: loadLang(),
  action: 'inspect',
  force: false,
  insertManagedBlock: false,
  data: null,
  stepFlags: loadFlags(initRoot),
};

const $ = (id) => document.getElementById(id);
const esc = (value) => String(value ?? '').replace(/[&<>"']/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

function badge(text, kind='info') { return `<span class="badge ${kind}">${esc(text)}</span>`; }
function metric(label, value) { return `<div class="metric"><span>${esc(label)}</span><b>${esc(value)}</b></div>`; }
function severityCounts(items=[]) { const counts = {ERROR:0, WARN:0, INFO:0}; for (const item of items) counts[item.severity] = (counts[item.severity] || 0) + 1; return counts; }
function statusKind(items=[]) { const counts = severityCounts(items); if (counts.ERROR) return 'error'; if (counts.WARN) return 'warn'; return 'ok'; }
function statusText(kind) { return kind === 'error' ? 'ERROR' : kind === 'warn' ? 'WARN' : 'OK'; }
function isInitialized(data) { const diagnostics = data.diagnostics || []; return !diagnostics.some(d => String(d.message).includes('Missing .ai-agent/rulebridge.yaml')); }

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
  const prevRoot = state.root;
  readControls();
  if (prevRoot && state.root !== prevRoot) {
    // 切换项目目录：读取该目录的持久化进度
    state.stepFlags = loadFlags(state.root);
  }
  state.data = await getJson('/api/inspect', {root: state.root, target: state.target});
  render(state.data);
}

function payload() { return {root: state.root, target: state.target, force: state.force, insert_managed_block: state.insertManagedBlock}; }

async function runAction(action) {
  readControls();
  state.action = action;
  let result;
  if (action === 'inspect') result = await getJson('/api/inspect', {root: state.root, target: state.target});
  else if (action === 'validate') result = await getJson('/api/validate', {root: state.root, target: state.target});
  else if (action === 'doctor') result = await getJson('/api/doctor', {root: state.root, target: state.target});
  else if (action === 'diff') result = await postJson('/api/diff', payload());
  else if (action === 'dry-run') result = await postJson('/api/sync', {...payload(), dry_run: true});
  else if (action === 'init') {
    result = await postJson('/api/init', {root: state.root, force: state.force});
    state.stepFlags = { diff: false, dryrun: false, sync: false };
    saveFlags(state.root, state.stepFlags);
    state.data = await getJson('/api/inspect', {root: state.root, target: state.target});
  }
  else if (action === 'sync') {
    if (!confirm(t('confirm.sync'))) return;
    result = await postJson('/api/sync', {...payload(), dry_run: false});
  }
  // 推进 wizard 进度标记
  if (action === 'diff') state.stepFlags.diff = true;
  else if (action === 'dry-run') state.stepFlags.dryrun = true;
  else if (action === 'sync') state.stepFlags.sync = true;
  saveFlags(state.root, state.stepFlags);
  if (action === 'inspect') state.data = result;
  else if (state.data) Object.assign(state.data, result);
  else state.data = await getJson('/api/inspect', {root: state.root, target: state.target});
  render(state.data, result);
}

async function packAction(name, enabled) {
  readControls();
  const result = await postJson(enabled ? '/api/pack/enable' : '/api/pack/disable', {root: state.root, name});
  state.data = await getJson('/api/inspect', {root: state.root, target: state.target});
  state.action = enabled ? 'pack-enable' : 'pack-disable';
  // 切换 pack 后重新预览/dryrun/sync 结果可能变化，重置后续进度
  state.stepFlags.dryrun = false;
  state.stepFlags.sync = false;
  saveFlags(state.root, state.stepFlags);
  render(state.data, result);
}

async function packDiff(name) {
  readControls();
  const result = await postJson('/api/pack/diff', {root: state.root, name});
  state.action = 'pack-diff';
  const box = $(`pack-preview-${name}`);
  if (box) {
    const loaded = box.dataset.loaded === '1' && !box.hidden;
    if (loaded) { box.hidden = true; box.dataset.loaded = '0'; }
    else { box.innerHTML = `<pre>${esc(result.diff || '# ' + t('diff.empty'))}</pre>`; box.hidden = false; box.dataset.loaded = '1'; }
  }
  render(state.data || await getJson('/api/inspect', {root: state.root, target: state.target}), {diagnostics: result.diagnostics || []});
}

async function shutdown() {
  if (!confirm(t('confirm.shutdown'))) return;
  try { await postJson('/api/shutdown', {root: state.root}); } catch(e) { /* 服务关闭后连接中断，忽略 */ }
  const mask = document.createElement('div');
  mask.className = 'shutdown-mask';
  mask.innerHTML = `<div class="shutdown-card"><div class="shutdown-ico">⏻</div><h3>${t('shutdown.title')}</h3><p>${t('shutdown.msg')}</p><p class="muted">${t('shutdown.hint')}</p></div>`;
  document.body.appendChild(mask);
}

function topStat(label, value, kind='neutral') { return `<div class="top-stat ${kind}"><b>${esc(value)}</b><span>${esc(label)}</span></div>`; }
function category(path) {
  const p = String(path).replace(/\\/g, '/');
  if (p === 'AGENTS.md') return 'codex'; if (p === 'CLAUDE.md' || p.startsWith('.claude/')) return 'claude'; if (p.startsWith('.cursor/')) return 'cursor'; if (p.startsWith('.zcode/')) return 'zcode'; if (p.startsWith('.trae/')) return 'trae'; if (p.startsWith('.githooks/')) return 'git'; if (p === '.mcp.json') return 'mcp'; if (p.startsWith('.codebuddy-plugin/')) return 'codebuddy'; if (p.startsWith('.workbuddy-plugin/')) return 'workbuddy'; return 'generic';
}

// ===== 小白引导 Wizard 状态机 =====
function computeProgress(data) {
  const initialized = isInitialized(data);
  const diags = data.diagnostics || [];
  const hasError = diags.some(d => d.severity === 'ERROR');
  const hasWarn = diags.some(d => d.severity === 'WARN');
  const steps = [
    { id: 'dir', title: t('wiz.dir') },
    { id: 'init', title: t('wiz.init') },
    { id: 'validate', title: t('wiz.validate') },
    { id: 'diff', title: t('wiz.diff') },
    { id: 'dryrun', title: t('wiz.dryrun') },
    { id: 'sync', title: t('wiz.sync') },
    { id: 'done', title: t('wiz.done') },
  ];
  const done = new Set();
  if (state.root && state.root !== state.defaultRoot) done.add('dir');
  if (initialized) done.add('init');
  if (initialized && !hasError) done.add('validate');
  if (state.stepFlags.diff) done.add('diff');
  if (state.stepFlags.dryrun) done.add('dryrun');
  if (state.stepFlags.sync && !hasError) done.add('sync');
  if (state.stepFlags.sync && !hasError && !hasWarn) done.add('done');
  let current;
  if (!initialized) current = 'init';
  else if (hasError) current = 'validate';
  else if (!state.stepFlags.diff) current = 'diff';
  else if (!state.stepFlags.dryrun) current = 'dryrun';
  else if (!state.stepFlags.sync) current = 'sync';
  else current = 'done';
  return { steps, done, current, initialized, hasError, hasWarn };
}

function renderGuide(data) {
  const prog = computeProgress(data);
  const progressItems = prog.steps.map(s => {
    let cls = '';
    if (prog.done.has(s.id)) cls = 'done';
    else if (s.id === prog.current) cls = 'current';
    const dot = prog.done.has(s.id) ? '✓' : (s.id === prog.current ? '→' : '');
    return `<li class="${cls}"><span class="dot">${dot}</span><span class="label">${esc(s.title)}</span></li>`;
  }).join('');
  return `<ul class="wizard-progress">${progressItems}</ul>${renderWizardStep(prog)}`;
}

function renderWizardStep(prog) {
  const dirHint = `<div class="wizard-hint">${t('wiz.init.dirhint', { root: `<code>${esc(state.root)}</code>` })}</div>`;
  const cur = prog.current;
  if (cur === 'init') {
    return `
      <div class="wizard-step">
        <div class="step-head"><span class="step-num">1</span><h3>${t('wiz.init.title')}</h3></div>
        <p>${t('wiz.init.desc')}</p>
        ${dirHint}
        <div class="btn-row"><button data-action="init">${t('wiz.init.btn')}</button><button class="secondary" data-action="inspect">${t('wiz.init.refresh')}</button></div>
      </div>`;
  }
  if (cur === 'validate') {
    return `
      <div class="wizard-step">
        <div class="step-head"><span class="step-num">2</span><h3>${t('wiz.validate.title')}</h3></div>
        <p>${t('wiz.validate.desc')}</p>
        <div class="btn-row"><button data-action="doctor">${t('wiz.validate.doctor')}</button><button class="secondary" data-action="validate">${t('wiz.validate.validate')}</button><button class="secondary" data-action="inspect">${t('wiz.validate.refresh')}</button></div>
      </div>`;
  }
  if (cur === 'diff') {
    return `
      <div class="wizard-step">
        <div class="step-head"><span class="step-num">3</span><h3>${t('wiz.diff.title')}</h3></div>
        <p>${t('wiz.diff.desc')}</p>
        <div class="btn-row"><button data-action="diff">${t('wiz.diff.btn')}</button><button class="secondary" data-action="doctor">${t('wiz.diff.doctor')}</button></div>
      </div>`;
  }
  if (cur === 'dryrun') {
    return `
      <div class="wizard-step">
        <div class="step-head"><span class="step-num">4</span><h3>${t('wiz.dryrun.title')}</h3></div>
        <p>${t('wiz.dryrun.desc')}</p>
        <div class="btn-row"><button class="warn" data-action="dry-run">${t('wiz.dryrun.btn')}</button><button class="secondary" data-action="diff">${t('wiz.dryrun.back')}</button></div>
      </div>`;
  }
  if (cur === 'sync') {
    return `
      <div class="wizard-step">
        <div class="step-head"><span class="step-num">5</span><h3>${t('wiz.sync.title')}</h3></div>
        <p>${t('wiz.sync.desc')}</p>
        <div class="btn-row"><button class="danger" data-action="sync">${t('wiz.sync.btn')}</button><button class="secondary" data-action="dry-run">${t('wiz.sync.dryrun')}</button></div>
      </div>`;
  }
  return `
    <div class="wizard-step">
      <div class="step-head"><span class="step-num">✓</span><h3>${t('wiz.done.title')}</h3></div>
      <p>${t('wiz.done.desc')}</p>
      <div class="wizard-hint ok">${t('wiz.done.hint')}</div>
      <div class="btn-row"><button class="secondary" data-action="inspect">${t('wiz.done.refresh')}</button><button class="secondary" data-action="diff">${t('wiz.done.repreview')}</button></div>
    </div>`;
}

function renderResources(source) {
  const rules = table([t('res.name'), t('res.title'), t('res.path'), t('res.source'), t('res.pack')], source.rules.map(r => [esc(r.name), esc(r.title), `<code>${esc(r.path)}</code>`, esc(r.source), esc(r.pack)]), t('res.noRules'));
  const skills = table([t('res.name'), t('res.path'), t('res.source'), t('res.pack')], source.skills.map(s => [esc(s.name), `<code>${esc(s.path)}</code>`, esc(s.source), esc(s.pack)]), t('res.noSkills'));
  const commands = table([t('res.name'), t('res.path'), t('res.source'), t('res.pack')], source.commands.map(c => [esc(c.name), `<code>${esc(c.path)}</code>`, esc(c.source), esc(c.pack)]), t('res.noCommands'));
  const hooks = table([t('res.event'), t('res.steps'), t('res.targets'), t('res.path'), t('res.source')], source.hooks.map(h => [esc(h.event), esc(h.steps), esc((h.targets||[]).join(', ') || 'all'), `<code>${esc(h.path)}</code>`, esc(h.source)]), t('res.noHooks'));
  const mcp = table([t('res.name'), t('res.state'), t('res.command'), t('res.targets'), t('res.path'), t('res.source')], source.mcpServers.map(m => [esc(m.name), badge(m.enabled ? t('res.enabled') : t('res.disabled'), m.enabled ? 'ok' : 'neutral'), `<code>${esc(m.command)}</code>`, esc((m.targets||[]).join(', ') || 'all'), `<code>${esc(m.path)}</code>`, esc(m.source)]), t('res.noMcp'));
  $('resourcesBody').innerHTML = `<div class="resource-grid"><section class="mini-card"><h3>${t('res.rules')}</h3>${rules}</section><section class="mini-card"><h3>${t('res.skills')}</h3>${skills}</section><section class="mini-card"><h3>${t('res.commands')}</h3>${commands}</section><section class="mini-card"><h3>${t('res.hooks')}</h3>${hooks}</section><section class="mini-card wide"><h3>${t('res.mcp')}</h3>${mcp}</section></div>`;
}

function renderPacks(packs) {
  if (!packs || !packs.length) {
    $('packsBody').innerHTML = `<div class="pack-empty">${t('pack.empty')}</div>`;
    return;
  }
  const rows = packs.map(p => `
    <div class="pack-row ${p.enabled ? 'enabled' : ''}">
      <div class="pack-meta">
        <div class="pack-title">${esc(p.title || p.name)} ${badge(p.enabled ? t('pack.enabled') : t('pack.disabled'), p.enabled ? 'ok' : 'neutral')}${p.license === 'review-required' ? ' ' + badge(t('pack.review'), 'warn') : ''}</div>
        <div class="pack-desc">${esc(p.description || '无描述')}</div>
        <div class="pack-sub"><span>${t('pack.name')}:<code>${esc(p.name)}</code></span><span>${t('pack.target')}:<code>${esc((p.targets||[]).join(', ') || 'all')}</code></span>${p.license ? `<span>${t('pack.license')}:<code>${esc(p.license)}</code></span>` : ''}</div>
      </div>
      <div class="pack-actions">
        <button class="secondary pack-diff" data-pack="${esc(p.name)}">${t('pack.preview')}</button>
        ${p.enabled ? `<button class="warn pack-disable" data-pack="${esc(p.name)}">${t('pack.disable')}</button>` : `<button class="pack-enable" data-pack="${esc(p.name)}">${t('pack.enable')}</button>`}
      </div>
      <div class="pack-preview" id="pack-preview-${esc(p.name)}" hidden></div>
    </div>`);
  $('packsBody').innerHTML = `<div class="pack-list">${rows.join('')}</div>`;
  document.querySelectorAll('.pack-enable').forEach(btn => btn.onclick = () => packAction(btn.dataset.pack, true).catch(showError));
  document.querySelectorAll('.pack-disable').forEach(btn => btn.onclick = () => packAction(btn.dataset.pack, false).catch(showError));
  document.querySelectorAll('.pack-diff').forEach(btn => btn.onclick = () => packDiff(btn.dataset.pack).catch(showError));
}

function renderDiffs(diffs) {
  if (!diffs.length) return `<p class="muted">${t('diff.empty')}</p>`;
  return diffs.map((item, idx) => `<details ${idx < 2 ? 'open' : ''}><summary><code>${esc(item.file.path)}</code></summary><pre>${esc(item.diff || '# no changes\n')}</pre></details>`).join('');
}

function bindActionButtons() {
  document.querySelectorAll('button[data-action]').forEach(btn => btn.onclick = () => runAction(btn.dataset.action).catch(showError));
}

function render(data, result={}) {
  applyStaticI18n();
  const source = data.source || {project:{name:'RuleBridge Project'}, rules:[], skills:[], commands:[], hooks:[], mcpServers:[]};
  const diagnostics = result.diagnostics || data.diagnostics || [];
  const counts = severityCounts(diagnostics);
  const kind = statusKind(diagnostics);
  const packs = data.packs || [];
  const files = data.files || [];
  const enabledPacks = packs.filter(p => p.enabled).length;

  document.body.className = `theme-${state.theme === 'light' ? 'light' : 'dark'}`;
  // 顶部统计（仅数据，不含操作按钮）
  $('topstats').innerHTML = [
    topStat(t('stat.rules'), source.rules.length),
    topStat(t('stat.errors'), counts.ERROR, 'error'),
    topStat(t('stat.warnings'), counts.WARN, 'warn'),
    badge(statusText(kind), kind),
  ].join('');
  // 图标按钮组（语言 / 主题 / 停止）→ brandbox 内
  const langLabel = state.lang === 'zh' ? 'CN' : 'EN';
  const themeIcon = state.theme === 'dark' ? '☀️' : '🌙';
  $('iconBtnGroup').innerHTML = [
    `<button class="icon-btn" id="langBtn" title="${t('ui.lang')}">${langLabel}</button>`,
    `<button class="icon-btn" id="themeBtn" title="${state.theme==='dark'?t('ui.light'):t('ui.dark')}">${themeIcon}</button>`,
    `<button class="icon-btn danger" id="shutdownBtn" title="${t('ui.stop')}">⏻</button>`,
  ].join('');
  $('langBtn').onclick = () => { state.lang = state.lang === 'zh' ? 'en' : 'zh'; saveLang(state.lang); document.documentElement.lang = state.lang === 'zh' ? 'zh-CN' : 'en'; render(state.data || data, result); };
  $('themeBtn').onclick = () => { state.theme = state.theme === 'dark' ? 'light' : 'dark'; saveTheme(state.theme); render(state.data || data, result); };
  $('shutdownBtn').onclick = () => shutdown().catch(showError);

  const targetSelect = $('targetSelect');
  targetSelect.innerHTML = `<option value="">${t('settings.allTargets')}</option>` + (data.targets || []).map(tg => `<option value="${esc(tg)}" ${state.target===tg?'selected':''}>${esc(tg)}</option>`).join('');
  $('rootInput').value = state.root;
  $('forceInput').checked = state.force;
  $('insertInput').checked = state.insertManagedBlock;

  $('guideBody').innerHTML = renderGuide(data);
  $('monitor').innerHTML = metric(t('mon.action'), state.action) + metric(t('mon.status'), statusText(kind)) + metric(t('mon.files'), files.length) + metric(t('mon.packs'), `${enabledPacks}/${packs.length}`);
  $('dashboardMetrics').innerHTML = [
    metric(t('dash.project'), source.project?.name || ''),
    metric(t('dash.rules'), source.rules.length),
    metric(t('dash.skills'), source.skills.length),
    metric(t('dash.commands'), source.commands.length),
    metric(t('dash.hooks'), source.hooks.length),
    metric(t('dash.mcp'), source.mcpServers.length),
    metric(t('dash.generated'), files.length),
    metric(t('dash.errors'), counts.ERROR),
    metric(t('dash.warnings'), counts.WARN),
  ].join('');
  renderResources(source);
  $('generatedBody').innerHTML = table([t('gen.path'), t('gen.category'), t('gen.mode')], files.map(f => [`<code>${esc(f.path)}</code>`, badge(category(f.path),'neutral'), badge(f.managed ? t('gen.managed') : t('gen.unmanaged'), f.managed?'ok':'warn')]), t('gen.empty'));
  $('diagnosticsBody').innerHTML = table([t('diag.severity'), t('diag.message'), t('diag.path')], diagnostics.map(d => [badge(d.severity, d.severity.toLowerCase()), esc(d.message), `<code>${esc(d.path)}</code>`]), t('diag.empty'));
  renderPacks(packs);
  $('writeResultsBody').innerHTML = table([t('wr.status'), t('wr.path'), t('wr.message')], (result.results||[]).map(r => [badge(r.status, r.status === 'skipped' ? 'warn' : 'ok'), `<code>${esc(r.path)}</code>`, esc(r.message)]), t('wr.empty'));
  $('diffBody').innerHTML = renderDiffs(result.diffs || []);
  bindActionButtons();
}

function showError(err) { $('diagnosticsBody').innerHTML = table([t('diag.severity'), t('diag.message'), t('diag.path')], [[badge(t('err.error'),'error'), esc(err.message || err), '']], ''); }

// 根目录输入回车刷新
$('rootInput').addEventListener('keydown', (e) => { if (e.key === 'Enter') inspect().catch(showError); });

// 关闭浏览器标签页前提醒用户先停止服务
window.addEventListener('beforeunload', (e) => {
  // 如果已经显示了 shutdown 遮罩，不再拦截（允许直接关）
  if (document.querySelector('.shutdown-mask')) return;
  e.preventDefault();
  // Chrome/Firefox: 设置 returnValue 会显示确认对话框
  e.returnValue = t('unload');
  return e.returnValue;
});

// 初始化语言与静态文案
document.documentElement.lang = state.lang === 'zh' ? 'zh-CN' : 'en';
applyStaticI18n();
bindActionButtons();
inspect().catch(showError);
