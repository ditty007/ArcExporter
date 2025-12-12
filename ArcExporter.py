#!/usr/bin/env python3
"""
Arc Browser to Bookmarks Exporter

Exports pinned tabs and folders from Arc browser to a standard HTML bookmarks file
that can be imported into any browser (Chrome, Brave, Firefox, Safari, etc.)

Usage:
    python arc_to_bookmarks.py                    # Uses default Arc location
    python arc_to_bookmarks.py /path/to/StorableSidebar.json   # Custom path

Output:
    arc_bookmarks.html - Import this file into your browser
"""

import json
import html
import os
import sys
from pathlib import Path
from datetime import datetime


def get_default_arc_path():
    """Get the default Arc browser data path based on OS"""
    if sys.platform == "darwin":  # macOS
        return Path.home() / "Library/Application Support/Arc/StorableSidebar.json"
    elif sys.platform == "win32":  # Windows
        local_app_data = os.environ.get("LOCALAPPDATA", "")
        arc_path = Path(local_app_data) / "Packages"
        # Find the Arc folder (name varies)
        for folder in arc_path.glob("TheBrowserCompany.Arc*"):
            json_path = folder / "LocalCache/Local/Arc/StorableSidebar.json"
            if json_path.exists():
                return json_path
        return None
    else:
        return None


