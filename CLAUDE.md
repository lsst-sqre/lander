# Claude Configuration for Lander

This is an HTML landing page generator for LSST PDF documentation. It's a Python project with Node.js/Webpack for frontend asset building.

## Commands

Build frontend assets:

```bash
npm run build
```

Run tests:

```bash
tox run -e py
```

Run linting/formatting:

```bash
tox run -e lint
```

Run type checking:

```bash
tox run -e typing
```

Run end-to-end integration tests:

```bash
make test
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
