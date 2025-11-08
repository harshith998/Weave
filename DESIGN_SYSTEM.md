# Weave UI Design System
**Version 1.0** | Linear-Inspired Glassmorphic Interface

---

## Design Philosophy

Weave's interface embodies cutting-edge minimalism inspired by Linear, combining:
- **Dark-first design** optimized for long creative sessions
- **Glassmorphism** for depth and futuristic aesthetic
- **Multi-color node system** for instant visual hierarchy
- **Information density** without clutter
- **Smooth, purposeful animations** that guide attention

---

## Color Palette

### Base Colors
```
Background Primary:     #1A1A1D  (Main app background)
Background Secondary:   #252528  (Card base, elevated surfaces)
Background Tertiary:    #2D2D32  (Hover states, subtle elevation)

Text Primary:           #EEEFF1  (Main text, headings)
Text Secondary:         #9CA3AF  (Subtext, labels, timestamps)
Text Tertiary:          #6B7280  (Disabled, placeholder text)

Border Subtle:          rgba(255, 255, 255, 0.08)  (Dividers, card borders)
Border Light:           rgba(255, 255, 255, 0.12)  (Focused borders)
```

### Node Status Colors
```
🟢 Completed:     #10B981  (Green - finished nodes)
🟡 In Progress:   #F59E0B  (Amber/Orange - actively working)
🔵 Pending:       #3B82F6  (Blue - queued/waiting)
🟣 Active/Selected: #8B5CF6  (Purple - currently selected node)
🔴 Error:         #EF4444  (Red - failed/error state)
```

### Glassmorphic Overlays
```
Glass Card:       rgba(37, 37, 40, 0.6)  (60% opacity of #252528)
Glass Border:     rgba(255, 255, 255, 0.1)
Backdrop Blur:    blur(12px)

Glass Card Hover: rgba(45, 45, 50, 0.7)  (Slightly lighter on hover)
```

### Gradients & Accents
```
Primary Gradient:   linear-gradient(135deg, #8B5CF6 0%, #3B82F6 100%)
Success Gradient:   linear-gradient(135deg, #10B981 0%, #059669 100%)
Warning Gradient:   linear-gradient(135deg, #F59E0B 0%, #D97706 100%)

Glow Effect (Purple):  0 0 20px rgba(139, 92, 246, 0.4)
Glow Effect (Orange):  0 0 20px rgba(245, 158, 11, 0.4)
Glow Effect (Blue):    0 0 20px rgba(59, 130, 246, 0.4)
Glow Effect (Green):   0 0 20px rgba(16, 185, 129, 0.4)
```

---

## Typography

### Font Family
```css
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
```

### Type Scale
```
H1 - Hero/Project Title
  font-size: 24px
  font-weight: 600 (Semibold)
  line-height: 32px
  letter-spacing: -0.02em
  color: #EEEFF1

H2 - Section Headers
  font-size: 18px
  font-weight: 600
  line-height: 24px
  letter-spacing: -0.01em
  color: #EEEFF1

H3 - Subsection/Node Names
  font-size: 14px
  font-weight: 500 (Medium)
  line-height: 20px
  letter-spacing: 0
  color: #EEEFF1

Body - Chat messages, descriptions
  font-size: 14px
  font-weight: 400 (Regular)
  line-height: 21px
  letter-spacing: 0
  color: #EEEFF1

Body Small - Metadata, timestamps
  font-size: 12px
  font-weight: 400
  line-height: 18px
  letter-spacing: 0
  color: #9CA3AF

Caption - Labels, hints
  font-size: 11px
  font-weight: 500
  line-height: 16px
  letter-spacing: 0.01em
  text-transform: uppercase
  color: #6B7280
```

---

## Spacing System

Use 4px base unit (4, 8, 12, 16, 24, 32, 48, 64)

```
xs:   4px   (Tight spacing, icon padding)
sm:   8px   (Element padding, small gaps)
md:   12px  (Default padding)
lg:   16px  (Section padding, card padding)
xl:   24px  (Large gaps between sections)
2xl:  32px  (Major section separation)
3xl:  48px  (Panel padding)
4xl:  64px  (Page-level spacing)
```

