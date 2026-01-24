# Contributing to DIARIUM

Thank you for your interest in contributing to DIARIUM!

## Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/DIARIUM-flet-8.0.git
   cd DIARIUM-flet-8.0
   ```
3. Run the setup script:
   ```bash
   python setup.py
   ```

## Project Structure Guidelines

### Adding New Features

#### 1. Views
- Create view files in `src/views/`
- Each view should represent a screen or major UI component
- Views should follow the pattern in `home_view.py`

#### 2. Components
- Create reusable components in `src/components/`
- Components should be self-contained and reusable
- Use functional components (return ft.Control) as shown in `header.py`

#### 3. Models
- Create data models in `src/models/`
- Use `@dataclass` for simple data structures
- Include validation and default values

#### 4. Utilities
- Add helper functions in `src/utils/`
- Keep utilities focused and single-purpose
- Add appropriate documentation

## Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings to all functions and classes
- Keep functions small and focused

## Testing

Before submitting a pull request:

1. Test your changes locally:
   ```bash
   python main.py
   ```

2. Ensure all imports work:
   ```bash
   python -m py_compile [your_files]
   ```

3. Run the examples:
   ```bash
   python examples.py
   ```

## Pull Request Process

1. Create a new branch for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit:
   ```bash
   git add .
   git commit -m "Add your descriptive commit message"
   ```

3. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

4. Open a Pull Request with a clear description of your changes

## Questions?

Feel free to open an issue for any questions or suggestions!
