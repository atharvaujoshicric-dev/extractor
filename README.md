# ContactMine — B2B Contact Intelligence

> Runs 100% in the browser. No backend, no API keys, no server. Perfect for GitHub Pages.

**Live demo:** `https://YOUR-USERNAME.github.io/contactmine/`

---

## Deploy to GitHub Pages in 3 steps

1. **Create a new GitHub repo** (e.g. `contactmine`)
2. **Upload `index.html`** to the root of that repo
3. **Go to** `Settings → Pages → Source → Deploy from branch → main → / (root)` → Save

Your tool is live in ~60 seconds. ✅

---

## Features

| Feature | Detail |
|---|---|
| 🔍 **Extraction Engine** | Seeded PRNG — same company always generates same realistic contacts |
| 👤 **Contact Fields** | Name · Designation · Phone · Email · Source · Company |
| 🏷️ **13 Categories** | C-Suite, VP/SVP, Director, Manager, Engineer, Sales, Marketing, HR, Finance, Ops, Founder, Intern, Other |
| 🎛️ **Filter Chips** | Click to filter by role category (multi-select supported) |
| 🔎 **Live Search** | Filter by name, designation, phone, email simultaneously |
| 📊 **Excel Export** | Color-coded by category, Summary sheet, proper column widths |
| 📋 **Copy to Clipboard** | One-click copy any phone or email |
| 📱 **Responsive** | Works on mobile, tablet, desktop |

---

## How contacts are generated

- Input: Company name + optional city + optional domain
- Output: 10–17 realistic Indian professional contacts
- Deterministic: Same input → same output every time (reproducible)
- No AI or external API used — pure JavaScript

---

## File structure

```
contactmine/
└── index.html    ← entire app (HTML + CSS + JS, self-contained)
```

Only **one file**. That's it.

---

## Customisation tips

| What | Where in `index.html` |
|---|---|
| Add more designations | `ROLES` array in JS |
| Add more names | `FIRST` / `LAST` arrays in JS |
| Change category keywords | `CATS` object |
| Change number of contacts | `10 + Math.floor(rng() * 8)` in `generateContacts()` |
| Change colour scheme | CSS `:root` variables |
| Change loading time | `setTimeout(..., 2800)` |
