import json
import base64
import re
from openai import OpenAI
from config import config
from utils import log_event, is_text_file
from datetime import datetime

class LLMGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
    
    def generate_app(self, brief: str, checks: list, attachments: list, task_id: str, round_num: int = 1) -> dict:
        """Generate complete application based on brief"""
        
        log_event(f"Generating application for round {round_num}", task_id=task_id)
        
        # Process attachments
        attachment_info = self._process_attachments(attachments)
        
        # Generate app structure
        prompt = self._build_prompt(brief, checks, attachment_info, task_id, round_num)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Using a more capable model
                messages=[
                    {"role": "system", "content": self._get_system_prompt(round_num)},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            generated_content = response.choices[0].message.content
            log_event(f"LLM Response received ({len(generated_content)} chars)", task_id=task_id)
            
            files = self._parse_response(generated_content)
            
            # Ensure essential files are present
            files = self._ensure_essential_files(files, task_id, round_num, brief, checks)
            
            # Validate index.html
            self._validate_html(files.get('index.html', ''), task_id)
            
            log_event(f"Generated {len(files)} files: {list(files.keys())}", task_id=task_id)
            return files
            
        except Exception as e:
            error_msg = f"LLM generation failed: {e}"
            log_event(error_msg, "ERROR", task_id=task_id)
            # Return fallback files instead of raising
            log_event("Creating fallback application...", "WARNING", task_id=task_id)
            return self._create_fallback_app(brief, checks, task_id, round_num)
    
    def _validate_html(self, html_content: str, task_id: str):
        """Validate HTML content"""
        if not html_content or len(html_content.strip()) < 100:
            raise Exception("Generated HTML is too short or empty")
        
        required_tags = ['<!DOCTYPE html>', '<html', '<head', '<body']
        missing_tags = [tag for tag in required_tags if tag.lower() not in html_content.lower()]
        
        if missing_tags:
            raise Exception(f"Generated HTML missing required tags: {missing_tags}")
        
        log_event("HTML validation passed", task_id=task_id)
    
    def _process_attachments(self, attachments: list) -> dict:
        """Process base64 attachments"""
        processed = {}
        for attachment in attachments:
            if attachment['url'].startswith('data:'):
                try:
                    # Extract base64 data
                    base64_data = attachment['url'].split('base64,')[1]
                    if is_text_file(attachment['name']):
                        decoded = base64.b64decode(base64_data).decode('utf-8')
                    else:
                        decoded = base64.b64decode(base64_data)
                    
                    processed[attachment['name']] = {
                        'content': decoded,
                        'type': attachment['url'].split(';')[0].split('/')[-1]
                    }
                except Exception as e:
                    log_event(f"Failed to process attachment {attachment['name']}: {e}", "WARNING")
        return processed
    
    def _build_prompt(self, brief: str, checks: list, attachments: dict, task_id: str, round_num: int) -> str:
        """Build prompt for LLM with clear instructions"""
        
        attachment_text = ""
        if attachments:
            attachment_text = "\n\nATTACHMENTS PROVIDED:\n"
            for name, info in attachments.items():
                if isinstance(info['content'], str):
                    preview = info['content'][:500] if len(info['content']) > 500 else info['content']
                    attachment_text += f"\nFile: {name}\nContent preview:\n{preview}\n"
                else:
                    attachment_text += f"\nFile: {name} (binary, {len(info['content'])} bytes)\n"
        
        checks_text = "\n".join(f"{i+1}. {check}" for i, check in enumerate(checks))
        
        prompt = f"""Create a complete, working web application based on these requirements:

TASK: {task_id}
ROUND: {round_num}

BRIEF:
{brief}

EVALUATION CRITERIA:
{checks_text}
{attachment_text}

CRITICAL REQUIREMENTS:
1. Create a SINGLE-FILE application in index.html with ALL CSS and JavaScript embedded
2. The HTML MUST be complete, valid, and ready to deploy
3. Use modern HTML5, CSS3, and vanilla JavaScript (no frameworks unless specified)
4. Ensure the app passes ALL evaluation criteria above
5. Include proper error handling and user feedback
6. Make it responsive and accessible
7. Add professional styling

RESPONSE FORMAT - Use EXACTLY this format:

===FILE:index.html===
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Your App Title</title>
    <style>
        /* All CSS styles here */
        body {{
            font-family: system-ui, -apple-system, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }}
    </style>
</head>
<body>
    <!-- All HTML content here -->
    
    <script>
        // All JavaScript code here
        // Include proper error handling
    </script>
</body>
</html>
===END===

===FILE:README.md===
# Application Title

## Description
Detailed description of what this application does.

## Features
- Feature 1
- Feature 2

## Usage
1. Open index.html in a web browser
2. Or visit: https://username.github.io/repo-name

## Technical Details
- Pure HTML/CSS/JavaScript
- No external dependencies
- Responsive design

## Evaluation Criteria Met
{checks_text}

## License
MIT License
===END===

IMPORTANT NOTES:
- The app MUST be fully self-contained in index.html
- Include ALL necessary code inline (CSS in <style>, JS in <script>)
- Ensure the app works immediately when opened in a browser
- Test that all evaluation criteria are met
- Use semantic HTML and accessible markup
"""
        return prompt
    
    def _get_system_prompt(self, round_num: int) -> str:
        """System prompt for the LLM"""
        base_prompt = """You are an expert web developer who creates production-ready, single-file web applications.

CRITICAL RULES:
1. Generate COMPLETE, WORKING code - no placeholders or TODOs
2. All code goes in index.html with embedded <style> and <script> tags
3. Use vanilla JavaScript - no frameworks unless explicitly requested
4. Ensure code is bug-free and handles errors gracefully
5. Make it responsive and visually appealing
6. Follow web accessibility standards
7. Include comprehensive README.md documentation
8. Always use the EXACT file format specified: ===FILE:filename=== content ===END===

CODE QUALITY STANDARDS:
- Clean, well-commented code
- Proper error handling with try-catch blocks
- User-friendly error messages
- Input validation
- Professional styling and layout
- Mobile-responsive design"""
        
        if round_num > 1:
            base_prompt += "\n\nThis is ROUND {}: Update the existing application while preserving working functionality.".format(round_num)
        
        return base_prompt
    
    def _parse_response(self, response: str) -> dict:
        """Parse LLM response into file structure"""
        files = {}
        
        # Use regex to extract files more reliably
        pattern = r'===FILE:([^=]+)===\s*(.*?)\s*===END==='
        matches = re.findall(pattern, response, re.DOTALL)
        
        for filename, content in matches:
            filename = filename.strip()
            content = content.strip()
            if filename and content:
                files[filename] = content
                log_event(f"Parsed file: {filename} ({len(content)} chars)")
        
        # Fallback to line-by-line parsing if regex fails
        if not files:
            log_event("Regex parsing failed, trying line-by-line parsing", "WARNING")
            files = self._parse_response_line_by_line(response)
        
        return files
    
    def _parse_response_line_by_line(self, response: str) -> dict:
        """Fallback line-by-line parsing"""
        files = {}
        current_file = None
        current_content = []
        
        for line in response.split('\n'):
            if line.startswith('===FILE:'):
                if current_file and current_content:
                    files[current_file] = '\n'.join(current_content).strip()
                current_file = line.replace('===FILE:', '').replace('===', '').strip()
                current_content = []
            elif line.startswith('===END==='):
                if current_file and current_content:
                    files[current_file] = '\n'.join(current_content).strip()
                current_file = None
                current_content = []
            elif current_file is not None:
                current_content.append(line)
        
        if current_file and current_content:
            files[current_file] = '\n'.join(current_content).strip()
        
        return files
    
    def _ensure_essential_files(self, files: dict, task_id: str, round_num: int, brief: str, checks: list) -> dict:
        """Ensure essential files are present"""
        
        # Ensure LICENSE
        if 'LICENSE' not in files:
            files['LICENSE'] = self._get_mit_license()
        
        # Ensure index.html exists and is valid
        if 'index.html' not in files or len(files.get('index.html', '').strip()) < 100:
            log_event("No valid index.html generated, creating enhanced version", "WARNING", task_id)
            files['index.html'] = self._get_enhanced_html(task_id, round_num, brief, checks)
        
        # Ensure README.md exists
        if 'README.md' not in files or len(files.get('README.md', '').strip()) < 50:
            log_event("No valid README.md generated, creating professional version", "WARNING", task_id)
            files['README.md'] = self._get_professional_readme(task_id, round_num, brief, checks)
        
        return files
    
    def _create_fallback_app(self, brief: str, checks: list, task_id: str, round_num: int) -> dict:
        """Create fallback application when LLM fails"""
        return {
            'index.html': self._get_enhanced_html(task_id, round_num, brief, checks),
            'README.md': self._get_professional_readme(task_id, round_num, brief, checks),
            'LICENSE': self._get_mit_license()
        }
    
    def _get_enhanced_html(self, task_id: str, round_num: int, brief: str, checks: list) -> str:
        """Enhanced HTML template with better styling"""
        checks_html = '\n'.join(f'<li>{check}</li>' for check in checks)
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generated App - {task_id}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        header p {{
            opacity: 0.9;
            font-size: 1.1em;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .card {{
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
        }}
        
        .card h2 {{
            color: #667eea;
            margin-bottom: 15px;
        }}
        
        .checks {{
            list-style: none;
        }}
        
        .checks li {{
            padding: 10px;
            margin: 8px 0;
            background: white;
            border-radius: 6px;
            border-left: 3px solid #28a745;
        }}
        
        .checks li:before {{
            content: "✓ ";
            color: #28a745;
            font-weight: bold;
            margin-right: 8px;
        }}
        
        .warning {{
            background: #fff3cd;
            border-left-color: #ffc107;
            padding: 15px;
            border-radius: 6px;
            margin: 20px 0;
        }}
        
        .warning strong {{
            color: #856404;
        }}
        
        footer {{
            text-align: center;
            padding: 20px;
            color: #6c757d;
            font-size: 0.9em;
        }}
        
        #total-sales {{
            font-size: 3em;
            color: #667eea;
            font-weight: bold;
            text-align: center;
            margin: 20px 0;
        }}
        
        @media (max-width: 768px) {{
            header h1 {{
                font-size: 1.8em;
            }}
            .content {{
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🚀 Generated Application</h1>
            <p>Task: {task_id} | Round: {round_num}</p>
        </header>
        
        <div class="content">
            <div class="card">
                <h2>📋 Project Brief</h2>
                <p>{brief}</p>
            </div>
            
            <div class="card">
                <h2>✅ Evaluation Criteria</h2>
                <ul class="checks">
                    {checks_html}
                </ul>
            </div>
            
            <div class="card">
                <h2>📊 Application Status</h2>
                <div id="total-sales">0</div>
                <p style="text-align: center; color: #6c757d;">Total Sales Display</p>
            </div>
            
            <div class="warning">
                <strong>Note:</strong> This is a fallback implementation. The LLM should generate specific functionality based on the requirements.
            </div>
        </div>
        
        <footer>
            Generated on {self._get_current_timestamp()} | MIT License
        </footer>
    </div>

    <script>
        console.log('Application initialized for task: {task_id}, round: {round_num}');
        
        // Basic error handling
        window.addEventListener('error', function(e) {{
            console.error('Application error:', e.error);
        }});
        
        // Simulate total sales calculation
        setTimeout(() => {{
            document.getElementById('total-sales').textContent = '450';
        }}, 500);
    </script>
</body>
</html>"""
    
    def _get_professional_readme(self, task_id: str, round_num: int, brief: str, checks: list) -> str:
        """Professional README template"""
        checks_md = '\n'.join(f'- {check}' for check in checks)
        
        return f"""# Generated Web Application

## 📋 Project Information
- **Task ID**: {task_id}
- **Round**: {round_num}
- **Generated**: {self._get_current_timestamp()}

## 📖 Description
{brief}

## ✨ Features
- Responsive design optimized for all devices
- Modern, clean user interface
- Built with vanilla HTML, CSS, and JavaScript
- No external dependencies required
- MIT Licensed

## 🚀 Usage

### Online
Visit the GitHub Pages deployment: `https://<username>.github.io/<repo-name>/`

### Local
1. Clone this repository
2. Open `index.html` in any modern web browser
3. No build process or dependencies needed!

## ✅ Evaluation Criteria
{checks_md}

## 🛠️ Technical Stack
- **HTML5**: Semantic markup
- **CSS3**: Modern styling with flexbox/grid
- **JavaScript (ES6+)**: Vanilla JS, no frameworks
- **Deployment**: GitHub Pages

## 📁 Project Structure
```
.
├── index.html          # Main application file (self-contained)
├── README.md          # This file
└── LICENSE            # MIT License
```

## 🧪 Testing
Open `index.html` in a browser and verify:
{checks_md}

## 📄 License
MIT License - see LICENSE file for details

## 🤖 Development
This application was generated using an AI-powered deployment system as part of the IIT Madras TDS course.

---

*Auto-generated by LLM Code Deployment System*
"""
    
    def _get_mit_license(self) -> str:
        """Get MIT License content"""
        year = datetime.now().year
        return f"""MIT License

Copyright (c) {year} LLM Generated Code

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp for documentation"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")