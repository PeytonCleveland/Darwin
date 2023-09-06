# Darwin
Implementation of prompt evolution based on Evol-Instruct: https://arxiv.org/pdf/2304.12244.pdf

## Usage
To run, first create a .env file in the same directory as the main.py script. Add `OPENAI_API_KEY=sk-{YOUR_OPENAI_API_KEY}` to this file.

The script requires an input CSV in with headers `Refusal, System, User, Assistant`. To validate your CSV run:
```bash
python3 main.py ./input.csv --validate
```

Once you have a valid CSV, run the script using:
```bash
python3 main.py ./input.csv
```

To change the number of epochs to evolve for, defaults to 4:
```bash
python3 main.py ./input.csv --epochs 5
```
