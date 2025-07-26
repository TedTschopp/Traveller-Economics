# Traveller Economics Installation Guide

## Quick Setup

### Option 1: Virtual Environment (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/Traveller-Economics.git
cd Traveller-Economics

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt

# Test installation
python3 quick_start.py
```

### Option 2: Basic Installation (Core Features Only)

```bash
# Install minimum dependencies
pip install requests pandas numpy tqdm

# Run basic analysis
python3 run_analysis.py
```

## System Requirements

- **Python**: 3.8 or higher
- **Memory**: 4GB+ recommended (for large datasets)
- **Storage**: 500MB for cached data
- **Network**: Internet connection for API access

## Dependencies Explained

### Required (Core Analysis)
- `requests`: HTTP client for Traveller Map API
- `pandas`: Data manipulation and analysis
- `numpy`: Numerical computations
- `tqdm`: Progress bars for long operations

### Optional (Full Features)
- `matplotlib`: Static charts and graphs
- `seaborn`: Statistical visualizations  
- `plotly`: Interactive dashboards
- `scipy`: Advanced statistical functions

## Troubleshooting

### Virtual Environment Issues

If you get "externally-managed-environment" errors:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Import Errors

Make sure you're in the virtual environment:
```bash
source venv/bin/activate  # Activate if not already active
which python3            # Should show venv/bin/python3
```

### Network/API Issues

If the Traveller Map API is unreachable:
- Check your internet connection
- The API may be temporarily down
- Try again with `--skip-cache` to bypass cached requests

### Memory Issues

For systems with limited RAM:
- Use `--request-delay 2.0` to slow down processing
- Skip visualizations: `python3 run_analysis.py --no-visualizations`
- Process specific sectors only

## Configuration

### Environment Variables

```bash
export TRAVELLER_CACHE_DIR="/custom/cache/path"
export TRAVELLER_API_DELAY="2.0"
export TRAVELLER_LOG_LEVEL="DEBUG"
```

### Configuration File

Copy `config_example.py` to `config.py` and customize:

```python
class Config:
    MILIEU = "M1105"
    CANON_TAG = "Official"
    REQUEST_DELAY = 1.0
    OUTPUT_DIR = "custom_output"
```

## Development Setup

For contributors and developers:

```bash
# Install development dependencies
pip install -e .[dev]

# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Run tests
python -m pytest tests/ -v

# Format code
black .
isort .

# Type checking (if mypy installed)
mypy traveller_economics.py
```

## Platform-Specific Notes

### macOS
- Use `python3` instead of `python`
- May need Xcode command line tools: `xcode-select --install`

### Windows
- Activate venv with: `venv\Scripts\activate`
- Use `py` instead of `python3` if available

### Linux/Ubuntu
- Install Python dev headers: `sudo apt install python3-dev`
- May need build tools: `sudo apt install build-essential`

## Docker Setup (Advanced)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python3", "run_analysis.py", "--all"]
```

```bash
docker build -t traveller-economics .
docker run -v $(pwd)/output:/app/output traveller-economics
```

## Performance Optimization

### For Large-Scale Analysis
- Use SSD storage for cache directory
- Increase `--request-delay` to avoid rate limiting
- Consider `--advanced` flag only for final analysis
- Use `--cache-dir` on fast storage

### For Regular Use
- Keep default settings
- Cache will speed up repeat analyses
- Use `--visualizations` for presentations

## Verification

Test your installation:

```bash
# Activate virtual environment
source venv/bin/activate

# Test basic functionality
python3 -c "from traveller_economics import EconomicCalculator; print('Installation successful!')"

# Run quick test analysis
python3 quick_start.py

# Full test with small dataset
python3 run_analysis.py --milieu M1105 --output-dir test_output
```

## Getting Help

1. Check the main README.md for usage examples
2. Review examples.py for common patterns
3. Run with `--log-level DEBUG` for detailed output
4. Open an issue on GitHub with error details

## Next Steps

After installation:
1. Run `python3 quick_start.py` for first analysis
2. Check `examples.py` for usage patterns
3. Review the generated reports in `output/`
4. Customize analysis with `config.py`
5. Try advanced features with `--advanced` flag
