import { definePreset } from '@primeuix/themes'
import Aura from '@primeuix/themes/aura'

// Darker emerald than Aura's default so that white text on primary buttons meets WCAG AA
// (see design/README.md, Design conventions).
export const AppPreset = definePreset(Aura, {
  semantic: {
    colorScheme: {
      light: {
        primary: {
          color: '{emerald.700}',
          contrastColor: '#ffffff',
          hoverColor: '{emerald.800}',
          activeColor: '{emerald.900}',
        },
      },
      dark: {
        primary: {
          color: '{emerald.400}',
          contrastColor: '{emerald.950}',
          hoverColor: '{emerald.300}',
          activeColor: '{emerald.200}',
        },
      },
    },
  },
})
