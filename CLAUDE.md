# Claude Configuration for Lander

This is an HTML landing page generator for LSST PDF documentation. It's a Python project with Node.js/Webpack for frontend asset building.

## Commands

Run tests:
```bash
make test
```

Run Python unit tests only:
```bash
make pytest
```

Build frontend assets:
```bash
npm run build
```

## Project Structure

- `src/lander/` - Python source code
- `tests/` - Python unit tests
- `integration-tests/` - End-to-end integration tests
- `js/`, `scss/` - Frontend source files
- `gulpfile.js`, `webpack.config.js` - Build configuration

## Development Notes

- Python package managed with setuptools
- Frontend assets built with Webpack and Gulp
- Uses pytest for unit testing
- Integration tests in bash scripts
- Code formatting with black (79 char line length)
- Import sorting with isort