# Weekend Training Report

**Started:** 2025-08-22 17:56:28.175959
**Completed:** 2025-08-23 00:11:56.126768
**Duration:** 6:15:27.950817

## Results

- **Best Model:** fit-weekend-3
- **Best Score:** 94.0%
- **Total Iterations:** 18

## Model Performance Over Time

| Iteration | Model | Score |
|-----------|-------|-------|
| 1 | fit-weekend-1 | 76.0% |
| 10 | fit-weekend-10 | 52.0% |
| 11 | fit-weekend-11 | 42.0% |
| 12 | fit-weekend-12 | 60.0% |
| 13 | fit-weekend-13 | 50.0% |
| 14 | fit-weekend-14 | 56.0% |
| 15 | fit-weekend-15 | 58.0% |
| 16 | fit-weekend-16 | 64.0% |
| 17 | fit-weekend-17 | 54.0% |
| 18 | fit-weekend-18 | 62.0% |
| 19 | fit-weekend-19 | 56.0% |
| 2 | fit-weekend-2 | 88.0% |
| 20 | fit-weekend-20 | 46.0% |
| 3 | fit-weekend-3 | 94.0% |
| 4 | fit-weekend-4 | 82.0% |
| 5 | fit-weekend-5 | 80.0% |
| 6 | fit-weekend-6 | 62.0% |
| 7 | fit-weekend-7 | 52.0% |
| 8 | fit-weekend-8 | 48.0% |
| 9 | fit-weekend-9 | 60.0% |

## Deployment

```bash
# Update the model in use
sed -i 's/fit-intelligence-[^"]*"/fit-intelligence-weekend"/g' ollama_query_parser.py

# Restart server
pkill -f unified_server.py
venv/bin/python unified_server.py &
```