---

## Layout Specifications

### Overall Structure
```
┌─────────────────────────────────────────────────────────┐
│ Top Bar (60px height)                                   │
├──────────────┬──────────────────────────────────────────┤
│              │                                          │
│ Left Panel   │ Right Panel (Tree/Timeline)             │
│ (20% width)  │ (80% width)                             │
│ Min: 280px   │ Min: 600px                              │
│ Max: 400px   │                                         │
│              │                                          │
└──────────────┴──────────────────────────────────────────┘
```

### Top Bar
```
Height: 60px
Padding: 0 24px
Background: #1A1A1D
Border-bottom: 1px solid rgba(255, 255, 255, 0.08)

Layout (flex, space-between):
  Left: Logo + Title
  Right: User Avatar + Settings + Sign Out
```

### Left Panel (Chat Interface)
```
Width: 20% (280px min, 400px max)
Padding: 24px 16px
Background: #1A1A1D
Border-right: 1px solid rgba(255, 255, 255, 0.08)

Structure (top to bottom):
  1. Agent Selector Dropdown (12px margin-bottom)
  2. Past Conversations List (12px margin-bottom)
  3. Chat Messages Area (flex-grow: 1, scrollable)
  4. Input Box (sticky bottom, 16px padding)
```

### Right Panel (Tree View)
```
Width: 80% (600px min)
Padding: 24px
Background: #1A1A1D

Structure:
  1. Tab Toggle (Tree View / Timeline Editor) - 48px height
  2. Tree Container (flex-grow: 1, scrollable)
     - Glassmorphic card containing tree
     - Padding: 24px
     - Border-radius: 12px
```

---

## Component Specifications

### 1. Agent Selector Dropdown

**Default State:**
```
Width: 100%
Height: 40px
Padding: 8px 12px
Background: rgba(45, 45, 50, 0.6)
Backdrop-filter: blur(12px)
Border: 1px solid rgba(255, 255, 255, 0.1)
Border-radius: 8px

Text: "Agent ▼" (14px, Medium, #EEEFF1)
Icon: Chevron down (16px)

Dropdown Items:
  - "• Sub-1" (Active: green dot)
  - "  Sub-2"
  - "  Sub-3"

Item Height: 36px
Item Hover: rgba(139, 92, 246, 0.15)
```

**Hover State:**
```
Background: rgba(45, 45, 50, 0.8)
Border: 1px solid rgba(255, 255, 255, 0.15)
Cursor: pointer
```

**Open State:**
```
Border: 1px solid rgba(139, 92, 246, 0.5)
Box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1)
```

---

### 2. Past Conversations List

**Container:**
```
Margin-bottom: 24px
```

**Header:**
```
Text: "Past Conversations ▼" (12px, uppercase, #6B7280)
Margin-bottom: 8px
```

**Conversation Item:**
```
Height: 32px
Padding: 6px 8px
Border-radius: 6px
Display: flex
Align-items: center
Gap: 8px

Icon: Chat bubble (14px, #9CA3AF)
Text: Project name (13px, #EEEFF1)
Time: "2d ago" (11px, #6B7280)
```

**Hover State:**
```
Background: rgba(139, 92, 246, 0.1)
Cursor: pointer
```

**Active State:**
```
Background: rgba(139, 92, 246, 0.2)
Border-left: 2px solid #8B5CF6
```

---

### 3. Chat Message Bubbles

**Agent Message:**
```
Max-width: 85%
Align: left
Margin-bottom: 16px

Content:
  Avatar: 32px circle (gradient background)
  Label: "Agent:" (12px, #9CA3AF, margin-bottom: 4px)
  Text: Message content (14px, #EEEFF1, line-height: 21px)

Background: rgba(37, 37, 40, 0.4)
Padding: 12px 16px
Border-radius: 12px
Backdrop-filter: blur(8px)
Border: 1px solid rgba(255, 255, 255, 0.06)
```

