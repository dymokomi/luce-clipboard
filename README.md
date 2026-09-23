# luce-clipboard

The system clipboard: read and write text.

## Modules

| import | what it holds |
| --- | --- |
| `import clipboard` | The desktop text clipboard |

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

macOS and Windows.

Native libraries it links, by platform (declared in `package.prisma`, linked only when the program reaches code that needs them):

- macos: AppKit, Foundation
- windows: user32

## Tests

`./test.sh` runs every module's `test` blocks and the unit tests through the native and C backends, then the program checks under `tests/programs`. It expects the compiler beside this checkout at `../luce-base/build/luce-base` (or `--base PATH`).

## License

MIT or Apache-2.0, at your option.
