import os
from datetime import datetime
import json
from pathlib import Path
import re
import sys

class BlogManager:
    def __init__(self):
        # Existing initialization code remains the same
        self.blog_dir = Path("/Users/akankshayadav/diary")
        self.entries_dir = self.blog_dir / 'entries'
        self.posts_dir = self.blog_dir / 'posts'
        self.assets_dir = self.blog_dir / 'assets'
        
        # Create necessary directories if they don't exist
        self.entries_dir.mkdir(exist_ok=True)
        self.posts_dir.mkdir(exist_ok=True)
        self.assets_dir.mkdir(exist_ok=True)
        
        # Create CSS file if it doesn't exist
        self.css_file = self.assets_dir / 'styles.css'
        if not self.css_file.exists():
            with open(self.css_file, 'w') as f:
                f.write(self._get_css_content())
        
        # Add .nojekyll file to prevent Jekyll processing
        nojekyll_file = self.blog_dir / '.nojekyll'
        if not nojekyll_file.exists():
            nojekyll_file.touch()
        
        # Load or create entries database
        self.db_file = self.blog_dir / 'entries.json'
        if self.db_file.exists():
            with open(self.db_file, 'r') as f:
                self.entries = json.load(f)
        else:
            self.entries = []

    def _get_css_content(self):
        """Return the content of the CSS file"""
        return '''
:root[data-theme="light"] {
    --background: #fafafa;
    --card-background: white;
    --text: #333;
    --text-muted: #666;
    --border: #eee;
    --border-muted: #ddd;
    --toggle-icon: "☾";
}

:root[data-theme="dark"] {
    --background: #1a1a1a;
    --card-background: #2a2a2a;
    --text: #e0e0e0;
    --text-muted: #999;
    --border: #3a3a3a;
    --border-muted: #404040;
    --toggle-icon: "☼";
}

body {
    font-family: "Georgia", serif;
    line-height: 1.6;
    max-width: 800px;
    margin: 0 auto;
    padding: 2rem;
    background: var(--background);
    color: var(--text);
    transition: background-color 0.3s ease, color 0.3s ease;
}

header {
    margin-bottom: 2rem;
}

h1 {
    font-size: 2rem;
    font-weight: normal;
    margin: 0;
    margin-bottom: 1rem;
}

nav {
    margin-bottom: 2rem;
}

nav a {
    color: var(--text);
    text-decoration: none;
    margin-right: 1rem;
}

nav a:hover {
    text-decoration: underline;
}

.entry {
    margin-bottom: 3rem;
}

.entry-date {
    color: var(--text-muted);
    font-size: 0.9rem;
    margin-bottom: 0.5rem;
}

.entry-title {
    font-size: 1.5rem;
    font-weight: normal;
    margin-bottom: 1rem;
    color: var(--text);
}

.entry-content {
    margin: 0;
    line-height: 1.8;
    white-space: pre-wrap;
}

footer {
    margin-top: 3rem;
    padding-top: 1rem;
    border-top: 1px solid var(--border-muted);
    color: var(--text-muted);
    font-size: 0.9rem;
    text-align: center;
}

#theme-toggle {
    position: absolute;
    top: 1rem;
    right: 1rem;
    background: none;
    border: none;
    color: var(--text-muted);
    cursor: pointer;
    font-size: 1.2rem;
    padding: 0.5rem;
    width: 2.5rem;
    height: 2.5rem;
    border-radius: 50%;
    transition: all 0.3s ease;
    opacity: 0.7;
}

#theme-toggle:hover {
    opacity: 1;
    background: var(--border);
}

#theme-toggle::after {
    content: var(--toggle-icon);
}

.archive-list {
    list-style: none;
    padding: 0;
}

.archive-item {
    margin-bottom: 1rem;
    display: flex;
    align-items: baseline;
}

.archive-title {
    color: var(--text);
    text-decoration: none;
}

.archive-title:hover {
    text-decoration: underline;
}'''

    def _create_entry_html(self, title, date, content):
        return f'''<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="stylesheet" href="../assets/styles.css">
</head>
<body>
    <button id="theme-toggle" aria-label="Toggle theme"></button>
    
    <header>
        <h1>Reflections</h1>
        <nav>
            <a href="../index.html">Home</a>
            <a href="../archive.html">Archive</a>
        </nav>
    </header>

    <main>
        <article class="entry">
            <div class="entry-date">{date}</div>
            <h2 class="entry-title">{title}</h2>
            <div class="entry-content">{content}</div>
        </article>
    </main>

    <footer>
        <p>© {datetime.now().year} Akanksha Yadav. All rights reserved.</p>
    </footer>

    <script>
        document.getElementById('theme-toggle').addEventListener('click', () => {{
            const html = document.documentElement;
            const currentTheme = html.getAttribute('data-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            html.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
        }});

        const savedTheme = localStorage.getItem('theme') || 'dark';
        document.documentElement.setAttribute('data-theme', savedTheme);
    </script>
</body>
</html>'''

    def _update_index_page(self):
        """Update the index page with the most recent entry"""
        if not self.entries:
            return
        
        latest = self.entries[0]
        index_html = f'''<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reflections</title>
    <link rel="stylesheet" href="assets/styles.css">
</head>
<body>
    <button id="theme-toggle" aria-label="Toggle theme"></button>

    <header>
        <h1>Reflections</h1>
        <nav>
            <a href="index.html">Home</a>
            <a href="archive.html">Archive</a>
        </nav>
    </header>

    <main>
        <article class="entry">
            <div class="entry-date">{latest['date']}</div>
            <h2 class="entry-title">{latest['title']}</h2>
            <div class="entry-content">{latest['content']}</div>
        </article>
    </main>

    <footer>
        <p>© {datetime.now().year} Akanksha Yadav. All rights reserved.</p>
    </footer>

    <script>
        document.getElementById('theme-toggle').addEventListener('click', () => {{
            const html = document.documentElement;
            const currentTheme = html.getAttribute('data-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            html.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
        }});

        const savedTheme = localStorage.getItem('theme') || 'dark';
        document.documentElement.setAttribute('data-theme', savedTheme);
    </script>
</body>
</html>'''
        
        with open(self.blog_dir / 'index.html', 'w') as f:
            f.write(index_html)

    def _update_archive_page(self):
        """Update the archive page with all entries"""
        entries_html = ''
        for entry in self.entries:
            entries_html += f'''
               <li class="entry-item">
                  <span class="entry-date">{entry['date']}</span>
                  <a href="entries/{entry['slug']}.html" class="archive-title">{entry['title']}</a>
               </li>
            </div>'''

        archive_html = f'''<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Archive - Reflections</title>
    <link rel="stylesheet" href="assets/styles.css">
</head>
<body>
    <button id="theme-toggle" aria-label="Toggle theme"></button>

    <header>
        <h1>Reflections</h1>
        <nav>
            <a href="index.html">Home</a>
            <a href="archive.html">Archive</a>
        </nav>
    </header>

    <main>
        <div class="entry-list">
            {entries_html}
        </div>
    </main>

    <footer>
        <p>© {datetime.now().year} Akanksha Yadav. All rights reserved.</p>
    </footer>

    <script>
        document.getElementById('theme-toggle').addEventListener('click', () => {{
            const html = document.documentElement;
            const currentTheme = html.getAttribute('data-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            html.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
        }});

        const savedTheme = localStorage.getItem('theme') || 'dark';
        document.documentElement.setAttribute('data-theme', savedTheme);
    </script>
</body>
</html>'''
        
        with open(self.blog_dir / 'archive.html', 'w') as f:
            f.write(archive_html)


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
        self.entries.insert(0, entry_data)
        
        # Save updated database
        with open(self.db_file, 'w') as f:
            json.dump(self.entries, f, indent=2)
        
        # Update index and archive pages
        self._update_index_page()
        self._update_archive_page()
        print("Updated index.html and archive.html")

def main():
    if len(sys.argv) != 2:
        print("Usage: python blog_manager.py <entry_file.txt>")
        print("Example: python blog_manager.py posts/my-new-entry.txt")
        sys.exit(1)
    
    try:
        blog = BlogManager()

        if sys.argv[1] in ["--update", "-u"]:
            # Just update the HTML files without creating new entry
            blog._update_index_page()
            blog._update_archive_page()
            print("\nBlog files updated successfully!")
            print(f"\nNext steps:")
            print("1. git add .")
            print('2. git commit -m "Update blog files"')
            print("3. git push origin main")
        else:
            
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