# Conga Brand Guidelines - Development Reference

## Brand Identity Summary
Conga is a business performance and revenue operations company. The brand voice is: straightforward but not stuffy, knowledgeable but not arrogant, innovative but customer-paced, expert but jargon-free.

---

## Color Palette

### Primary Corporate Colors
| Color | Hex | RGB | Usage |
|-------|-----|-----|-------|
| Conga Red | #E53535 | 229, 53, 53 | Primary brand color, CTAs, accents |
| Blue Harbor Light | #E3F0F4 | 227, 240, 244 | Light backgrounds, subtle accents |
| Charcoal Gray | #474542 | 71, 69, 66 | Dark text, secondary elements |

### Secondary Corporate Colors
| Color | Hex | RGB | Usage |
|-------|-----|-----|-------|
| White | #FFFFFF | 255, 255, 255 | Backgrounds, text on dark |
| Light Gray | #F1F2F2 | 241, 242, 242 | Subtle backgrounds (5% black) |
| Medium Gray | #BBBCBC | 187, 188, 188 | Borders, disabled states |
| Black | #000000 | 0, 0, 0 | Headlines, strong text |

### Product/Accent Colors
| Color | Hex | RGB | Usage |
|-------|-----|-----|-------|
| Blue Harbor | #48A9C5 | 72, 169, 197 | Product accents, secondary CTAs |

