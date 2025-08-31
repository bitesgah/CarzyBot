# CarzyBot

Ein vielseitiger Discord-Bot für Community-Management, Giveaways, Selfroles, Tickets und Social-Media-Benachrichtigungen.

## Features
- **Giveaways**: Erstelle und verwalte Gewinnspiele mit automatischer Auslosung
- **Ticket-System**: Support-Tickets mit Claim/Close/Log-Funktion
- **Selfroles**: User können sich Rollen selbst geben
- **Custom Embeds**: Schöne Embed-Nachrichten erstellen und senden
- **Moderation**: Purge, Nuke, Respawn, Serverinfo, Rollenverwaltung
- **Social Media**: YouTube, Twitch & TikTok Benachrichtigungen

## Installation
1. Repository klonen
2. Python 3.8+ installieren
3. Abhängigkeiten installieren:
   ```bash
   pip install -r requirements.txt
   ```
4. Die Beispiel-Konfigurationsdateien (`jsons/*.json.example`) kopieren und als `.json` speichern (z.B. `env.json.example` → `env.json`) und mit deinen Daten füllen.
5. Bot starten:
   ```bash
   python CarzyMain.py
   ```

## Konfiguration
Alle sensiblen Daten (Token, API-Keys, Channel-IDs) werden in den JSON-Dateien im `jsons/`-Ordner gespeichert. Die `.example`-Dateien dienen als Vorlage.

**Wichtig:** Die echten JSON-Dateien werden nicht mit ins Repo geladen (siehe `.gitignore`).

## Beispiel für `jsons/env.json`
```json
{
  "TOKEN": "DEIN_DISCORD_BOT_TOKEN",
  "TwitchClientID": "DEINE_TWITCH_CLIENT_ID",
  "TwitchSecret": "DEIN_TWITCH_CLIENT_SECRET"
}
```

## Hinweise
- Passe die Channel-IDs und Rollen-IDs in den JSON-Dateien an deinen Server an.
- Für Social-Media-Benachrichtigungen werden ggf. API-Keys benötigt.
- Der Bot lädt automatisch alle Cogs aus dem `cogs/`-Ordner.

## Lizenz
MIT License

---

Viel Spaß mit CarzyBot! Bei Fragen oder Problemen gerne ein Issue auf GitHub erstellen.
