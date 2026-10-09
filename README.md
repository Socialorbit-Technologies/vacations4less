# Vacations4Less website

Static rebuild of [vacations4less.us](https://vacations4less.us/), deployed to **https://vacations4less.us/staging/** on every push to `main`.

## Structure

```
src/
  pages/        one file per page (meta block at the top: title, description, path, nav)
  partials/     header.html + footer.html shared by every page
  assets/       css, js, img
  contact.php   quote + newsletter form handler (emails contact@vacations4less.us)
  .htaccess     staging noindex, caching, compression
build.py        assembles pages into public/
```

Edit a page in `src/pages/`, commit, push. GitHub Actions builds and uploads `public/` over FTP.

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
| Lagoon | `#0E3B43` | primary dark, headings |
| Reef | `#1C6E70` | links |
| Sea glass | `#BFE3D9` | tints |
| Mist | `#F2F8F7` | page background |
| Hibiscus | `#D7264E` | calls to action |
| Sun | `#F4B740` | small highlights |

Type: Bricolage Grotesque (headings), Source Serif 4 (body).

## Before going live

- Images currently load from the WordPress media library (`/wp-content/uploads/…`). Copy them into `src/assets/img/` before WordPress is removed.
- Flights, car rental, Hawaii availability, blog, privacy and terms link to the existing WordPress pages.
- Confirm the testimonials are from real customers.
- Build with `STAGING=0` for production (removes noindex), and point the deploy at `public_html/`.
