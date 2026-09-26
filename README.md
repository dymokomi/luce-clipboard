# luce-clipboard

The system clipboard: read and write text and images.

## Modules

| import | what it holds |
| --- | --- |
| `import clipboard` | The desktop clipboard: text, and images as PNG (plus a bitmap on Windows) |

## Using it

Add the dependency to `package.prisma`; the modules keep their short names:

```prisma
def dependency "luce-clipboard" {
    str owner = "dymokomi"
    str version = "^0.1.0"
}
```

## Depends on

- luce-std
- luce-window

## Platforms

macOS, Windows and Linux. On Linux the clipboard is X11's CLIPBOARD selection (under
Wayland, through XWayland): libX11.so.6 is loaded at run time, and the clipboard keeps a
connection and a thread of its own that answers other programs for what this one copied.
Text goes as UTF8_STRING (STRING for older programs), images as image/png, large ones in
INCR steps. Without an X display the clipboard reports `window.unsupported`.

Native libraries it links, by platform (declared in `package.prisma`, linked only when the program reaches code that needs them):

- macos: AppKit, Foundation
- windows: user32
- linux: none at link time (libX11.so.6 is opened when the clipboard is first used)

## Tests

`./test.sh` runs every module's `test` blocks and the unit tests through the native and C backends, then the program checks under `tests/programs`. The X11 check (`tests/programs/x11`) runs on Linux with a display or Xvfb, between real processes, and with xclip when installed. It expects the compiler beside this checkout at `../luce-base/build/luce-base` (or `--base PATH`).

## License

MIT or Apache-2.0, at your option.
