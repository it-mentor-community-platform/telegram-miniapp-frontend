import { definePreset } from '@primeuix/themes'
import Aura from '@primeuix/themes/aura'

// Tonal chips and tiles: a pale background with a darker same-hue foreground in light mode, a
// translucent tint with a light foreground in dark mode. Used through the tint-* utilities.
const lightTint = (hue: string) => ({ background: `{${hue}.50}`, color: `{${hue}.700}` })
const darkTint = (hue: string, shade = 400) => ({
  background: `color-mix(in srgb, {${hue}.${shade}} 16%, transparent)`,
  color: `{${hue}.300}`,
})

export const AppPreset = definePreset(Aura, {
  semantic: {
    colorScheme: {
      light: {
        // Darker emerald than Aura's default so that white text on primary buttons meets WCAG AA
        // (see design/README.md, Design conventions).
        primary: {
          color: '{emerald.700}',
          contrastColor: '#ffffff',
          hoverColor: '{emerald.800}',
          activeColor: '{emerald.900}',
        },
        app: { background: '{surface.50}' },
        subtle: { color: '{surface.400}' },
        tint: {
          success: lightTint('emerald'),
          warn: lightTint('orange'),
          info: lightTint('blue'),
          help: lightTint('violet'),
          neutral: { background: '{surface.100}', color: '{surface.700}' },
        },
        roadmap: { segment: { background: '{content.border.color}', filledBackground: '{emerald.500}' } },
      },
      dark: {
        primary: {
          color: '{emerald.400}',
          contrastColor: '{emerald.950}',
          hoverColor: '{emerald.300}',
          activeColor: '{emerald.200}',
        },
        app: { background: '{surface.950}' },
        subtle: { color: '{surface.500}' },
        tint: {
          success: darkTint('emerald'),
          warn: darkTint('orange', 500),
          info: darkTint('blue'),
          help: darkTint('violet'),
          neutral: { background: '{surface.800}', color: '{surface.300}' },
        },
        roadmap: { segment: { background: '{surface.700}', filledBackground: '{emerald.400}' } },
      },
    },
  },
  components: {
    // Mockup cards: 1px border, 1rem padding, a faint shadow in light mode only.
    card: {
      body: { padding: '1rem', gap: '1rem' },
      colorScheme: {
        light: { root: { shadow: '0 1px 2px rgb(15 23 42 / 0.04)' } },
        dark: { root: { shadow: 'none' } },
      },
      css: ({ dt }) => `
        .p-card {
          border: 1px solid ${dt('content.border.color')};
        }
      `,
    },
    // Mockup tags: 12/16 px semibold text.
    tag: {
      root: { fontSize: '0.75rem', fontWeight: '600', padding: '0.125rem 0.5rem' },
      css: () => `
        .p-tag {
          line-height: 1rem;
        }
      `,
    },
    // Defaults match the list-row icon tile; other sizes are set per use.
    avatar: {
      root: {
        width: '2.5rem',
        height: '2.5rem',
        borderRadius: '0.625rem',
        background: '{tint.neutral.background}',
        color: '{tint.neutral.color}',
      },
      icon: { size: '1.125rem' },
    },
  },
})
