import os
from datetime import datetime
import json
from pathlib import Path
import re
import sys

class BlogManager:
    def __init__(self):
        # Set fixed directory path
        self.blog_dir = Path("/Users/akankshayadav/diary")
        self.entries_dir = self.blog_dir / 'entries'
        self.posts_dir = self.blog_dir / 'posts'
        
        # Create necessary directories if they don't exist
        self.entries_dir.mkdir(exist_ok=True)
        self.posts_dir.mkdir(exist_ok=True)
        
        # Load or create entries database
        self.db_file = self.blog_dir / 'entries.json'
        if self.db_file.exists():
            with open(self.db_file, 'r') as f:
                self.entries = json.load(f)
        else:
            self.entries = []
            
        # Ensure we're in the correct directory
        if not self.blog_dir.exists():
            raise RuntimeError(f"Blog directory not found at {self.blog_dir}")

    def process_entry_file(self, file_path):
        """Process an entry file and create blog post"""
        file_path = Path(file_path)
        if not file_path.exists():
            print(f"Error: File not found at {file_path}")
            return False

        with open(file_path, 'r') as f:
            content = f.read()

        # Parse the entry file
        try:
            # Split by '---' separator
            parts = content.split('---\n')
            if len(parts) < 3:
                raise ValueError("Invalid file format. Expected title and content separated by '---'")
            
            title = parts[1].strip()
            entry_content = parts[2].strip()
            
            self.create_entry(title, entry_content)
            print(f"Successfully created entry: {title}")
            return True
        except Exception as e:
            print(f"Error processing file: {e}")
            return False

    def create_entry(self, title, content):
        """Create a new blog entry"""
        date = datetime.now()
        date_str = date.strftime('%B %d, %Y')
        
        # Create entry slug
        slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
        filename = f"{slug}.html"
        
        # Create entry HTML
        entry_html = self._create_entry_html(title, date_str, content)
        
        # Save entry file
        entry_path = self.entries_dir / filename
        with open(entry_path, 'w') as f:
            f.write(entry_html)
        print(f"Created entry file: {entry_path}")
        
        # Update entries database
        entry_data = {
            'date': date_str,
            'title': title,
            'slug': slug,
            'content': content
        }
        self.entries.insert(0, entry_data)  # Add to start of list
        
        # Save updated database
        with open(self.db_file, 'w') as f:
            json.dump(self.entries, f, indent=2)
        
        # Update index and archive pages
        self._update_index_page()
        self._update_archive_page()

    def _create_entry_html(self, title, date, content):
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Reflections</title>
    <style>
        body {{
            font-family: system-ui, -apple-system, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 2rem auto;
            padding: 0 1rem;
            color: #333;
        }}
        nav {{
            margin: 2rem 0;
        }}
        nav a {{
            margin-right: 1rem;
            text-decoration: none;
            color: #555;
        }}
        .entry-date {{
            font-weight: bold;
            margin-top: 2rem;
            color: #666;
        }}
        .entry-content {{
            margin: 1rem 0 2rem;
            white-space: pre-wrap;
        }}
        footer {{
            margin-top: 3rem;
            padding-top: 1rem;
            border-top: 1px solid #eee;
            color: #666;
            font-size: 0.9rem;
        }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    
    <nav>
        <a href="../index.html">Home</a>
        <a href="../archive.html">Archive</a>
    </nav>

    <main>
        <article class="entry">
            <div class="entry-date">{date}</div>
            <div class="entry-content">
                {content}
            </div>
        </article>
    </main>

    <footer>
        © {datetime.now().year} Akanksha Yadav. All rights reserved.
    </footer>
</body>
</html>'''

    def _update_index_page(self):
        """Update the index page with the most recent entry"""
        if not self.entries:
            return
        
        latest = self.entries[0]
        index_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reflections</title>
    <style>
        body {{
            font-family: system-ui, -apple-system, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 2rem auto;
            padding: 0 1rem;
            color: #333;
        }}
        nav {{
            margin: 2rem 0;
        }}
        nav a {{
            margin-right: 1rem;
            text-decoration: none;
            color: #555;
        }}
        .entry-date {{
            font-weight: bold;
            margin-top: 2rem;
            color: #666;
        }}
        .entry-content {{
            margin: 1rem 0 2rem;
            white-space: pre-wrap;
        }}
        footer {{
            margin-top: 3rem;
            padding-top: 1rem;
            border-top: 1px solid #eee;
            color: #666;
            font-size: 0.9rem;
        }}
    </style>
</head>
<body>
    <h1>Reflections</h1>
    
    <nav>
        <a href="index.html">Home</a>
        <a href="archive.html">Archive</a>
    </nav>

    <main>
        <article class="entry">
            <div class="entry-date">{latest['date']}</div>
            <div class="entry-content">
                {latest['content']}
            </div>
        </article>
    </main>

    <footer>
        © {datetime.now().year} Akanksha Yadav. All rights reserved.
    </footer>
</body>
</html>'''
        
        with open(self.blog_dir / 'index.html', 'w') as f:
            f.write(index_html)

    def _update_archive_page(self):
        """Update the archive page with all entries"""
        entries_html = ''
        for entry in self.entries:
            entries_html += f'''
            <li class="archive-item">
                <span class="entry-date">{entry['date']}</span>
                <a href="entries/{entry['slug']}.html" class="entry-title">{entry['title']}</a>
            </li>'''

        archive_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Archive - Reflections</title>
    <style>
        body {{
            font-family: system-ui, -apple-system, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 2rem auto;
            padding: 0 1rem;
            color: #333;
        }}
        nav {{
            margin: 2rem 0;
        }}
        nav a {{
            margin-right: 1rem;
            text-decoration: none;
            color: #555;
        }}
        .archive-list {{
            list-style: none;
            padding: 0;
        }}
        .archive-item {{
            margin: 1rem 0;
            display: flex;
            align-items: baseline;
        }}
        .entry-date {{
            min-width: 150px;
            color: #666;
        }}
        .entry-title {{
            text-decoration: none;
            color: #333;
        }}
        .entry-title:hover {{
            text-decoration: underline;
        }}
        footer {{
            margin-top: 3rem;
            padding-top: 1rem;
            border-top: 1px solid #eee;
            color: #666;
            font-size: 0.9rem;
        }}
    </style>
</head>
<body>
    <h1>Archive</h1>
    
    <nav>
        <a href="index.html">Home</a>
        <a href="archive.html">Archive</a>
    </nav>

    <main>
        <ul class="archive-list">
            {entries_html}
        </ul>
    </main>

    <footer>
        © {datetime.now().year} Akanksha Yadav. All rights reserved.
    </footer>
</body>
</html>'''
        
        with open(self.blog_dir / 'archive.html', 'w') as f:
            f.write(archive_html)

def main():
    if len(sys.argv) != 2:
        print("Usage: python blog_manager.py <entry_file.txt>")
        print("Example: python blog_manager.py posts/my-new-entry.txt")
        sys.exit(1)
    
    try:
        blog = BlogManager()
        entry_file = sys.argv[1]
        
        if blog.process_entry_file(entry_file):
            print("\nBlog updated successfully!")
            print(f"\nNext steps:")
            print("1. git add .")
            print('2. git commit -m "Add new entry: [Your Entry Title]"')
            print("3. git push origin main")
        else:
            print("\nFailed to create entry. Please check the error message above.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()