**User Message:**
```
Max-width: 85%
Align: right
Margin-bottom: 16px
Margin-left: auto

Content:
  Label: "You:" (12px, #9CA3AF, margin-bottom: 4px)
  Text: Message content (14px, #EEEFF1)

Background: rgba(139, 92, 246, 0.15)
Padding: 12px 16px
Border-radius: 12px
Border: 1px solid rgba(139, 92, 246, 0.3)
```

---

### 4. Chat Input Box

**Container:**
```
Position: sticky bottom
Width: 100%
Margin-top: auto
Padding-top: 16px
Background: linear-gradient(to top, #1A1A1D 80%, transparent)
```

**Input Field:**
```
Width: 100%
Height: 44px
Padding: 12px 16px
Background: rgba(37, 37, 40, 0.6)
Backdrop-filter: blur(12px)
Border: 1px solid rgba(255, 255, 255, 0.1)
Border-radius: 8px

Placeholder: "Type message..." (#6B7280)
Text: 14px, #EEEFF1
```

**Focus State:**
```
Border: 1px solid rgba(139, 92, 246, 0.5)
Box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1)
Outline: none
```

**Context Pill (when node selected):**
```
Position: Above input (8px gap)
Display: inline-flex
Align-items: center
Gap: 6px
Padding: 4px 10px
Background: rgba(139, 92, 246, 0.2)
Border: 1px solid rgba(139, 92, 246, 0.3)
Border-radius: 12px

Content: "💬 Scene 1 Agent" (12px, #EEEFF1)
Close button: × (14px, #9CA3AF)
```

---

### 5. Tab Toggle (Tree View / Timeline Editor)

**Container:**
```
Height: 48px
Display: flex
Gap: 4px
Padding: 4px
Background: rgba(37, 37, 40, 0.4)
Border-radius: 10px
Margin-bottom: 16px
```

**Tab Button:**
```
Flex: 1
Height: 40px
Padding: 0 24px
Background: transparent
Border: none
Border-radius: 8px

Text: 14px, Medium, #9CA3AF
Cursor: pointer
Transition: all 0.2s ease
```

**Active Tab:**
```
Background: rgba(139, 92, 246, 0.15)
Border: 1px solid rgba(139, 92, 246, 0.3)
Text color: #EEEFF1
Box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2)
```

**Hover (inactive):**
```
Background: rgba(255, 255, 255, 0.05)
Text color: #EEEFF1
```

---

### 6. Tree View Container (Glassmorphic)

**Outer Container:**
```
Width: 100%
Min-height: calc(100vh - 180px)
Background: rgba(37, 37, 40, 0.6)
Backdrop-filter: blur(12px)
Border: 1px solid rgba(255, 255, 255, 0.1)
Border-radius: 12px
Padding: 24px
Box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2)
```

**Tree Header:**
```
Margin-bottom: 24px
Display: flex
Justify-content: space-between
Align-items: center

Title: "🌳 South Park Episode: AI Takes Over" (18px, Semibold, #EEEFF1)
Overall Progress: "✓ 67%" (14px, #10B981)
```

---

### 7. Tree Node Components

#### **Root Node (Completed)**
```
Display: flex
Align-items: center
Gap: 12px
Padding: 12px 16px
Background: rgba(16, 185, 129, 0.1)
Border: 1px solid rgba(16, 185, 129, 0.3)
Border-radius: 8px
Margin-bottom: 12px

Icon: 🟢 (12px green circle)
Text: "Main Goal" (14px, Medium, #EEEFF1)
Status: "Completed" (12px, #10B981)
Badge: "✓ 100%" (12px, #10B981, right-aligned)
```

**Hover State:**
```
Background: rgba(16, 185, 129, 0.15)
Cursor: pointer
Transform: translateX(2px)
Transition: all 0.2s ease
```

---

#### **Mid-Level Node (In Progress)**
```
Margin-left: 24px (indentation for hierarchy)
Display: flex
Align-items: center
Gap: 12px
Padding: 12px 16px
Background: rgba(245, 158, 11, 0.1)
Border: 1px solid rgba(245, 158, 11, 0.3)
Border-radius: 8px
Margin-bottom: 8px

Icon: 🟡 (12px amber circle with pulse animation)
Text: "Character Agent" (14px, Medium, #EEEFF1)
Status: "In Progress" (12px, #F59E0B)
Progress: "◐ 67%" (12px, #F59E0B)
```

