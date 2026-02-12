# CSV to Safari Bookmarks

This project includes a script to convert a CSV list of URLs into a Safari-importable bookmarks HTML file.

## Script

`/Users/lou/Documents/New project/scripts/csv_to_safari_bookmarks.py`

## Usage

```bash
python3 '/Users/lou/Documents/New project/scripts/csv_to_safari_bookmarks.py' \
  --input '/Users/lou/Documents/csv/lol.csv' \
  --output '/Users/lou/Documents/New project/output/safari_bookmarks/lol_bookmarks.html'
```

Optional flags:

- `--folder "Folder Name"`: Override default folder name (defaults to input filename stem).
- `--allow-non-http`: Include non-http(s) URLs that still have a scheme and host.

## Safari Import

1. Open Safari.
2. Click `File`.
3. Click `Import From`.
4. Click `Bookmarks HTML File...`.
5. Select the generated `.html` file.

