# rotating file server

A simple webserver that rotates through a configured list of files in either
linear or random order.

## Usage

### 1: Configure

Configure the files to be served (in `config.yaml`);
```yaml
files:
  - rpki-20230814T000525Z.json
  - rpki-20230814T010529Z.json
  - rpki-20230814T020527Z.json
  - rpki-20230814T030523Z.json
  - rpki-20230814T040532Z.json
```

### 2: Run

```bash
poetry run python -m rotate_files
# or on another port
poetry run python -m rotate_files --port 8081
# and randomise the files
poetry run python -m rotate_files --random
```
