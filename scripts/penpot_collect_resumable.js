// Read-only bounded collection. Require two identical full-file passes before
// publishing immutable evidence. Never mix facts from different captures.
storage.conformanceTransfer = null;
storage.conformanceSnapshot = null;
const normalizeFamily = value => value.split('/').map(p => p.trim()).join('/');
const family = c => c ? normalizeFamily(c.name.includes('/') ? c.name : `${c.path}/${c.name}`) : null;
const fileId = penpot.currentFile.id;
const startedAt = Date.now();
const makePass = () => ({pages: [], nodes: [], records: [], seen: new Set(),
  pageIndex: 0, pending: [], pageId: null, catalogue: null, recordIndex: 0, recordMap: new Map()});
const state = {pass: makePass(), first: null, done: false, failed: false};
const fail = error => {
  state.failed = true;
  storage.conformanceSnapshot = {version: auditRequest.version, fingerprint: auditRequest.fingerprint,
    fileId, fileName: auditRequest.fileName, capturedAt: new Date(startedAt).toISOString(),
    coverage: 'full-file', complete: false, collectionErrors: [String(error.message ?? error)],
    pages: state.pass.pages, nodes: state.pass.nodes, records: state.pass.records};
  storage.conformanceTransfer = null;
  return {done: false, failed: true, errors: storage.conformanceSnapshot.collectionErrors};
};
storage.conformanceCollectStep = () => {
  if (state.failed) return {done: false, failed: true};
  if (state.done) return {done: true, nodes: storage.conformanceSnapshot.nodes.length};
  const batchStarted = Date.now();
  let count = 0;
  try {
    if (penpot.currentFile.id !== fileId || penpot.currentFile.name !== auditRequest.fileName) throw Error('Generated file identity changed');
    if (Date.now() - startedAt > 600000) throw Error('Resumable collection total bound exceeded');
    const pass = state.pass;
    while (count < 50 && Date.now() - batchStarted < 3000) {
      if (pass.pending.length) {
        if (pass.seen.size >= 20000) throw Error('Collection shape bound exceeded');
        const [n, parent] = pass.pending.pop();
        if (pass.seen.has(n.id)) throw Error(`Duplicate/cyclic shape ${n.id}`);
        pass.seen.add(n.id);
        const c = n.component?.();
        const rawOpacity = n.opacity;
        pass.nodes.push({id: n.id, parent, pageId: pass.pageId, type: n.type, name: n.name,
          hidden: n.hidden, rawOpacity, opacitySource: rawOpacity === null ? 'penpot-null-default-v1' : 'explicit',
          opacity: rawOpacity === null ? 1 : rawOpacity, bounds: [n.x, n.y, n.width, n.height],
          fills: n.fills, text: n.type === 'text' ? n.characters : null,
          copy: n.isComponentCopyInstance(), head: n.isComponentHead(), family: family(c), componentId: c?.id ?? null,
          refId: n.componentRefShape()?.id ?? null, variant: c?.variantProps ?? {},
          auditKey: n.getPluginData('auditKey') || null, slot: n.getPluginData('auditSlot') || null,
          variantContainer: n.isVariantContainer(),
          variantMembers: n.isVariantContainer() ? (n.variants?.variantComponents() ?? []).map(c => c.id).sort() : []});
        for (const child of [...(n.children ?? [])].reverse()) pass.pending.push([child, n.id]);
        count++;
      } else if (pass.pageIndex < penpot.currentFile.pages.length) {
        const page = penpot.currentFile.pages[pass.pageIndex++];
        pass.pages.push({id: page.id, name: page.name});
        pass.pageId = page.id;
        pass.pending = [...page.root.children].reverse().map(n => [n, null]);
      } else {
        if (pass.catalogue === null) pass.catalogue = [...penpot.library.local.components];
        if (pass.recordIndex < pass.catalogue.length) {
          const representative = pass.catalogue[pass.recordIndex++];
          const variants = representative.isVariant() ? representative.variants : null;
          if (representative.isVariant() && !variants) throw Error(`Missing native variant set ${representative.id}`);
          const members = variants ? variants.variantComponents() : [representative];
          if (!members.length || !members.some(c => c.id === representative.id)) throw Error(`Incomplete native variant set ${representative.id}`);
          for (const c of members) {
            const record = {id: c.id, family: family(c), mainId: c.mainInstance()?.id ?? null, variant: c.variantProps ?? {}};
            if (pass.recordMap.has(c.id) && JSON.stringify(pass.recordMap.get(c.id)) !== JSON.stringify(record)) throw Error(`Conflicting component record ${c.id}`);
            pass.recordMap.set(c.id, record);
          }
          count++;
        } else {
          pass.records = [...pass.recordMap.values()];
          const stable = {pages: [...pass.pages].sort((a,b)=>a.id.localeCompare(b.id)),
            nodes: [...pass.nodes].sort((a,b)=>a.id.localeCompare(b.id)),
            records: [...pass.records].sort((a,b)=>a.id.localeCompare(b.id))};
          // Preserve nested property values; sort only entity order.
          const serialized = JSON.stringify(stable);
          if (state.first === null) {
            state.first = serialized;
            state.pass = makePass();
            return {done: false, pass: 2, nodes: 0};
          }
          if (state.first !== serialized) throw Error('File changed between complete collection passes; restart capture');
          storage.conformanceSnapshot = {version: auditRequest.version, fingerprint: auditRequest.fingerprint,
            capturedAt: new Date(startedAt).toISOString(), fileId, fileName: auditRequest.fileName,
            complete: true, coverage: 'full-file', collectionErrors: [],
            pages: pass.pages, nodes: pass.nodes, records: pass.records};
          state.done = true;
          return {done: true, nodes: pass.nodes.length, records: pass.records.length, passes: 2};
        }
      }
    }
    return {done: false, pass: state.first === null ? 1 : 2, nodes: pass.nodes.length};
  } catch (error) { return fail(error); }
};
return storage.conformanceCollectStep();