# NOVA AI 🤖

**Your Personal AI-Powered Desktop Assistant**

NOVA AI is a Python-based desktop assistant designed to make everyday tasks easier through artificial intelligence, voice interaction, automation, and intelligent assistance.

Built with a modern desktop interface, NOVA combines AI-powered conversations with practical desktop utilities to create a smarter and more interactive user experience.

## ✨ Features

- **AI-Powered Conversations:** Interact with an AI assistant using the Groq API.
- **Voice Interaction:** Speak with NOVA using speech recognition and text-to-speech.
- **Smart Memory:** Maintain persistent information across conversations.
- **Task Automation:** Perform supported desktop tasks through automation modules.
- **Browser Control:** Automate supported browser operations.
- **File Management:** Manage files using integrated file-management utilities.
- **Reminders:** Organize reminders and stay on top of tasks.
- **Modern Desktop UI:** Interactive interface built using CustomTkinter.
- **Configurable Settings:** Customize assistant behavior and preferences.

## 🛠️ Tech Stack

| Technology         | Purpose                   |
| ------------------ | ------------------------- |
| Python             | Core development          |
| CustomTkinter      | Desktop GUI               |
| Groq API           | AI-powered responses      |
| pyttsx3            | Text-to-speech            |
| Speech Recognition | Voice input               |
| SQLite             | Local data storage        |
| Selenium           | Browser automation        |
| Python-dotenv      | Environment configuration |

## 📁 Project Structure

```text
NOVA_AI/
│
├── automation/       # Automation modules
├── brain/            # Assistant intelligence
├── config/           # Configuration
├── core/             # Core assistant logic
├── database/         # Database management
├── services/         # Supporting services
├── tools/            # Integrated tools
├── ui/               # Desktop interface
├── voice/            # Voice input and output
├── assets/           # UI assets
├── data/             # Application data
├── logs/             # Application logs
├── tests/            # Testing modules
│
├── main.py           # Application entry point
├── requirements.txt  # Dependencies
├── .env.example      # Environment template
├── .gitignore
└── README.md
```

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/jaiswalmegh/NOVA_AI
cd NOVA_AI
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

### 3. Activate the Environment

**Windows PowerShell:**

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file using `.env.example` as the template.

Add your required API credentials and configuration values.

**Important:** Never upload your actual `.env` file or API keys to GitHub.

### 6. Run NOVA AI

```bash
python main.py
```

## 🔐 Security

- Keep API credentials private.
- Store sensitive configuration in environment variables.
- Do not commit personal credentials or private data.
- Review automation permissions before running operations.

## 🚀 Future Enhancements

- More natural AI voice integration.
- Improved contextual memory.
- Advanced desktop automation.
- Expanded tool integrations.
- Enhanced conversational intelligence.
- Further UI and performance improvements.

## 👨‍💻 Developer

**Megh Jaiswal**

Developed as a personal AI assistant project exploring artificial intelligence, Python application development, voice interaction, and desktop automation.

---

⭐ If you find NOVA AI interesting, consider giving the repository a star!

**NOVA AI | Think Smarter. Work Faster.**