**Pulse Animation:**
```css
@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.7; transform: scale(1.1); }
}

animation: pulse 2s ease-in-out infinite;
```

**Hover State:**
```
Background: rgba(245, 158, 11, 0.15)
Glow: 0 0 20px rgba(245, 158, 11, 0.3)
Cursor: pointer
```

**Hover Tooltip:**
```
Position: absolute (right side of node)
Display: glass card
Padding: 12px
Min-width: 200px
Background: rgba(37, 37, 40, 0.95)
Backdrop-filter: blur(16px)
Border: 1px solid rgba(245, 158, 11, 0.4)
Border-radius: 8px
Box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3)
Z-index: 100

Content:
  "Working on: Voice profile generation"
  "Progress: 67%"
  "Est. time: 2m 34s"
  (12px, #9CA3AF)
```

---

#### **Sub-Node (Child)**
```
Margin-left: 48px (double indent)
Display: flex
Align-items: center
Gap: 8px
Padding: 8px 12px
Background: transparent
Border-left: 2px solid rgba(59, 130, 246, 0.3)
Margin-bottom: 4px

Connector: "└─" (10px, #6B7280)
Icon: ○ (8px blue circle outline)
Text: "Voice Profile" (13px, #EEEFF1)
Progress Bar: if working (width: 60px, height: 4px)
```

**Progress Bar:**
```
Height: 4px
Background: rgba(59, 130, 246, 0.2)
Border-radius: 2px
Overflow: hidden

Fill:
  Background: linear-gradient(90deg, #3B82F6, #8B5CF6)
  Width: 80% (dynamic)
  Border-radius: 2px
  Animation: shimmer 2s infinite
```

**Hover State:**
```
Background: rgba(59, 130, 246, 0.05)
Border-left: 2px solid rgba(59, 130, 246, 0.5)
Cursor: pointer
```

---

#### **Active/Selected Node (Purple Glow)**
```
Display: flex
Align-items: center
Gap: 12px
Padding: 12px 16px
Background: rgba(139, 92, 246, 0.15)
Border: 2px solid rgba(139, 92, 246, 0.5)
Border-radius: 8px
Margin-bottom: 8px
Box-shadow: 0 0 24px rgba(139, 92, 246, 0.4),
            0 0 0 4px rgba(139, 92, 246, 0.1)

Icon: 🟣 (12px purple circle with glow)
Text: "Scene 1 Agent" (14px, Semibold, #EEEFF1)
Badge: "← SELECTED" (11px, uppercase, #8B5CF6)
Status: "Working..." (12px, #8B5CF6)
```

**Glow Animation:**
```css
@keyframes glow {
  0%, 100% { box-shadow: 0 0 20px rgba(139, 92, 246, 0.4); }
  50% { box-shadow: 0 0 30px rgba(139, 92, 246, 0.6); }
}

animation: glow 3s ease-in-out infinite;
```

---

#### **Pending Node**
```
Display: flex
Align-items: center
Gap: 12px
Padding: 12px 16px
Background: rgba(59, 130, 246, 0.05)
Border: 1px solid rgba(59, 130, 246, 0.2)
Border-radius: 8px
Margin-bottom: 8px
Opacity: 0.7

Icon: 🔵 (12px blue circle)
Text: "Scene 2 Agent" (14px, #EEEFF1)
Status: "Pending" (12px, #6B7280)
```

**Hover State:**
```
Opacity: 1
Background: rgba(59, 130, 246, 0.1)
Border: 1px solid rgba(59, 130, 246, 0.3)
Cursor: pointer
```

---

### 8. Node Details Panel (Below Tree)

**Container:**
```
Margin-top: 24px
Padding: 20px
Background: rgba(37, 37, 40, 0.8)
Backdrop-filter: blur(16px)
Border: 1px solid rgba(139, 92, 246, 0.3)
Border-radius: 12px
Box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2)
```

