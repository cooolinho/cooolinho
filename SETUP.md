# GitHub Profil-README

Diese `README.md` ist ein **Profil-README**. Damit sie auf deinem GitHub-Profil erscheint:

1. Lege ein Repository mit **exakt deinem Username** an: `cooolinho/cooolinho`
2. Setze es auf **public**.
3. Inhalt dieses Ordners ins Repo-Root kopieren, committen, pushen.

```bash
git init
git add .
git commit -m "Add profile README"
git branch -M main
git remote add origin git@github.com:cooolinho/cooolinho.git
git push -u origin main
```

## Wichtig: Reihenfolge beim ersten Mal

Die Statistik-Bilder werden **nicht** von einem fremden Dienst geladen, sondern von zwei
GitHub Actions in diesem Repo erzeugt. Vor dem ersten Lauf zeigen die Bildpfade ins Leere.
Deshalb in dieser Reihenfolge vorgehen:

1. **PAT anlegen**: GitHub → Settings → Developer settings → Personal access tokens →
   *Tokens (classic)* → Generate new token mit den Scopes **`read:user`** und **`repo`**.
2. **Als Secret hinterlegen**: Repo → Settings → Secrets and variables → Actions →
   New repository secret, Name **`SUMMARY_GITHUB_TOKEN`**, Wert = das Token.
   Der eingebaute `GITHUB_TOKEN` reicht hier nicht — er kommt nicht an die
   repo-übergreifenden Contribution-Daten.
3. **Push** (siehe oben).
4. **Beide Workflows einmal manuell starten**: Repo → Actions → „Profile summary cards"
   bzw. „Contribution snake" → *Run workflow*.
5. Profil öffnen und prüfen, dass keine kaputten Bild-Icons mehr da sind.

## Die beiden Workflows

| Datei | Erzeugt | Landet in |
| --- | --- | --- |
| `.github/workflows/profile-summary-cards.yml` | Profil-Details, Stats, Sprachen, Productive Time | `profile-summary-card-output/<theme>/` auf `main` |
| `.github/workflows/snake.yml` | Contribution-Snake (hell + dunkel) | Branch `output` |

Beide laufen täglich per Cron und lassen sich jederzeit per *Run workflow* auslösen.

### Warum keine `*.vercel.app`-Dienste mehr

Die früher üblichen öffentlichen Instanzen sind ausgefallen (Stand 2026-08-29):
`github-readme-stats.vercel.app` liefert `DEPLOYMENT_PAUSED` (HTTP 503),
`github-profile-trophy.vercel.app` und `github-readme-activity-graph.vercel.app`
liefern `DEPLOYMENT_DISABLED` / *Payment required* (HTTP 402). Der Mirror
`github-readme-stats.hackclub.dev` antwortet zwar mit 200, rendert aber die Fehlerkarte
„No GitHub API tokens found".

Deshalb erzeugen die Actions die SVGs jetzt selbst im Repo. Die einzigen verbliebenen
externen Bilder sind `img.shields.io` (Badges) und `komarev.com` (Profil-Zähler) —
eigene Domains, keine Vercel-Deployments.

Der Header (`assets/header.svg`) und der Footer (`assets/footer.svg`) sind handgeschriebene,
statische SVGs in diesem Repo und ersetzen `capsule-render.vercel.app`.

## Anpassen

- **Username**: kommt an vielen Stellen als `cooolinho` vor — bei Bedarf global ersetzen
  (auch in den `raw.githubusercontent.com`-URLs der Snake).
- **Foto statt Banner**: Im README ist ein auskommentierter Block mit
  `https://github.com/cooolinho.png` (dein Avatar). Banner-Zeile löschen, Block einkommentieren.
  Für ein eigenes Bild: Datei nach `assets/` legen und relativ verlinken.
- **Header-Text**: steht direkt als `<text>` in `assets/header.svg`.
- **Kontakt-Links**: LinkedIn-URL und E-Mail-Adresse sind leer und müssen ergänzt oder
  entfernt werden.
- **Projekte**: Die Tabelle enthält fünf Repos aus deinem Projektordner — Beschreibungen
  prüfen, Repos ersetzen, die nicht public sind.
- **Theme**: Das README nutzt `github` (hell) und `github_dark` (dunkel) über
  `<picture>`-Elemente. Andere Themes gibt es unter
  `profile-summary-card-output/` nach dem ersten Lauf — dort einfach den Ordnernamen tauschen.
- **Weniger Dateien**: Der Workflow erzeugt per Default *alle* Themes (~65 Ordner). Wenn dich
  das stört, setze in `profile-summary-cards.yml` `THEME: "github_dark"` — dann brauchst du
  im README aber auch die `<picture>`-Umschaltung nicht mehr und verweist direkt auf das
  eine Theme.

## Bekannte Eigenheiten

- `raw.githubusercontent.com` cached rund 5 Minuten — direkt nach einem Workflow-Lauf kann
  die Snake noch die alte Version zeigen.
- **Private Commits** zählen nur, wenn du unter Settings → Public profile →
  „Include private contributions on my profile" aktivierst.
- Der Cron im README der Summary-Cards-Action lautet `* */24 * * *`; das feuert 60× in einer
  Stunde. In `profile-summary-cards.yml` steht deshalb bewusst `17 4 * * *`.
- Eine Trophäen-Karte gibt es nicht mehr — dafür existiert kein Action-basierter Generator.
  Die Kennzahlen deckt `3-stats.svg` ab.
