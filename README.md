# Arc Browser Pinned Favourite Folders, Subfolders and Pages to Bookmarks Exporter

Export your pinned tabs and folders from Arc browser to a standard HTML bookmarks file that can be imported into any browser (Chrome, Brave, Firefox, Safari, Edge, etc.)

## Features

- ✅ Exports **pinned tabs only** (not open tabs)
- ✅ Organizes bookmarks **by Space**
- ✅ **Flattens subfolders** for easy browsing
- ✅ Preserves bookmark titles and URLs
- ✅ Works on **macOS and Windows**
- ✅ No dependencies (Python standard library only)

## Why?

Arc browser doesn't have a built-in export feature for your pinned tabs and folders. This script reads Arc's data file directly and converts it to the standard Netscape bookmark format that all browsers understand.

## Usage

### Quick Start (macOS)

```bash
# Clone the repo
git clone https://github.com/ditty007/ArcExporter.git
cd ArcExporter

# Run the script (it will find Arc's data automatically)
python3 ArcExporter.py

# Import arc_bookmarks.html into your browser
```

### Custom Path

If the script can't find your Arc data, provide the path manually:

```bash
python3 arc_to_bookmarks.py ~/Library/Application\ Support/Arc/StorableSidebar.json
```

### Arc Data Location

| OS | Path |
|---|---|
| macOS | `~/Library/Application Support/Arc/StorableSidebar.json` |
| Windows | `%LOCALAPPDATA%\Packages\TheBrowserCompany.Arc*\LocalCache\Local\Arc\StorableSidebar.json` |

## Importing Bookmarks

After running the script, import `arc_bookmarks.html` into your browser:

### Brave / Chrome
1. Open `brave://bookmarks` or `chrome://bookmarks`
2. Click the three dots menu (⋮)
3. Select "Import bookmarks"
4. Choose the `arc_bookmarks.html` file

### Firefox
1. Press `Ctrl+Shift+O` (or `Cmd+Shift+O` on Mac)
2. Click "Import and Backup" → "Import Bookmarks from HTML"
3. Choose the `arc_bookmarks.html` file

### Safari
1. File → Import From → Bookmarks HTML File
2. Choose the `arc_bookmarks.html` file

## Output Structure

The exported bookmarks are organized like this:

```
Arc Bookmarks/
├── Space 1 (e.g., "me")/
│   ├── Folder A/
│   │   └── bookmarks...
│   ├── Folder B/
│   │   └── bookmarks...
│   └── standalone bookmarks...
├── Space 2 (e.g., "work")/
│   └── ...
└── Space 3/
    └── ...
```

## Requirements

- Python 3.6+
- No external dependencies

## License

MIT License - feel free to use, modify, and share.

## Contributing

Pull requests welcome! If you find a bug or have a feature request, please open an issue.
