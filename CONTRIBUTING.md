# Contributing to Swarm Homepage

Thank you for considering contributing to Swarm Homepage! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- A clear, descriptive title
- Steps to reproduce the issue
- Expected behavior vs actual behavior
- Your environment (OS, Docker version, etc.)
- Relevant logs or screenshots

### Suggesting Features

Feature requests are welcome! Please open an issue with:
- A clear description of the feature
- Why it would be useful
- Any implementation ideas you have

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests: `python test_app.py`
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to your branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/remotephone/swarm-homepage.git
cd swarm-homepage
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Run tests:
```bash
python test_app.py
```

## Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add comments for complex logic
- Keep functions focused and small

## Testing

- Add tests for new features
- Ensure all tests pass before submitting PR
- Test with Docker to ensure containerization works

## Documentation

- Update README.md if adding new features
- Add docstrings to new functions and classes
- Update QUICKSTART.md if changing setup process

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
