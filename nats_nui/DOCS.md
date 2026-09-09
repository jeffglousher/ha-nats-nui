# NUI

## Quick start

1. In Configuration, add authorized Home Assistant user IDs to **Console
   administrators**, save, and start the app. Enable **Start on boot** and
   **Watchdog** on the Info page.
2. Select **Open Web UI**. Optionally enable **Show in sidebar**.
3. In NUI, select **ALL**, then **NEW** to add a connection.
4. Enter a name and your server address, such as `nats://NATS_HOST:4222`.
5. Choose the server's authentication method, enter its credentials and save.
6. Select the connection and use its action icons to browse streams, messages
   or key/value buckets.

NUI connects to the server from inside Home Assistant. `localhost` refers to
the NUI container, not your computer or another app. Use a hostname or address
reachable from Home Assistant. The broker's credentials are separate from your
Home Assistant sign-in.

## Access through Home Assistant

Ingress is the only supported access method. Home Assistant authenticates your
session and proxies the page, API and WebSocket connection. There are no host
ports to configure and no standalone LAN URL. Use **Open Web UI** or the sidebar;
do not bookmark an internal ingress URL, which is session-dependent.

The gateway accepts only HA Supervisor requests carrying a listed user's ID.
The NUI backend is reachable
only inside its own container. No HA API, host-network or privileged access is
required. When using HA remotely, use your normal secure HA access method.

Access to this app permits use of its saved NATS credentials. Broker permissions
determine what those connections can do; HA sign-in does not create separate
NATS accounts. Grant app access only to people who should manage those servers.

## Configuration

### Console administrators

Default: **empty**, which denies access to the interface, API and WebSockets.
List the Home Assistant user IDs authorized to manage every saved NUI connection.
Use the 32-character lowercase hexadecimal ID, not a name, password or access
token. Find it on the user's Home Assistant details page. Save and restart to
apply additions and removals; the previous list stays active until restart.
Changing a listed user's HA role does not remove them from this explicit list.
Only the read-only
health endpoint permits Supervisor requests without a user identity for Watchdog.

The administrator-only sidebar setting controls visibility; it does not enforce
ingress authorization. This list is the access boundary. An explicitly listed
user can manage all saved broker connections, so include only intended operators.
After upgrading from 0.4.1, populate this list before reopening NUI.

### Log detail

Default: **warn**. Choose the amount of NUI service detail shown in HA's Log tab:

- **warn:** warnings and errors; recommended for normal use.
- **info:** adds service lifecycle and connection diagnostics for troubleshooting.
- **error:** service errors only.

Save and restart to apply changes. The app launcher always reports startup,
readiness, shutdown and unexpected service exits. Routine HTTP access logs are
disabled. Review logs before sharing; diagnostic output can contain server names
and other connection metadata.

### Server connections

Manage server addresses and credentials inside NUI, not in the HA configuration
form. No broker is created by installing this app. Creating or modifying streams,
consumers, messages or buckets affects the connected server and its other clients.
Deleting or purging data is not a connectivity test.

## Persistence, updates and backups

Saved connections and credentials are stored in the app's persistent data volume.
Schema files use the same volume. Restarting and updating preserves them.
The browser's layout is stored separately in that browser, so another browser
can have a different layout while using the same server connections.

Include this app in Home Assistant backups. Cold backups briefly stop and restart
the app to copy consistent data. These backups contain saved credentials; protect
them. Backing up NUI does **not** back up the connected NATS server's messages.
Back up the broker separately. Uninstalling the app can remove its saved settings.

When updating from a release with a direct host port, clear the old port mapping,
update in place and reopen through HA. No connection re-entry is required.

## Troubleshooting

- **Page will not open:** check the app is running and open it from HA again.
  Old direct-port or internal ingress bookmarks are not supported.
- **403 Forbidden:** verify your Home Assistant user ID is listed in Console
  administrators, then save and restart. An empty list deliberately blocks access.
- **Connection fails:** verify the broker is reachable from HA and check its
  port, authentication method, token or credentials, and TLS requirements.
  After correcting a failed connection change, reopen the connection or retry
  the operation; a failed refresh no longer requires restarting the app.
- **Connected but no streams:** confirm the broker has JetStream enabled and
  the selected account has streams and permission to list them.
- **Live updates stop:** reopen the app from HA. If using an external HA reverse
  proxy, confirm it supports WebSocket upgrades. Check both NUI and broker logs.
- **Empty layout:** select ALL to open your connections. This app initializes missing browser layout settings automatically; saved connections are stored separately.
- **App restarts repeatedly:** read the preceding service-exit message and check
  data-volume space and permissions. The watchdog restarts the complete app if
  the interface service or ingress gateway fails.

For support, include the app version, browser, relevant error lines and reproduction
steps. Remove credentials and private message content before sharing.

## Learn more

- [NUI project](https://github.com/nats-nui/nui)
- [NATS documentation](https://docs.nats.io/)
- [Report an app issue](https://github.com/jeffglousher/ha-nats-nui/issues)

## Security boundaries

The ingress panel is hidden from non-administrators. Home Assistant authenticates
the session; the gateway separately authorizes the configured user IDs, then
the gateway strips HA credentials before forwarding and rejects cross-site browser
requests. NUI manages broker credentials and can modify broker data: grant access
only to broker administrators. Schema files are confined to the configured schema
directory. The image rebuilds patched dependencies and runs security regression
tests before installation.