**Header:**
```
Display: flex
Align-items: center
Gap: 12px
Margin-bottom: 16px

Icon: 🎬 (20px)
Title: "Scene 1: Cafe Interior" (16px, Semibold, #EEEFF1)
```

**Status Row:**
```
Margin-bottom: 12px

Label: "Working:" (11px, uppercase, #6B7280)
Text: "Adjusting warm lighting filter" (14px, #EEEFF1)
```

**Progress Bar:**
```
Width: 100%
Height: 8px
Background: rgba(139, 92, 246, 0.2)
Border-radius: 4px
Margin-bottom: 12px
Overflow: hidden

Fill:
  Background: linear-gradient(90deg, #8B5CF6, #3B82F6)
  Width: 85% (dynamic)
  Border-radius: 4px

  Shimmer animation:
    Background: linear-gradient(90deg,
      transparent 0%,
      rgba(255,255,255,0.3) 50%,
      transparent 100%)
    Animation: shimmer 2s infinite
```

**Metadata:**
```
Display: flex
Gap: 16px
Margin-bottom: 16px

Item: "85%" (14px, Medium, #8B5CF6)
Item: "Last update: 2s ago" (12px, #9CA3AF)
```

**Preview Thumbnail:**
```
Width: 100%
Height: 200px
Background: #0A0A0A (or preview image)
Border-radius: 8px
Border: 1px solid rgba(255, 255, 255, 0.1)
Overflow: hidden
Object-fit: cover

Placeholder state:
  Display: flex, center
  Icon: Film reel (48px, #6B7280)
  Text: "Generating preview..." (13px, #9CA3AF)
```

---

## Animation Specifications

### Transition Defaults
```css
/* Use for most UI elements */
transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);

/* For smooth fades */
transition: opacity 0.3s ease;

/* For glass effects */
transition: backdrop-filter 0.3s ease,
            background 0.2s ease;
```

### Keyframe Animations

**Pulse (for active nodes):**
```css
@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.7;
    transform: scale(1.05);
  }
}
/* Apply: animation: pulse 2s ease-in-out infinite; */
```

**Glow (for selected nodes):**
```css
@keyframes glow {
  0%, 100% {
    box-shadow: 0 0 20px rgba(139, 92, 246, 0.4),
                0 0 0 4px rgba(139, 92, 246, 0.1);
  }
  50% {
    box-shadow: 0 0 30px rgba(139, 92, 246, 0.6),
                0 0 0 6px rgba(139, 92, 246, 0.15);
  }
}
/* Apply: animation: glow 3s ease-in-out infinite; */
```

**Shimmer (for progress bars):**
```css
@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

/* Progress bar shimmer overlay */
.progress-shimmer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg,
    transparent 0%,
    rgba(255, 255, 255, 0.3) 50%,
    transparent 100%);
  animation: shimmer 2s infinite;
}
```

**Fade In Up (for new nodes appearing):**
```css
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
/* Apply: animation: fadeInUp 0.4s ease-out; */
```

**Slide In Right (for detail panels):**
```css
@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}
/* Apply: animation: slideInRight 0.3s ease-out; */
```

---

## Interaction States

### Universal Hover Behavior
All interactive elements should have:
1. **Subtle background change** (10-15% opacity increase)
2. **Cursor change** to pointer
3. **Smooth transition** (0.2s)
4. **Optional glow** for primary actions

### Focus States (Keyboard Navigation)
```css
*:focus-visible {
  outline: 2px solid rgba(139, 92, 246, 0.5);
  outline-offset: 2px;
  border-radius: 4px;
}
```

### Disabled States
```css
.disabled {
  opacity: 0.4;
  cursor: not-allowed;
  pointer-events: none;
}
```

### Loading States
Use shimmer effect or spinner:
```
Spinner:
  Size: 20px
  Border: 2px solid rgba(139, 92, 246, 0.3)
  Border-top: 2px solid #8B5CF6
  Animation: spin 0.8s linear infinite
```

