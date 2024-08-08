# README.md

# GitHub Crawler

GitHub Crawler is a Python-based application that allows you to crawl GitHub repositories based on specific keywords. It uses the aiohttp library for making HTTP requests and unittest for running tests.

## Setting Up the Environment

1. Ensure you have Python installed on your system. You can download it from [here](https://www.python.org/downloads/).

2. Clone the repository to your local machine using the following command:
   ```
   git clone https://github.com/ArsenPidhoretskyi/github-crawler.git
   ```

3. Navigate to the cloned repository:
   ```
   cd github-crawler
   ```

4. Install the required Python packages using pip:
   ```
   pip install -r requirements.txt
   ```

## Running the Crawler

To run the GitHub Crawler, use the following command:

```python
python app/handler.py
```

This will start the crawler with the default input data specified in `app/handler.py`. You can modify this data to suit your needs.

## Running the Tests

To run the tests, run the following command:

```python
python -m unittest discover
```

This will discover and run all the test cases in the `tests.py` file.

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

