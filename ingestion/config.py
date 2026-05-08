import yaml
from pathlib import Path


def load_config(path: str | None = None) -> dict:
    # Se non viene passato path → usa config.yaml in questa cartella (config/)
    if path is None:
        path = Path(__file__).parent.parent / "config" / "config.yaml"
    else:
        path = Path(path)
    # Risolve il percorso assoluto, gestisce anche i percorsi relativi e verifica che il file esista
    path = path.resolve(strict=True) 
    # Se il file non esiste, solleva un'eccezione chiara
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found at path: {path}")
    # Se il file esiste, prova a caricarlo come YAML, gestendo eventuali errori di parsing
    try:
        with open(path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    # Se il file non è un YAML valido, solleva un'eccezione chiara
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML format in {path}: {e}") from e
    # Se il file è vuoto o non è un dict, solleva un'eccezione chiara
    if config is None:
        raise ValueError(f"Configuration file at {path} is empty")
    # Se il config non è un dict, solleva un'eccezione chiara
    if not isinstance(config, dict):
        raise ValueError("Configuration must be a dictionary")
    # Aggiungiamo il percorso del config al dict, per poterlo loggare in seguito
    config["_config_path"] = str(path) 
    return config