# ContextOS — UI Revamp Design Reference

**Status:** Design proposal only. Stored exclusively in `design_revamp/`. No changes to `web/`, `backend/`, or any other source files have been made.  
**Last Updated:** 15 October 2026  
**Tool:** Google Stitch MCP  
**Stitch Project ID:** `17359454100226408308`  
**Stitch Project Title:** ContextOS — Old Money Revamp  
**Active Design System Asset:** `assets/56f3a7cc3f074e36aaad05e374ca3de0` (Institutional Heritage)

---

## Aesthetic Direction: Institutional Heritage / Old Money

This revamp direction embodies the calculated discretion, gravity, and permanence of a centuries-old private banking house, collegiate archival vault, or supreme registrar. It moves ContextOS from a light-green SaaS aesthetic to an authoritative, timeless digital instrument.

### Design Tokens (Institutional Heritage)

| Token | Previous Value | Proposed Value | Description |
|---|---|---|---|
| Page Background | `#f7f8fa` | `#FEF9EE` (warm alabaster) | Matte archival canvas; eliminates monitor fatigue |
| Card Surface | `#ffffff` | `#F8F3E8` / `#F2EDE2` (parchment) | Tactile vellum feel for content cards and inspectors |
| Sidebar / Primary | `#ffffff` | `#161D26` (Oxford charcoal-navy) | Leather-bound folio register feel |
| Primary Ink / Text | `#202936` | `#1D1C15` (deep iron gall ink) | Classical letterpress contrast |
| Muted Ink / Labels | `#64748b` | `#45474B` / `#75777C` | Secondary captions, timestamps, coordinates |
| Border Rule | `#e7eaee` | `#DEDACF` / `#D0C8B6` | Hairline copperplate ledger rule (1px solid) |
| Primary Accent | `#214e3c` + lime | `#9B8354` (antique brass / gold) | Validation seals, active navigation pips |
| Hover / Selection | `#f0fdf4` | `#EDE7DA` (pressed linen wash) | Restrained row highlight and table selection |
| Heading Typography | system-ui | **EB Garamond** (400–600 weight) | Editorial authority for headlines and mastheads |
| UI & Body Copy | system-ui | **Inter** / **Newsreader** | High-density administrative reading clarity |
| Labels & Metrics | monospace | **Source Sans 3** / **JetBrains Mono** | Tracked uppercase labels & tabular alignment |

### Core Architectural Principles
1. **Zero-Shadow Architectural Restraint:** Absolutely zero synthetic drop-shadows, blurred glassmorphism, or multi-stop gradients. Depth is established purely via tonal stepping and hairline containment rules.
2. **Rectilinear Precision:** Strict `0px` to `3px` micro-radii on all containers, buttons, cards, and modal frames.
3. **Calibrated Instantaneity:** Zero decorative transitions or bounce animations. State transitions are instantaneous and authoritative.
4. **Archival Typography:** Tracked uppercase section labels in antique brass (`#9B8354`) paired with classical EB Garamond serif titles.
5. **Auditable Dignity:** Monospaced cryptographic provenance signatures, Merkle timestamps, and token counters are prominently displayed like legal seals.

---

## Latest Stitch Screens & Standalone Local Prototypes

All five core application screens have been refreshed with the Institutional Heritage system and are stored locally in this directory:

