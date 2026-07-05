# JYPE Minecraft Server

Local Fabric Minecraft server backup repository.

## Clone

```bash
git clone git@github.com:yl-2010/JYPE_minecraft_server.git ~/github/JYPE-minecraft-server
cd ~/github/JYPE-minecraft-server
```

## What's backed up

- Live world data (`world/`)
- Server config, mods, scripts, and player lists
- BlueMap config (map tiles regenerate automatically)

## What's excluded

- Discord webhook secret
- Server logs and BlueMap logs
- `session.lock` (only exists while the server is running)
- BlueMap rendered map tiles (large, regeneratable)
- Old `.tar.gz` world snapshots in `backups/` (over GitHub's 100 MB file limit)

## Push a backup

The server can stay running. From this folder:

```bash
git add -A
git commit -m "world sync $(TZ=America/Los_Angeles date '+%l:%M:%S %p' | tr '[:upper:]' '[:lower:]' | sed 's/^ *//') Pacific"
git push
```

Or use the helper script:

```bash
./scripts/backup-to-git.sh
```

Optional: run `save-all` in the server console before pushing for a cleaner world snapshot.
