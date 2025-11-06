"# africommerce" 
"# EcommerceSanDiego" 
You are an expert UI/UX and frontend engineer. I have an existing HTML/CSS project for an e-commerce site exporting Nigerian products to the U.S. Below is my current file structure and a high-level description of what each file does. Your task is to **enhance** my UI/UX—using ONLY my existing files (add new ones only if absolutely necessary), follow my naming conventions, and keep CSS modular. Deliver code diffs or updated files with clear comments.

rgins, flex, text-center)


### 2. Goals & Constraints
1. **Responsive & Mobile-First**: Use media queries in `base.css` and `layout.css` to ensure all pages adapt down to 320px width.
2. **Afrocentric but Modern**: Leverage my CSS variables (`--primary-green`, `--accent-ochre`, etc.) to reflect Nigerian heritage without bloating CSS.
3. **UI Components**: Improve buttons, form fields, product cards, navbar, and modal dialogs (e.g. cart preview) for best practice accessibility (ARIA roles, focus states).
4. **Performance**: Keep HTML semantics intact. Use CSS transforms/animations sparingly (e.g. smooth hover states), optimize image loading (native `loading="lazy"`).
5. **Minimal New Dependencies**: No new CSS frameworks. You may suggest tiny utility classes or a single CSS file if needed.

### 3. Specific Tasks
- **Navbar & Hero** (`index.html`):  
  - Collapse menu into a hamburger on ≤768px.  
  - Add subtle slide-in animation for mobile menu.  
- **Product Listing** (`products.html`):  
  - Add sticky filter sidebar on desktop, and a slide-in filter modal on mobile.  
  - Improve product-card grid: show 4 columns on ≥1200px, 3 on ≥900px, 2 on ≥600px, 1 on smaller.  
- **Product Detail** (`product-detail.html`):  
  - Implement an image gallery with thumbnail selector and zoom-on-hover.  
  - Style “Add to Cart” form with quantity selector plus/minus buttons.  
- **Checkout Flow** (`cart.html`):  
  - Add step-by-step progress bar (Cart → Address → Payment → Review).  
  - Style form inputs with error states and inline validation messages.  
- **Vendor Dashboard** (`vendor-dashboard.html`):  
  - Turn static tables into responsive cards on mobile.  
  - Add a sidebar toggle and collapsible sections for Orders / Inventory.  

### 4. Deliverables
- Updated CSS (or new partials) with annotated comments.  
- HTML diffs or full updated files.  
- Short explanation of each change and why it improves UI/UX.  
- A final summary of any newly added classes, variables, or components.

### 5. Tone & Best Practices
- Write clean, DRY CSS. Use BEM or my existing naming style.  
- Comment EVERY non-trivial section of CSS/HTML.  
- Ensure all interactive elements have clear focus outlines.  
- No inline styles—keep layout in CSS files.

—  
Please proceed step by step, starting with the **navbar and hero section** in `index.html` and `css/layout.css`. Show me the HTML/CSS diff, then explain.  
