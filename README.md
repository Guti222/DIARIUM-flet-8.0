# DIARIUM - Personal Diary Application

A modern, elegant personal diary application built with [Flet](https://flet.dev/) 0.80+ framework.

## 📖 About

DIARIUM is a personal diary application that allows you to record your daily thoughts, memories, and experiences in a beautiful and intuitive interface.

## 🚀 Features

- **Easy to Use**: Clean and intuitive user interface
- **Diary Entries**: Create, read, update, and delete diary entries
- **Organization**: Tag and categorize your entries
- **Cross-Platform**: Works on Windows, macOS, Linux, and web

## 📁 Project Structure

```
DIARIUM-flet-8.0/
│
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── .gitignore             # Git ignore rules
│
├── src/                   # Source code
│   ├── __init__.py
│   ├── app.py             # Main application class
│   │
│   ├── components/        # Reusable UI components
│   │   ├── __init__.py
│   │   └── header.py
│   │
│   ├── views/             # Application views/screens
│   │   ├── __init__.py
│   │   └── home_view.py
│   │
│   ├── models/            # Data models
│   │   ├── __init__.py
│   │   └── diary_entry.py
│   │
│   └── utils/             # Utility functions
│       ├── __init__.py
│       ├── config.py
│       └── helpers.py
│
└── assets/                # Static assets
    ├── images/
    └── icons/
```

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Guti222/DIARIUM-flet-8.0.git
   cd DIARIUM-flet-8.0
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 🎯 Usage

Run the application:

```bash
python main.py
```

## 🧩 Development

### Adding a New View

1. Create a new file in `src/views/` (e.g., `new_view.py`)
2. Implement your view class
3. Import and use it in `src/app.py`

### Adding a New Component

1. Create a new file in `src/components/` (e.g., `new_component.py`)
2. Implement your component as a `ft.UserControl`
3. Import and use it in your views

### Adding a New Model

1. Create a new file in `src/models/` (e.g., `new_model.py`)
2. Define your data model using `@dataclass` or classes
3. Import and use it in your application logic

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is open source and available under the MIT License.

## 🔗 Links

- [Flet Documentation](https://flet.dev/docs/)
- [Python Documentation](https://docs.python.org/)

## 👤 Author

Guti222

---

Built with ❤️ using [Flet](https://flet.dev/)