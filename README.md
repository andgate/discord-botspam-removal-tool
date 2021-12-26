# Usage Instructions

To use, you only need is the dicord token of the bot you want to purge. This can be retrieved from the [discord developer panel](https://discord.com/developers).

Also, the bot role must be given the `Manage Messages` permission. This can be done from discord by right-clicking the server icon:
```
Server Settings -> Roles -> Edit bot role -> Permissions tab
```
Finally under the permissions tab, enable `Manage Messages`.

# Build Instructions

Requirements:
  - `python3`
  - `make`

To setup project:
```
make setup
```
NOTE: you may have to install `pyqt5` as an administrator.

To build project:
```
make app
```
When finished building, the app can be found at `dist/discord-bot-spam-removal-tool.exe`.

To quickly run the project in development mode:
```
make dev
```
