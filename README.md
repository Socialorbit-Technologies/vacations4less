# Vacations4Less website

Static rebuild of [vacations4less.us](https://vacations4less.us/), deployed to **https://vacations4less.us/staging/** on every push to `main`.

## Structure

```
src/
  pages/        one file per page (meta block at the top: title, description, path, nav)
  blog/         one file per blog post -> /blog/<file-name>/
  blog-index.html  the /blog/ listing page
  partials/     header, footer and the blog post template
  assets/       css, js, img
  contact.php   quote + newsletter form handler (emails contact@vacations4less.us)
  .htaccess     staging noindex, caching, compression
build.py        assembles pages into public/
```

Edit a page in `src/pages/`, commit, push.

### Adding a blog post

Copy `src/blog/nakalele-blowhole-maui.html` to `src/blog/<url-slug>.html`, update the meta block (`title`, `seo_title`, `description`, `excerpt`, `date`, `category`, `cover`, `cover_alt`, `thumb`) and write the body in HTML. Image paths in `cover`/`thumb` are relative to `wp-content/uploads/`. The blog page, home page "travel tips" section, related posts, sitemap and article schema update automatically on the next push. GitHub Actions builds and uploads `public/` over FTP.

Local preview: `python3 build.py && cd public && php -S localhost:8000`

## One-time setup (GitHub → Settings → Secrets and variables → Actions)

| Secret | Value |
|---|---|
| `FTP_SERVER` | FTP host from DirectAdmin (often `ftp.vacations4less.us` or the server IP) |
| `FTP_USERNAME` | FTP account username |
| `FTP_PASSWORD` | FTP account password |
| `FTP_SERVER_DIR` | *optional* — defaults to `domains/vacations4less.us/public_html/staging/`. If the FTP account is already rooted at `public_html`, set this to `staging/`. |

If the host doesn't support FTPS, change `protocol: ftps` to `ftp` in `.github/workflows/deploy.yml`.

## Brand

| Token | Hex | Use |
|---|---|---|
| Navy | `#0F1E4A` | headings, footer |
| Royal blue | `#1D4ED8` | primary blue: bands, page headers, links |
| Sky | `#EEF3FE` | alternate section background |
| Sunshine | `#FFC233` | calls to action (always with navy text) |
| Sunshine soft | `#FFD978` | small highlights on blue/dark |

Palette: **Royal & Sunshine** (chosen by the client). CSS token names (`--ocean`, `--orange`) are historical; their values are this palette.

Type: Bricolage Grotesque (headings), Source Serif 4 (body).

## Colour previews (staging only)

Staging builds show a "Colours" button bottom-left with five palettes: Royal & Sunshine (default, chosen), Ocean & Sunset, Navy & Coral, Emerald & Mango, Indigo & Amber. Link straight to one with `?theme=coral` (or `ocean`, `emerald`, `dusk`, `royal`). The palettes live at the end of `src/assets/css/site.css`. Production builds (`STAGING=0`) leave the switcher out; to launch with a variant, copy its values into `:root`.

## Home page slider

Slides live at the top of `src/pages/index.html` (`.slide-media` for the photo, `.slide-copy` for the text, one `.slider-dot` each, all in the same order). Only the first image loads up front; the rest load just before they show. It autoplays every 4 s (`SLIDE_MS` in `src/assets/js/site.js`), pauses while someone types in the quote form, uses the slider by keyboard, presses pause, or switches tabs. Visitors who prefer reduced motion get a plain crossfade with no zoom.

## Before going live

- Images currently load from the WordPress media library (`/wp-content/uploads/…`). Copy them into `src/assets/img/` before WordPress is removed.
- Privacy policy and terms link to the existing WordPress pages. There is no self-booking: every booking goes through the quote form or a phone call.
- Confirm the testimonials are from real customers.
- Pages use clean URLs (`/about/`, `/services/`, `/contact/`), the same addresses as the WordPress site, so no redirects are needed for them. Old blog URLs (`/nakalele-blowhole-maui/`, `/travel-tips-blog/`) 301-redirect to `/blog/...` via `.htaccess` once deployed at the domain root.
- Build with `STAGING=0` for production (removes noindex), and point the deploy at `public_html/`.