### Color Usage Rules
- Corporate palette is primary; use predominantly
- Product palette (Blue Harbor) reserved for product references only
- Red (#E53535) is the primary accent and call-to-action color
- Use white logo/text on red, charcoal, or dark backgrounds
- Maintain adequate contrast for readability (WCAG compliance)

---

## Typography

### Font Stack (CSS)
```css
/* Primary font stack */
font-family: 'Buenos Aires', 'Montserrat', 'Century Gothic', sans-serif;

/* For web projects, use Montserrat from Google Fonts as primary */
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;700&display=swap');
```

### Typography Hierarchy
| Element | Weight | Case | Color | Notes |
|---------|--------|------|-------|-------|
| Section Tags | Bold (700) | ALL CAPS | Conga Red (#E53535) | letter-spacing: 0.1em |
| Headlines (H1) | Bold (700) | Title Case | Black (#000000) | Large, impactful |
| Subheadings (H2-H3) | Regular (400) | Sentence case | Charcoal (#474542) | |
| Body Headlines | Bold (700) | Sentence case | Black (#000000) | |
| Body Text | Regular (400) | Sentence case | Charcoal (#474542) | |

### CSS Variables Example
```css
:root {
  /* Colors */
  --conga-red: #E53535;
  --blue-harbor-light: #E3F0F4;
  --blue-harbor: #48A9C5;
  --charcoal-gray: #474542;
  --light-gray: #F1F2F2;
  --medium-gray: #BBBCBC;
  
  /* Typography */
  --font-primary: 'Montserrat', 'Century Gothic', sans-serif;
  --font-weight-regular: 400;
  --font-weight-medium: 500;
  --font-weight-bold: 700;
}
```

---

## Tone of Voice Guidelines

### Writing Principles
- **Customer-focused**: Make the customer the hero, not Conga
- **Clear and concise**: Target 8th grade reading level
- **Active voice**: Preferred over passive voice
- **Contractions allowed**: we're, can't, don't, etc.
- **Oxford comma**: Always use serial comma
- **Sentence case**: For all titles, headlines, and subheaders

### Voice Characteristics

| Attribute | Do | Don't |
|-----------|----|----|
| Straightforward | Say what you mean with healthy levity | Be silly, whimsical, or stuffy |
| Knowledgeable | Share expertise graciously | Sound arrogant or condescending |
| Innovative | Solve big problems at customer's pace | Push everyone to move fast regardless of readiness |
| Expert | Make technology accessible, avoid jargon | Use overly technical language |
| Optimistic | Speak positively about possibilities | Over-promise or use hyperbole |
| Confident | Share what's possible humbly | Boast about awards or capabilities |

### Example Transformations

**Instead of:** "Leverage our innovative solutions to find new efficiencies"  
**Write:** "Streamline and automate to boost efficiency"

**Instead of:** "200+ million users can't be wrong"  
**Write:** "See why top companies love working with us"

**Instead of:** "The key to your digital transformation"  
**Write:** "Meet customer needs today with agility for tomorrow"

### Writing Style Rules
- Spell out numbers 0-9, use numerals for 10+
- Time format: "9 am PT" (no periods in am/pm)
- Dates as ordinals: "November 8th"
- Em dashes without spaces: "word—word"
- Single space after periods
- Avoid exclamation points (use very sparingly)

### Specific Terms & Spelling
| Correct | Incorrect |
|---------|-----------|
| eSignature | e-signature, E-signature |
| eBook | e-book, Ebook |
| eLearning | e-learning |
| Whitepaper | White paper |
| Data sheet | Datasheet |
| AI | A.I. |
| contract lifecycle management (CLM) | Contract Lifecycle Management |
| configure price quote (CPQ) | Configure Price Quote |

---

## Visual Elements

### Comets (Motion Graphics)
Visual motif representing acceleration and forward motion:
- Circle shape preceded by gradient tail
- Tail is 66-75% the height of the circle
- Tail and circle must be different colors
- Allowed colors: Conga Red, Blue Harbor Light, Charcoal Gray, White
- Use non-repetitive color combinations in clusters

### Snake Element
- Elongated comet that winds across composition
- Represents a path or journey
- Same color rules as Comets apply

### Swipe Pattern
- 45° angled lines with flush edges
- Gradient from White to Blue Harbor Light
- Use sparingly for dramatic reveals

### Design Patterns
- Emphasize circles and rounded elements (reflects logo shape)
- C-shape masks for images (curved crop)
- Rounded corners on UI elements
- Gradient overlays: White → Blue Harbor Light

---

## Component Styling Guide

### Buttons
```css
/* Primary Button */
.btn-primary {
  background-color: #E53535;
  color: #FFFFFF;
  border: none;
  border-radius: 4px;
  padding: 12px 24px;
  font-weight: 700;
  text-transform: none; /* Sentence case */
}

.btn-primary:hover {
  background-color: #c42e2e; /* Darker red */
}

/* Secondary Button */
.btn-secondary {
  background-color: transparent;
  color: #E53535;
  border: 2px solid #E53535;
  border-radius: 4px;
  padding: 10px 22px;
  font-weight: 700;
}

.btn-secondary:hover {
  background-color: #E53535;
  color: #FFFFFF;
}
```

### Cards & Containers
```css
.card {
  background-color: #FFFFFF;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  /* Or use subtle border */
  border: 1px solid #E3F0F4;
}

.card-light {
  background-color: #F1F2F2; /* Light Gray */
}

.card-accent {
  background-color: #E3F0F4; /* Blue Harbor Light */
}
```

### Form Elements
```css
.input {
  border: 1px solid #BBBCBC;
  border-radius: 4px;
  padding: 12px 16px;
  color: #474542;
}

.input:focus {
  border-color: #E53535;
  outline: none;
  box-shadow: 0 0 0 3px rgba(229, 53, 53, 0.1);
}

.label {
  color: #474542;
  font-weight: 500;
  margin-bottom: 8px;
}
```

### Navigation
```css
.nav-link {
  color: #474542;
  font-weight: 500;
  text-decoration: none;
}

.nav-link:hover,
.nav-link.active {
  color: #E53535;
}

.navbar {
  background-color: #FFFFFF;
  /* Or for accent header */
  background-color: #E3F0F4;
}
```

### Icons
- Use line icons with consistent stroke weights
- Colors: Charcoal Gray (#474542) or White on dark backgrounds
- Product family icons can have Blue Harbor Light (#E3F0F4) circular backgrounds

---

## Photography Guidelines

### Do Use
- Natural light photography
- Rich but not oversaturated colors
- Real, candid moments
- People as the focus
- Positive, upbeat professional settings
- Diverse representation

### Don't Use
- Overly dark or colorized images
- Scenes without people
- Graphic overlays on photos
- Overly posed or cliché corporate shots
- Distant subjects
- Abstract concept imagery

### Image Masking
- Circle masks (fully enclosed or subject breaking top)
- C-shape masks (curved crop, can bleed off edge)
- Red overlay allowed sparingly (Conga Red at 66-80% opacity, Multiply blend)

---

## Key Brand Messages

Use these phrases in headlines and hero sections:

| Message Type | Phrase |
|--------------|--------|
| Tagline | "Business Accelerated" |
| What we do | "Meet complexity with confidence" |
| Why we exist | "Growing your way" |

### Value Propositions
- **Operate with agility**: Adapt processes, focus on strategic work
- **Business results, accelerated**: Move at the speed of customers
- **Realize comprehensive value**: Comprehensive product set for any size business
- **Move with an expert at your side**: Backed by innovative collaborators

---

## Quick Reference - Tailwind CSS Classes

If using Tailwind, create these custom colors in your config:

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        'conga-red': '#E53535',
        'blue-harbor': '#48A9C5',
        'blue-harbor-light': '#E3F0F4',
        'charcoal': '#474542',
        'gray-light': '#F1F2F2',
        'gray-medium': '#BBBCBC',
      },
      fontFamily: {
        sans: ['Montserrat', 'Century Gothic', 'sans-serif'],
      },
    },
  },
}
```

---

## Logo Usage

### Primary Logo
- Red circle (#E53535) with white "conga" text inside
- Minimum size: 60px digital / 0.75 inches print

### Secondary Logo (Wordmark only)
- "conga" text in Conga Red
- Use when circle doesn't fit (small items, embroidery)
- Minimum size: 100px digital / 0.625 inches print

### Clear Space
- Minimum clear space = height of the "g" in logo
- Keep free of other elements, text, edges

### Logo Don'ts
- Don't distort or stretch
- Don't use unapproved colors
- Don't rotate
- Don't add effects (shadows, outlines)
- Don't place on low-contrast backgrounds
- Don't use legacy/old logo versions

---

*This reference document is derived from the Conga Brand Guidelines (January 2021). When in doubt, prioritize: customer focus, clarity, and the red/white/charcoal color scheme.*
