// Windify Academy Color Palette
export const COLORS = {
  // Primary colors
  primary: '#F25A23',
  primaryLight: '#F19255',
  
  // Secondary colors
  secondary: '#224976',
  
  // Status colors
  success: '#10B981',
  warning: '#F59E0B',
  error: '#EF4444',
  info: '#3B82F6',
  
  // Neutral colors
  gray: {
    50: '#F9FAFB',
    100: '#F3F4F6',
    200: '#E5E7EB',
    300: '#D1D5DB',
    400: '#9CA3AF',
    500: '#6B7280',
    600: '#4B5563',
    700: '#374151',
    800: '#1F2937',
    900: '#111827',
  },
  
  // Background colors
  background: {
    primary: '#FFFFFF',
    secondary: '#F9FAFB',
    accent: '#FEF3F2',
  },
  
  // Text colors
  text: {
    primary: '#111827',
    secondary: '#6B7280',
    muted: '#9CA3AF',
  }
}

// CSS Custom Properties for Tailwind CSS
export const CSS_VARIABLES = {
  '--color-primary': COLORS.primary,
  '--color-primary-light': COLORS.primaryLight,
  '--color-secondary': COLORS.secondary,
}

// Tailwind CSS color classes mapping
export const TAILWIND_COLORS = {
  primary: 'text-[#F25A23]',
  primaryLight: 'text-[#F19255]',
  primaryBg: 'bg-[#F25A23]',
  primaryLightBg: 'bg-[#F19255]',
  primaryBorder: 'border-[#F25A23]',
  primaryLightBorder: 'border-[#F19255]',
  primaryHover: 'hover:bg-[#F25A23]',
  primaryLightHover: 'hover:bg-[#F19255]',
}

// Gradient utilities
export const GRADIENTS = {
  primary: 'linear-gradient(135deg, #F25A23 0%, #F19255 100%)',
  primaryReverse: 'linear-gradient(135deg, #F19255 0%, #F25A23 100%)',
}
