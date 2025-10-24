# Saber Brand Implementation Guidelines

## Core Colours
```css
--saber-blue: #044D73;
--saber-green: #7CC061;
--dark-blue: #091922;
--dark-green: #0A2515;
--gradient-dark: #0d1138;
--white-98: rgba(255, 255, 255, 0.98);
```

## Typography
- **Headers (H1-H3)**: Montserrat ExtraBold, uppercase, letter-spacing: 0.05em
- **Subheaders (H4+)**: Montserrat SemiBold, uppercase, letter-spacing: 0.03em  
- **Body**: Source Sans Pro Regular
- **Import**: 
```html
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@600;800&family=Source+Sans+Pro:wght@400;600&display=swap" rel="stylesheet">
```

## Design Patterns

### 1. Cards
- White background (98% opacity)
- 16px border radius
- Backdrop blur effect
- Subtle green border on hover
- Box shadow with colour tint

### 2. Buttons
- **Primary**: Green gradient (#7CC061 to #95D47E)
- **Secondary**: Blue gradient (#044D73 to #0A5F8E)
- Hover lift animation (-4px translateY)
- Smooth transitions (0.3s ease)

### 3. Backgrounds
- Main: Dark gradient (#091922 to #0d1138)
- Energy pulse animations on gradients
- Glass morphism overlays where appropriate

### 4. Stats Cards
- Blue gradient background
- White text
- Green accent border animation
- Icon integration

## Key Visual Elements
- Energy pulse animations on gradients
- Glass morphism effects (backdrop-filter: blur)
- Box shadows with colour tints (green/blue)
- Hover states that lift elements (-4px translateY)
- Custom scrollbars with gradient thumbs
- Smooth transitions throughout (0.3s ease)

## Content Tone
- Lead with business outcomes, then technical details
- Use analogies for complex concepts
- Expert but approachable language
- No unexplained jargon
- Clear call-to-action messaging

## Essential CSS Classes
```css
.saber-card /* Glass card with hover lift */
.saber-btn /* Green gradient button */
.saber-btn-secondary /* Blue gradient button */
.stat-card /* Metric display with icon */
.saber-gradient /* Header gradient with energy animation */
.saber-container /* Content wrapper with max-width */
.saber-form /* Styled form elements */
```

## Must Include Elements
- Saber logo in header with white/transparent background container
- "Expert • Clear • Strategic" tagline where appropriate
- Footer with copyright and company positioning
- Icons from Font Awesome for visual hierarchy
- Responsive design for all screen sizes

## Form Styling
- Floating labels for modern UX
- Green focus states on inputs
- Validation feedback with colour coding
- Progress indicators for multi-step forms
- File upload areas with drag-and-drop

## Animation Guidelines
```css
/* Standard transition */
transition: all 0.3s ease;

/* Hover lift */
transform: translateY(-4px);

/* Energy pulse */
@keyframes pulse {
  0%, 100% { opacity: 0.8; }
  50% { opacity: 1; }
}

/* Gradient shift */
background-size: 200% 200%;
animation: gradient 15s ease infinite;
```

## Accessibility
- High contrast ratios (WCAG AA minimum)
- Focus indicators on all interactive elements
- Semantic HTML structure
- ARIA labels where needed
- Keyboard navigation support

## Responsive Breakpoints
- Mobile: < 768px
- Tablet: 768px - 1024px
- Desktop: > 1024px
- Wide: > 1440px

## Implementation Checklist
- [ ] Font imports loaded
- [ ] Colour variables defined
- [ ] Logo positioned correctly
- [ ] Glass morphism effects applied
- [ ] Animations smooth and performant
- [ ] Forms styled consistently
- [ ] Mobile responsive
- [ ] Accessibility tested