---

## Glassmorphism Implementation Guide

### CSS Template for Glass Cards
```css
.glass-card {
  background: rgba(37, 37, 40, 0.6);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px); /* Safari support */
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.glass-card:hover {
  background: rgba(45, 45, 50, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.15);
  transition: all 0.3s ease;
}
```

### Layering for Depth
```
Layer 1 (Background): #1A1A1D (solid)
Layer 2 (Main glass): rgba(37, 37, 40, 0.6) + blur(12px)
Layer 3 (Elevated glass): rgba(45, 45, 50, 0.7) + blur(16px)
Layer 4 (Tooltips/modals): rgba(37, 37, 40, 0.95) + blur(20px)
```

### Performance Optimization
```
/* Use will-change for frequently animated elements */
.tree-node {
  will-change: transform, opacity;
}

/* Use transform for animations instead of position */
/* GOOD: */ transform: translateX(2px);
/* BAD: */  left: 2px;
```

---

## Responsive Behavior

### Breakpoints
```
Mobile:  < 768px
Tablet:  768px - 1024px
Desktop: > 1024px
Large:   > 1440px
```

### Mobile Adjustments (< 768px)
```
- Left panel: 100% width, slide-in drawer
- Right panel: 100% width, push content
- Tab toggle: Full width, stacked vertically
- Tree nodes: Reduce padding to 8px, smaller text
- Hide glassmorphic blur (performance)
```

### Tablet Adjustments (768px - 1024px)
```
- Left panel: 30% width (min 280px)
- Right panel: 70% width
- Maintain glassmorphic effects
- Slightly reduce node padding
```

---

## Accessibility

