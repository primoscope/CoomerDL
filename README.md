![Windows Compatibility](https://img.shields.io/badge/Windows-10%2C%2011-blue)
![Downloads](https://img.shields.io/github/downloads/emy69/CoomerDL/total)

# Coomer Downloader App

**Coomer Downloader App** is a Python-based desktop application that simplifies downloading images and videos from various URLs. With an intuitive GUI, you can paste a link and let the app handle the rest.

---

## Support My Work

If you find this tool helpful, please consider supporting my efforts:

[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-FFDD00.svg?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/emy_69)
[![Support on Patreon](https://img.shields.io/badge/Support%20on%20Patreon-FF424D.svg?style=for-the-badge&logo=patreon&logoColor=white)](https://www.patreon.com/emy69)


---

## Features

### Download Images and Videos
- **Multithreaded Downloads**: Boosts download speed by utilizing multiple threads.
- **Progress Feedback**: Real-time progress updates during downloads.
- **Queue Management**: Efficiently handles large download queues.

**Supported File Extensions**:
- **Videos**: `.mp4`, `.mkv`, `.webm`, `.mov`, `.avi`, `.flv`, `.wmv`, `.m4v`
- **Images**: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff`
- **Documents**: `.pdf`, `.doc`, `.docx`, `.xls`, `.xlsx`, `.ppt`, `.pptx`
- **Compressed**: `.zip`, `.rar`, `.7z`, `.tar`, `.gz`

---

## Supported Pages

- [coomer.su](https://coomer.su/)  
- [kemono.su](https://kemono.su/)  
- [erome.com](https://www.erome.com/)  
- [bunkr.albums.io](https://bunkr-albums.io/)  
- [simpcity.su](https://simpcity.su/)  
- [jpg5.su](https://jpg5.su/)  

---

## CLI Tools

If you prefer using command-line interfaces, check out the following projects:

- **[Coomer CLI](https://github.com/Emy69/Coomer-cli)**  
  A CLI tool for downloading media from Coomer and similar sites. It offers customizable options for file naming, download modes, rate limiting, checksum verification, and more.

- **[Simpcity CLI](https://github.com/Emy69/SimpCityCLI)**  
  A CLI tool specifically designed for downloading media from Simpcity. It shares many features with Coomer CLI and is tailored for the Simpcity platform.

---


## Language Support

- [Español](#)  
- [English](#)  
- [日本語 (Japanese)](#)  
- [中文 (Chinese)](#)  
- [Français (French)](#)  
- [Русский (Russian)](#)  

---

## Community

Have questions or just want to say hi? Join the Discord server:

[![Join Discord](https://img.shields.io/badge/Join-Discord-7289DA.svg?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/ku8gSPsesh)

---

## Downloads

- **Latest Version**: Visit the [Releases Page](https://github.com/Emy69/CoomerDL/releases) to download the newest version.

---

## Usage

1. Launch the application.
2. Paste the URL of the image or video you want to download.
3. Click **Download** and wait for the process to finish.

![Usage GIF](https://github.com/Emy69/CoomerDL/blob/main/resources/screenshots/0627.gif)

---

## Clone the Repository

To get a local copy of the project, run the following command:

```sh
git clone https://github.com/Emy69/CoomerDL.git
```
### Install Dependencies
Navigate to the project folder:
```sh
cd CoomerDL
```
Then install the required dependencies:
```sh
pip install -r requirements.txt
```
### Run the Application
Once everything is installed, you can start the application with:
```sh
python main.py
```

---

## Contributing with AI Coding Agents

This repository is optimized for AI coding agents (GitHub Copilot, Claude, GPT-4, etc.). The documentation is structured to help agents understand and implement changes effectively.

### Documentation Structure

| File | Purpose | Use When |
|------|---------|----------|
| [ROADMAP.md](ROADMAP.md) | Overview of all tasks with quick-reference format | Finding what to work on |
| [TASKS.md](TASKS.md) | Detailed task breakdowns with acceptance criteria | Implementing a specific task |
| [SPECIFICATIONS.md](SPECIFICATIONS.md) | Full code specifications for new features | Building new classes/functions |
| [POTENTIAL_ISSUES.md](POTENTIAL_ISSUES.md) | Known blockers and edge cases | Understanding risks |

### How to Prompt AI Agents

#### For Bug Fixes
```
Read ROADMAP.md and implement task BUG-001.

Context: This is a Python desktop app using CustomTkinter.
The bug is in downloader/downloader.py.
Follow the FIND/REPLACE instructions in the task.
```

#### For New Features
```
Read ROADMAP.md and SPECIFICATIONS.md, then implement FEATURE-002 (BaseDownloader class).

Requirements:
1. Create the new file at downloader/base.py
2. Follow the class specification in SPECIFICATIONS.md
3. Include all abstract methods and data classes
4. Ensure backward compatibility
```

#### For Refactoring
```
Read ROADMAP.md and implement REFACTOR-001 (standardize cancel mechanisms).

Files to modify: downloader/bunkr.py, downloader/erome.py, downloader/simpcity.py
Follow the step-by-step instructions in the task.
Test by running: python main.py
```

### Best Practices for Agent Prompts

1. **Always reference the task ID** (e.g., BUG-001, FEATURE-002)
2. **Point to the documentation files** - agents work better with context
3. **Specify the scope** - "only modify X file" prevents over-engineering
4. **Include test instructions** - so the agent can verify the fix
5. **Mention constraints** - "maintain backward compatibility", "minimal changes"

### Example Workflow

```bash
# 1. Ask agent to read the roadmap and pick a task
"Read ROADMAP.md and list all 🔴 CRITICAL tasks"

# 2. Ask agent to implement one task
"Implement BUG-001 from ROADMAP.md. Show me the exact changes."

# 3. Verify the changes
python main.py

# 4. Ask agent to run tests if applicable
"Run any tests related to the downloader module"
```

### Task Priority Guide

| Icon | Priority | Agent Instruction |
|------|----------|-------------------|
| 🔴 | CRITICAL | "Fix this bug first, it causes crashes" |
| 🟠 | HIGH | "Important feature, implement carefully" |
| 🟡 | MEDIUM | "Improvement, make minimal changes" |
| 🟢 | LOW | "Nice-to-have, only if time permits" |

### Quick Agent Commands

Copy-paste these prompts to get started:

**List all tasks:**
```
Read ROADMAP.md and give me a summary of all open tasks by priority.
```

**Fix a specific bug:**
```
Read ROADMAP.md task BUG-001. Show the current code, explain the bug, and provide the fix.
```

**Implement a feature:**
```
Read SPECIFICATIONS.md section "BaseDownloader" and create the file downloader/base.py with the full implementation.
```

**Check for issues:**
```
Read POTENTIAL_ISSUES.md and tell me which issues might affect task FEATURE-001.
```