def load_arc_data(filepath):
    """Load and parse the Arc StorableSidebar.json file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_item_type(item):
    """Determine if an item is a folder or tab"""
    if 'data' not in item:
        return None
    if 'list' in item['data']:
        return 'folder'
    elif 'tab' in item['data']:
        return 'tab'
    return None


def escape_html_text(text):
    """Safely escape HTML characters"""
    return html.escape(str(text)) if text else ''


def get_folder_with_direct_tabs(item_id, items_by_id):
    """Get a folder with only its direct tab children (not subfolders)"""
    if item_id not in items_by_id:
        return None
    
    item = items_by_id[item_id]
    if get_item_type(item) != 'folder':
        return None
    
    tabs = []
    for child_id in item.get('childrenIds', []):
        if child_id in items_by_id:
            child = items_by_id[child_id]
            if get_item_type(child) == 'tab':
                tab_data = child['data']['tab']
                url = tab_data.get('savedURL', '')
                title = child.get('title') or tab_data.get('savedTitle', '') or 'Untitled'
                if url:
                    tabs.append({'title': title, 'url': url})
    
    return {
        'title': item.get('title') or 'Untitled Folder',
        'tabs': tabs
    }


def get_all_folders_flat(item_id, items_by_id, collected=None):
    """Recursively get all folders (including nested) as a flat list"""
    if collected is None:
        collected = []
    
    if item_id not in items_by_id:
        return collected
    
    item = items_by_id[item_id]
    if get_item_type(item) != 'folder':
        return collected
    
    # Add this folder if it has tabs
    folder = get_folder_with_direct_tabs(item_id, items_by_id)
    if folder and folder['tabs']:
        collected.append(folder)
    
    # Recurse into subfolders
    for child_id in item.get('childrenIds', []):
        if child_id in items_by_id:
            child = items_by_id[child_id]
            if get_item_type(child) == 'folder':
                get_all_folders_flat(child_id, items_by_id, collected)
    
    return collected


def export_bookmarks(data):
    """Export Arc data to HTML bookmarks format"""
    containers = data.get('sidebar', {}).get('containers', [])
    
    if not containers:
        print("Error: No containers found in Arc data")
        return None
    
    last_container = containers[-1]
    
    # Get spaces info
    spaces = []
    for space in last_container.get('spaces', []):
        if isinstance(space, dict) and 'title' in space:
            space_info = {
                'id': space['id'],
                'title': space['title'],
                'pinned_container': None,
            }
            container_ids = space.get('containerIDs', [])
            for i, cid in enumerate(container_ids):
                if cid == 'pinned' and i + 1 < len(container_ids):
                    space_info['pinned_container'] = container_ids[i + 1]
            spaces.append(space_info)
    
    if not spaces:
        print("Error: No spaces found in Arc data")
        return None
    
    # Build items dictionary
    items = last_container.get('items', [])
    items_by_id = {}
    for i in range(0, len(items), 2):
        if i + 1 < len(items):
            item_data = items[i + 1]
            if isinstance(item_data, dict) and 'id' in item_data:
                items_by_id[item_data['id']] = item_data
    
    # Generate HTML
    html_lines = [
        '<!DOCTYPE NETSCAPE-Bookmark-file-1>',
        '<!-- Exported from Arc Browser using arc_to_bookmarks.py -->',
        f'<!-- Export date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} -->',
        '<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">',
        '<TITLE>Arc Bookmarks</TITLE>',
        '<H1>Arc Bookmarks</H1>',
        '<DL><p>'
    ]
    
    total_folders = 0
    total_bookmarks = 0
    
    for space in spaces:
        pinned_container_id = space['pinned_container']
        
        # Find all top-level items in this space's pinned container
        top_level_items = []
        for item_id, item in items_by_id.items():
            if item.get('parentID') == pinned_container_id:
                top_level_items.append(item_id)
        
        if not top_level_items:
            continue
        
        html_lines.append(f'    <DT><H3>{escape_html_text(space["title"])}</H3>')
        html_lines.append('    <DL><p>')
        
        # Collect all folders (flattened) and standalone tabs
        all_folders = []
        standalone_tabs = []
        
        for item_id in top_level_items:
            item = items_by_id[item_id]
            item_type = get_item_type(item)
            
            if item_type == 'folder':
                folders = get_all_folders_flat(item_id, items_by_id)
                all_folders.extend(folders)
            elif item_type == 'tab':
                tab_data = item['data']['tab']
                url = tab_data.get('savedURL', '')
                title = item.get('title') or tab_data.get('savedTitle', '') or 'Untitled'
                if url:
                    standalone_tabs.append({'title': title, 'url': url})
        
        # Write folders
        for folder in all_folders:
            html_lines.append(f'        <DT><H3>{escape_html_text(folder["title"])}</H3>')
            html_lines.append('        <DL><p>')
            for tab in folder['tabs']:
                html_lines.append(f'            <DT><A HREF="{escape_html_text(tab["url"])}">{escape_html_text(tab["title"])}</A>')
                total_bookmarks += 1
            html_lines.append('        </DL><p>')
            total_folders += 1
        
        # Write standalone tabs
        for tab in standalone_tabs:
            html_lines.append(f'        <DT><A HREF="{escape_html_text(tab["url"])}">{escape_html_text(tab["title"])}</A>')
            total_bookmarks += 1
        
        html_lines.append('    </DL><p>')
    
    html_lines.append('</DL><p>')
    
    return {
        'html': '\n'.join(html_lines),
        'folders': total_folders,
        'bookmarks': total_bookmarks,
        'spaces': len(spaces)
    }


def main():
    # Determine input file path
    if len(sys.argv) > 1:
        input_path = Path(sys.argv[1])
    else:
        input_path = get_default_arc_path()
        if not input_path:
            print("Error: Could not find Arc browser data.")
            print("Please provide the path to StorableSidebar.json as an argument.")
            print("\nUsage: python arc_to_bookmarks.py /path/to/StorableSidebar.json")
            sys.exit(1)
    
    if not input_path.exists():
        print(f"Error: File not found: {input_path}")
        sys.exit(1)
    
    print(f"Reading Arc data from: {input_path}")
    
    # Load and export
    try:
        data = load_arc_data(input_path)
        result = export_bookmarks(data)
        
        if not result:
            sys.exit(1)
        
        # Write output file
        output_path = Path("arc_bookmarks.html")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result['html'])
        
        print(f"\n✓ Export successful!")
        print(f"  Spaces: {result['spaces']}")
        print(f"  Folders: {result['folders']}")
        print(f"  Bookmarks: {result['bookmarks']}")
        print(f"\nOutput saved to: {output_path.absolute()}")
        print("\nTo import into your browser:")
        print("  1. Open your browser's bookmark manager")
        print("  2. Look for 'Import bookmarks' option")
        print("  3. Select 'Bookmarks HTML file'")
        print("  4. Choose the arc_bookmarks.html file")
        
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in Arc data file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