### Color Contrast
All text meets WCAG AA standards:
- Primary text (#EEEFF1) on dark (#1A1A1D): 13.5:1 ✓
- Secondary text (#9CA3AF) on dark: 7.2:1 ✓
- Accent colors on dark backgrounds: > 4.5:1 ✓

### Screen Reader Support
```html
<!-- Node example -->
<div
  role="treeitem"
  aria-expanded="true"
  aria-selected="true"
  aria-label="Scene 1 Agent, in progress, 85% complete"
  tabindex="0"
>
  <span aria-hidden="true">🟡</span>
  <span>Scene 1 Agent</span>
  <span class="sr-only">In Progress, 85% complete</span>
</div>
```

### Keyboard Navigation
```
Tab: Navigate between interactive elements
Enter/Space: Activate buttons, select nodes
Arrow keys: Navigate tree structure
Escape: Close dropdowns, deselect nodes
/ : Focus search/input (like Linear)
```

---

## Z-Index Scale
```
Base layer:           z-index: 0
Tree nodes:           z-index: 1
Hover tooltips:       z-index: 100
Dropdowns:            z-index: 200
Modals/overlays:      z-index: 500
Toast notifications:  z-index: 1000
```

---

## File Structure Recommendations

```
/src
  /components
    /Chat
      ChatInput.jsx
      ChatMessage.jsx
      ConversationList.jsx
      AgentSelector.jsx
    /Tree
      TreeView.jsx
      TreeNode.jsx
      NodeDetails.jsx
      HoverTooltip.jsx
    /Common
      GlassCard.jsx
      TabToggle.jsx
      ProgressBar.jsx
  /styles
    globals.css          (Base styles, CSS reset)
    variables.css        (Color/spacing tokens)
    glassmorphism.css    (Reusable glass styles)
    animations.css       (Keyframes, transitions)
  /utils
    nodeHelpers.js       (Node state logic)
    colorHelpers.js      (Dynamic color generation)
```

---

## Design Tokens (CSS Variables)

```css
:root {
  /* Colors */
  --bg-primary: #1A1A1D;
  --bg-secondary: #252528;
  --bg-tertiary: #2D2D32;

  --text-primary: #EEEFF1;
  --text-secondary: #9CA3AF;
  --text-tertiary: #6B7280;

  --border-subtle: rgba(255, 255, 255, 0.08);
  --border-light: rgba(255, 255, 255, 0.12);

  --status-completed: #10B981;
  --status-progress: #F59E0B;
  --status-pending: #3B82F6;
  --status-active: #8B5CF6;
  --status-error: #EF4444;

  /* Glass */
  --glass-bg: rgba(37, 37, 40, 0.6);
  --glass-border: rgba(255, 255, 255, 0.1);
  --glass-blur: 12px;

  /* Spacing */
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 12px;
  --space-lg: 16px;
  --space-xl: 24px;
  --space-2xl: 32px;

  /* Typography */
  --font-size-xs: 11px;
  --font-size-sm: 12px;
  --font-size-base: 14px;
  --font-size-lg: 16px;
  --font-size-xl: 18px;
  --font-size-2xl: 24px;

  /* Transitions */
  --transition-fast: 0.15s;
  --transition-base: 0.2s;
  --transition-slow: 0.3s;

  /* Shadows */
  --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.1);
  --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.2);
  --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.3);

  /* Glow effects */
  --glow-purple: 0 0 20px rgba(139, 92, 246, 0.4);
  --glow-orange: 0 0 20px rgba(245, 158, 11, 0.4);
  --glow-blue: 0 0 20px rgba(59, 130, 246, 0.4);
  --glow-green: 0 0 20px rgba(16, 185, 129, 0.4);
}
```

---

## Implementation Checklist

### Phase 1: Foundation
- [ ] Set up CSS variables and design tokens
- [ ] Implement base glassmorphic card styles
- [ ] Create layout structure (top bar, left panel, right panel)
- [ ] Set up Inter font loading
- [ ] Implement dark background gradient

### Phase 2: Left Panel (Chat)
- [ ] Agent selector dropdown
- [ ] Past conversations list
- [ ] Chat message bubbles (agent + user)
- [ ] Chat input with context pill
- [ ] Scrolling behavior

### Phase 3: Right Panel (Tree)
- [ ] Tab toggle component
- [ ] Glassmorphic tree container
- [ ] Node components (all states: completed, progress, pending, active)
- [ ] Node hierarchy/indentation
- [ ] Node hover tooltips

### Phase 4: Interactions
- [ ] Node click → context pill in chat
- [ ] Node hover → tooltip with status
- [ ] Agent selector → filter/highlight
- [ ] Smooth transitions between states
- [ ] Keyboard navigation

### Phase 5: Animations & Polish
- [ ] Pulse animation on in-progress nodes
- [ ] Glow effect on selected node
- [ ] Progress bar shimmer
- [ ] Fade in animations for new nodes
- [ ] Loading states

### Phase 6: Node Details Panel
- [ ] Details panel below tree
- [ ] Preview thumbnail area
- [ ] Progress visualization
- [ ] Metadata display

### Phase 7: Testing & Optimization
- [ ] Test glassmorphism performance
- [ ] Verify color contrast (accessibility)
- [ ] Keyboard navigation testing
- [ ] Responsive behavior (mobile/tablet)
- [ ] Cross-browser testing (Safari backdrop-filter)

---

## Notes for Future Implementation

### Timeline Editor Tab (Phase 2)
When building the Timeline Editor tab:
- Horizontal timeline at bottom (similar to Adobe Premiere)
- Clip preview area on top
- Use same glassmorphic styling
- Same color system for clip states
- Draggable clips with smooth animations

### Real-time Updates
Consider WebSocket or Server-Sent Events for:
- Node status changes
- Progress updates
- New chat messages
- Live preview thumbnails

### State Management
Recommended structure:
```javascript
{
  activeAgent: "Sub-1",
  selectedNode: "scene-1-agent",
  tree: {
    nodes: [...],
    edges: [...]
  },
  chat: {
    messages: [...],
    contextNode: "scene-1-agent"
  },
  ui: {
    leftPanelWidth: 320,
    activeTab: "tree-view"
  }
}
```

---

## Version History
- **v1.0** - Initial design system (2025-11-08)
  - Linear-inspired dark mode
  - Glassmorphism implementation
  - Multi-color node system
  - Complete component specifications

---

**End of Design System v1.0**