### 1. Workspace Overview
- **Local File:** [screen_overview.html](file:///Users/faizanchoudhary/Documents/ai_builder_cup/design_revamp/screen_overview.html)
- **Stitch Screen ID:** `d782ff3a66fd4b48b0d96027958c2eee`
- **Stitch Screenshot:** [View Google Cloud CDN Image](https://lh3.googleusercontent.com/aida/AEtjO1UoqONOHhgVuS5s0TibQrBuMCWZXNB8fR5csoJP6zBL3Zazic9bxKy81RFci7t1z56A5mLkKuKzuPrbE7-AocnnY5NoumqlCFS_UT2GB485nqNXbLoJG5v6Yv8Y6TLmt3DI7lZJAeFqd5rso4k-jflg0ickNzdnuSbNHwqVFd5kaMNuZX2g5bsD4cQPF-96ULEnIM7wvSdjK1SrYMx9sWVA28pnRVjSKSPXWfEYdf687U8Pvkk1cgHMDhsL)
- **Features:** Oxford charcoal-navy register sidebar with antique brass pip indicator, alabaster page canvas, stat cards with antique gold metric numbers, and a two-column institutional knowledge ledger.

### 2. Shared Knowledge Repository
- **Local File:** [screen_knowledge_repository.html](file:///Users/faizanchoudhary/Documents/ai_builder_cup/design_revamp/screen_knowledge_repository.html)
- **Stitch Screen ID:** `849849f2636541c483d0a0f3755507ae`
- **Stitch Screenshot:** [View Google Cloud CDN Image](https://lh3.googleusercontent.com/aida/AEtjO1U9PUxThI1wrBb7ENgTPwN5jD8_ZZvmKXYL7I15fsl5Rn11EA5mlSb8YP6lz21wzNvfROvtBD8Arw5oGWI6KlThHMOYtHYlI4omqfDxbB7kHUdFDOUff9zdlKYfvl3mJwPly2bL2jLH7AhgOnSyHnJkOdYh21WaetT2LzjznYStyyCTtLXgOki750SNjZTXqnMPwpA9gNgGIUaLUaaHFd9nLXa77mwSgsMtUrusxrpzBm97d4rTK91HpohD)
- **Features:** 3-column knowledge card grid, domain taxonomy chips (Architecture, Product Spec, Quality, Security, Infrastructure), ivory search bar, and provenance hashes.

### 3. Change Reviews & Independent Governance
- **Local File:** [screen_change_reviews.html](file:///Users/faizanchoudhary/Documents/ai_builder_cup/design_revamp/screen_change_reviews.html)
- **Stitch Screen ID:** `2cb04d2e27e14beebded197345b59054`
- **Stitch Screenshot:** [View Google Cloud CDN Image](https://lh3.googleusercontent.com/aida/AEtjO1UG4sT6uPhxkgJqq6ghSLyS9GivOBEmIczw07g_Gt8y8pwA345kZY4_r-RsfRtIwFjXbHAr7S0ORMZwVS0aSJoKJypPuxgPQfIDKk3_wnMAjzZFuxIbWtoyI99TMsScko3T-VCli6SeOP2xl16ztLBxRQbfOhv_sQFXIfQtV3qq7G2eswIyEzj2LWtrCo5FPBTJzXoQJQAsE4T9TELoGq4Jzhrwm5glcWtU-_N7Rhc1BWmOb5eroPXUnsa5)
- **Features:** Diff inspection cards rendered in parchment with subdued sage and terracotta highlights, cryptographic proposal digests, and filter tabs (Pending, Approved, Rejected).

### 4. Agent Tasks & Context Assembler
- **Local File:** [screen_tasks.html](file:///Users/faizanchoudhary/Documents/ai_builder_cup/design_revamp/screen_tasks.html)
- **Stitch Screen ID:** `e8d608015b3e432ea8696bf866465da5`
- **Stitch Screenshot:** [View Google Cloud CDN Image](https://lh3.googleusercontent.com/aida/AEtjO1UqcJ33nLV9uWvUKHhwJHYnht1TOrVC_BXfY8Lw63-VKBcPkbr2EOgh7B7jUAPhZ6J0D1RQZjcWuDLZ3N8tmlPJ7H8FsEk_eM-Wvwt3jJcl-5gmDYmVyqqlflCNQP2IYwHd3QTBO0Ivvks9AuTKN4FxEiuK3OVPSpMTFKxdXzU1mfqM6KUcnsK2Q8NQl04Pt4DrVLPhNcocwh9czsuPO4OOy3z2XeYG_kujYLiLQ17VCbHc-2shww9w76tx)
- **Features:** Dual-pane prompt packing workstation with token budget slider (8k to 64k), bounded context node weights, Merkle seal indicator, and historical execution audit ledger.

### 5. Context Insights & Institutional Telemetry
- **Local File:** [screen_insights.html](file:///Users/faizanchoudhary/Documents/ai_builder_cup/design_revamp/screen_insights.html)
- **Stitch Screen ID:** `1d787e36b8584d61804b9a64c80e1ce5` (and original design spec `6cd1080553834209af57ad386e740c48`)
- **Stitch Screenshot:** [View Google Cloud CDN Image](https://lh3.googleusercontent.com/aida/AEtjO1VK7NtcguEm3X2h-fC3sqTX4VlgINan7paWKL8zR6-AvO6E3NRpDA2vq2s0es9n-BSou53RbWTAWdja0QfwIau-IkaVimgN2bmHAkydZVXDU0gNfRUDiWkSlO36S2oZzvzVD_Avqr6VBPGrxuJ1y1atz5GVzR-ROfjvfFRtKZL8G03t0swEJ5pPs2Wpi4_2spmpcOhCCMZlmcxC6N52YWPM8B6Pc03ulLKzOF09EVTt99pfr1eHNeOvHNIZ)
- **Features:** KPI cards (Governed Topics, Token Savings, Cost Avoidance, Freshness), domain density bars, context optimization benchmarks, and review velocity metrics.

---

## Non-Destructive Adoption Guide for Builder Agent

If and when the builder agent chooses to apply this visual upgrade to the active app, **zero backend or JavaScript logic changes are required**. The implementation is 100% confined to `web/style.css` and a font import in `web/index.html`.

### Step 1: Add Google Fonts to `web/index.html`
Insert inside `<head>`:
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
```

### Step 2: Update Color Tokens in `web/style.css`
Replace the `:root` block:
```css
:root {
  --bg: #FEF9EE;           /* warm alabaster canvas */
  --paper: #F8F3E8;        /* warm parchment card surface */
  --sidebar: #161D26;      /* deep Oxford charcoal-navy */
  --sidebar-hover: #222C3A;/* subdued slate hover */
  --sidebar-border: #10161E;
  --ink: #1D1C15;          /* deep iron gall ink */
  --muted: #45474B;        /* warm dark umber secondary text */
  --line: #DEDACF;         /* hairline copperplate border rule */
  --gold: #9B8354;         /* antique brass accent */
  --gold-bg: #EDE7DA;      /* pressed linen wash */
  --green: #161D26;        /* compatibility alias */
  --lime: #EDE7DA;         /* compatibility alias */
  --soft: #FEF9EE;
  --orange: #9B8354;
  --shadow: none;          /* zero shadow - flat architectural hairlines */
  --font-serif: 'EB Garamond', Georgia, serif;
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-mono: 'JetBrains Mono', Menlo, monospace;
}
```

---

*All files in `design_revamp/` are non-intrusive reference prototypes.*
