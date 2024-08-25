#!/usr/bin/python3
"""
markdown2html.py: Converts a Markdown file to an HTML file.
"""

import sys
import os
import re
import hashlib

def md5_conversion(text):
    return hashlib.md5(text.encode()).hexdigest()

def remove_c(text):
    return text.replace('c', '').replace('C', '')

def convert_bold_emphasis(text):
    # Convert bold: **text** -> <b>text</b>
    text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
    # Convert emphasis: __text__ -> <em>text</em>
    text = re.sub(r"__(.*?)__", r"<em>\1</em>", text)
    return text

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: ./markdown2html.py README.md README.html", file=sys.stderr)
        sys.exit(1)
    
    md_file = sys.argv[1]
    html_file = sys.argv[2]

    if not os.path.exists(md_file):
        print(f"Missing {md_file}", file=sys.stderr)
        sys.exit(1)
    
    with open(md_file, "r") as file:
        content = file.readlines()
    
    html_content = []
    in_ul = in_ol = in_paragraph = False

    for line in content:
        line = line.strip()

        if "[[" in line and "]]" in line:
            match = re.search(r"\[\[(.*?)\]\]", line)
            if match:
                line = line.replace(match.group(0), md5_conversion(match.group(1)))

        if "((" in line and "))" in line:
            match = re.search(r"\(\((.*?)\)\)", line)
            if match:
                line = line.replace(match.group(0), remove_c(match.group(1)))

        line = convert_bold_emphasis(line)

        if line.startswith("#"):
            if in_paragraph:
                html_content.append("</p>")
                in_paragraph = False
            level = len(line.split(" ")[0])
            heading_text = line.strip("#").strip()
            html_content.append(f"<h{level}>{heading_text}</h{level}>")
        
        elif line.startswith("-"):
            if in_paragraph:
                html_content.append("</p>")
                in_paragraph = False
            if not in_ul:
                html_content.append("<ul>")
                in_ul = True
            html_content.append(f"<li>{line[1:].strip()}</li>")
        
        elif line.startswith("*"):
            if in_paragraph:
                html_content.append("</p>")
                in_paragraph = False
            if not in_ol:
                html_content.append("<ol>")
                in_ol = True
            html_content.append(f"<li>{line[1:].strip()}</li>")
        
        else:
            if in_ul:
                html_content.append("</ul>")
                in_ul = False
            if in_ol:
                html_content.append("</ol>")
                in_ol = False

            if line:
                # Handle multi-line paragraphs with <br/> tags
                if in_paragraph:
                    html_content[-1] += f"<br/>{line}"
                else:
                    html_content.append(f"<p>{line}")
                    in_paragraph = True
            elif in_paragraph:
                # Close paragraph when a blank line is encountered
                html_content.append("</p>")
                in_paragraph = False

    if in_ul:
        html_content.append("</ul>")
    if in_ol:
        html_content.append("</ol>")
    if in_paragraph:
        html_content.append("</p>")

    with open(html_file, "w") as file:
        file.write("\n".join(html_content))
    
    sys.exit(0)
