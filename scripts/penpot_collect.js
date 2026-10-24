// Read-only fact collector. auditRequest is supplied by the Python emitter.
const snapshot = {
  version: auditRequest.version, fingerprint: auditRequest.fingerprint,
  capturedAt: new Date().toISOString(), fileId: penpot.currentFile.id,
  fileName: penpot.currentFile.name, complete: false,
  coverage: 'full-file',
  collectionErrors: [], pages: [], nodes: [], records: []
};
const normalizeFamily = value => value.split('/').map(p => p.trim()).join('/');
const family = c => c ? normalizeFamily(c.name.includes('/') ? c.name : `${c.path}/${c.name}`) : null;
const seen = new Set();
const started = Date.now();
try {
  if (snapshot.fileName !== auditRequest.fileName) throw Error('Wrong generated file');
  for (const page of penpot.currentFile.pages) {
    snapshot.pages.push({id: page.id, name: page.name});
    const pending = [...page.root.children].reverse().map(n => [n, null]);
    while (pending.length) {
      if (seen.size >= 20000 || Date.now() - started > 15000) throw Error('Collection bound exceeded');
      const [n, parent] = pending.pop();
      if (seen.has(n.id)) throw Error(`Duplicate/cyclic shape ${n.id}`);
      seen.add(n.id);
      const c = n.component?.();
      // The plugin getter exposes stored nil as null; Penpot's renderer uses
      // (or opacity 1). Retain raw evidence rather than silently filling gaps.
      // Undefined, exceptions and invalid numeric values are NOT defaults.
      const rawOpacity = n.opacity;
      snapshot.nodes.push({
        id: n.id, parent, pageId: page.id, type: n.type, name: n.name,
        hidden: n.hidden, rawOpacity,
        opacitySource: rawOpacity === null ? 'penpot-null-default-v1' : 'explicit',
        opacity: rawOpacity === null ? 1 : rawOpacity,
        bounds: [n.x, n.y, n.width, n.height],
        fills: n.fills,
        text: n.type === 'text' ? n.characters : null,
        copy: n.isComponentCopyInstance(), head: n.isComponentHead(),
        family: family(c), componentId: c?.id ?? null,
        refId: n.componentRefShape()?.id ?? null,
        variant: c?.variantProps ?? {},
        auditKey: n.getPluginData('auditKey') || null,
        slot: n.getPluginData('auditSlot') || null,
        variantContainer: n.isVariantContainer(),
        variantMembers: n.isVariantContainer() ? (n.variants?.variantComponents() ?? []).map(c => c.id).sort() : []
      });
      for (const child of [...(n.children ?? [])].reverse()) pending.push([child, n.id]);
    }
  }
  // The local catalogue exposes one representative per variant family, not
  // every State record. Enumerate the native variant set before deduplicating.
  const records = new Map();
  for (const representative of penpot.library.local.components) {
    const variants = representative.isVariant() ? representative.variants : null;
    if (representative.isVariant() && !variants) throw Error(`Missing native variant set ${representative.id}`);
    const members = variants ? variants.variantComponents() : [representative];
    if (!members.length || !members.some(c => c.id === representative.id)) {
      throw Error(`Incomplete native variant set ${representative.id}`);
    }
    for (const c of members) {
      const record = {id: c.id, family: family(c), mainId: c.mainInstance()?.id ?? null,
                      variant: c.variantProps ?? {}};
      if (records.has(c.id) && JSON.stringify(records.get(c.id)) !== JSON.stringify(record)) {
        throw Error(`Conflicting component record ${c.id}`);
      }
      records.set(c.id, record);
    }
  }
  snapshot.records = [...records.values()];
  snapshot.complete = true;
} catch (error) {
  snapshot.collectionErrors.push(String(error.message ?? error));
}
return snapshot;