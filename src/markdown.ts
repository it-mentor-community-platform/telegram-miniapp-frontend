import MarkdownIt, { type Token } from 'markdown-it'

type Environment = { specialization?: string }
type Figure = { src: string; title?: string; alt?: string; caption?: string }

const sources = {
  java: { page: 'https://zhukovsd.github.io/java-backend-interview-prep/', images: 'https://zhukovsd.github.io/java-backend-interview-prep/' },
  python: { page: 'https://zhukovsd.github.io/python-backend-interview-prep/', images: 'https://raw.githubusercontent.com/zhukovsd/python-backend-interview-prep/master/assets/' },
}

function sourceFor(specialization?: string) {
  const name = specialization?.trim().replace(/\s+Backend$/i, '').toLowerCase()
  return name === 'java' || name === 'python' ? sources[name] : undefined
}

// Unknown relative paths must never resolve against the Mini App's own origin.
export function resolveAnswerUrl(value: string, specialization?: string, image = false): string | undefined {
  if (/[\u0000-\u001f\u007f\\]/.test(value)) return undefined
  const raw = value.trim()
  if (!raw) return undefined
  if (!image && raw.startsWith('#')) return raw
  try {
    const source = sourceFor(specialization)
    let base = image ? source?.images : source?.page
    if (/^\/(?:java|python)-backend-interview-prep\//.test(raw)) base = 'https://zhukovsd.github.io/'
    if (raw.startsWith('//')) base = 'https://zhukovsd.github.io/'
    const url = base ? new URL(raw, base) : new URL(raw)
    if (url.username || url.password) return undefined
    if (image ? url.protocol !== 'https:' : !['https:', 'http:', 'mailto:'].includes(url.protocol)) return undefined
    return url.href
  } catch {
    return undefined
  }
}

function parseFigure(value: string): { figure: Figure; length: number } | undefined {
  const match = /^\{\{<\s*figure\s+([^\n]*?)>\}\}/.exec(value)
  if (!match) return undefined
  const attributes = match[1]!.trim()
  const rule = /([a-z]+)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'=<>`]+))/gy
  const values: Record<string, string> = {}
  let pos = 0
  while (pos < attributes.length) {
    rule.lastIndex = pos
    const attribute = rule.exec(attributes)
    if (!attribute || !['src', 'title', 'alt', 'caption'].includes(attribute[1]!) || attribute[1]! in values) return undefined
    values[attribute[1]!] = attribute[2] ?? attribute[3] ?? attribute[4] ?? ''
    pos = rule.lastIndex
    if (pos < attributes.length && !/\s/.test(attributes[pos]!)) return undefined
    while (pos < attributes.length && /\s/.test(attributes[pos]!)) pos++
  }
  return values.src ? { figure: values as Figure, length: match[0].length } : undefined
}

// No arbitrary HTML/plugins: output is generated only by markdown-it and the escaped renderers below.
const markdown = new MarkdownIt({ html: false, linkify: true, typographer: false, breaks: false })
const escape = markdown.utils.escapeHtml

function renderImage(src: string, alt: string, title: string | undefined, env: Environment) {
  const url = resolveAnswerUrl(src, env.specialization, true)
  if (!url) return `<span class="markdown-image-error">${escape(alt || 'Изображение недоступно')}</span>`
  return `<img src="${escape(url)}" alt="${escape(alt)}"${title ? ` title="${escape(title)}"` : ''} loading="lazy" decoding="async" referrerpolicy="no-referrer">`
}

// Block/inline rules run after code recognition; never replace shortcodes in source with a regex.
markdown.block.ruler.before('paragraph', 'answer_figure', (state, line, _endLine, silent) => {
  if (state.sCount[line]! - state.blkIndent >= 4) return false
  const text = state.src.slice(state.bMarks[line]! + state.tShift[line]!, state.eMarks[line]!)
  const result = parseFigure(text)
  if (!result || text.slice(result.length).trim()) return false
  if (silent) return true
  const token = state.push('answer_figure', 'figure', 0)
  token.block = true
  token.meta = result.figure
  token.map = [line, line + 1]
  state.line = line + 1
  return true
}, { alt: ['paragraph', 'reference', 'blockquote', 'list'] })

markdown.inline.ruler.before('text', 'answer_figure', (state, silent) => {
  if (!state.src.startsWith('{{<', state.pos)) return false
  const result = parseFigure(state.src.slice(state.pos))
  if (!result || state.pos + result.length > state.posMax) return false
  if (!silent) state.push('answer_figure', 'span', 0).meta = result.figure
  state.pos += result.length
  return true
})

markdown.renderer.rules.answer_figure = (tokens, index, _options, env) => {
  const token = tokens[index]!
  const figure = token.meta as Figure
  const caption = figure.caption || figure.title
  const image = renderImage(figure.src, figure.alt || figure.title || 'Иллюстрация к ответу', figure.title, (env ?? {}) as Environment)
  if (token.block) return `<figure>${image}${caption ? `<figcaption>${escape(caption)}</figcaption>` : ''}</figure>\n`
  return `<span class="markdown-inline-figure" role="figure">${image}${caption ? `<span class="markdown-caption">${escape(caption)}</span>` : ''}</span>`
}

markdown.renderer.rules.image = (tokens, index, options, env, renderer) => {
  const token = tokens[index]!
  return renderImage(String(token.attrGet('src') ?? ''), renderer.renderInlineAsText(token.children ?? [], options, env), token.attrGet('title')?.toString(), (env ?? {}) as Environment)
}

markdown.core.ruler.after('inline', 'answer_links_and_headings', (state) => {
  const env = state.env as Environment
  function visit(tokens: Token[]) {
    const links: boolean[] = []
    for (const token of tokens) {
      if (token.type === 'heading_open' || token.type === 'heading_close') {
        // Answers are nested below the page's question heading; never introduce another h1/h2.
        token.tag = `h${Math.min(6, Number(token.tag.slice(1)) + 2)}`
      }
      if (token.type === 'link_open') {
        const href = resolveAnswerUrl(String(token.attrGet('href') ?? ''), env.specialization)
        links.push(Boolean(href))
        if (href) {
          token.attrSet('href', href)
          if (!href.startsWith('#')) {
            token.attrSet('target', '_blank')
            token.attrSet('rel', 'noopener noreferrer')
          }
        } else {
          token.tag = 'span'
          token.attrs = null
        }
      } else if (token.type === 'link_close' && !links.pop()) token.tag = 'span'
      if (token.children) visit(token.children)
    }
  }
  visit(state.tokens)
})

markdown.renderer.rules.table_open = () => '<div class="markdown-table" role="region" aria-label="Таблица в ответе" tabindex="0"><table>\n'
markdown.renderer.rules.table_close = () => '</table></div>\n'
const fence = markdown.renderer.rules.fence!
markdown.renderer.rules.fence = (...args) => fence(...args).replace('<pre>', '<pre tabindex="0">')
const codeBlock = markdown.renderer.rules.code_block!
markdown.renderer.rules.code_block = (...args) => codeBlock(...args).replace('<pre>', '<pre tabindex="0">')

export function renderAnswerMarkdown(text: string, specialization?: string): string {
  return markdown.render(text, { specialization } satisfies Environment)
}
