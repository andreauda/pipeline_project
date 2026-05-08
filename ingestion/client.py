import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time


class APIClient:

    def __init__(self, config: dict):

        #️ config - valori di base per base_url, headers e timeout
        self.base_url = config['api']['base_url']
        self.headers = config['api']['headers']
        self.timeout = config['api']['timeout']

        # retry - valori di default per retry, backoff e status_forcelist
        self.max_attempts = config['retry']['max_attempts']
        self.backoff_factor = config['retry']['backoff_factor']
        self.status_forcelist = config['retry']['status_forcelist']

        # rate limit - valori di default per il sleep in caso di 429
        self.default_sleep = config['rate_limit']['default_sleep']
        self.max_sleep = config['rate_limit']['max_sleep']

        # session
        self.session = requests.Session()

        # retry, qui stiamo gestendo l'errore 500 
        retry_strategy = Retry(
            total=self.max_attempts,
            backoff_factor=self.backoff_factor,
            status_forcelist=self.status_forcelist,
            allowed_methods=["GET"],
            raise_on_status=False
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)

        # mount per applicare la strategia di retry sia su http che https
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def get(self, endpoint: str, params: dict = None, attempt: int = 1):

        url = f"{self.base_url}{endpoint}"

        # ✅ protezione da loop infinito
        if attempt > self.max_attempts:
            raise Exception(f"Max retry attempts reached for endpoint: {endpoint}")

        # ✅ gestione normale della richiesta
        try:
            response = self.session.get(
                url,
                headers=self.headers,
                params=params,
                timeout=self.timeout
            )

            # ✅ gestione rate limit (429)
            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")

                try:
                    retry_after = int(retry_after) #valore estratto dall'header, se presente, e convertito in intero
                except (TypeError, ValueError):
                    retry_after = self.default_sleep #se non c'è o non è un numero valido, usiamo un valore di default

                sleep_time = min(retry_after, self.max_sleep)

                time.sleep(sleep_time)

                return self.get(endpoint, params, attempt + 1)

            # ✅ errori HTTP normali
            response.raise_for_status()

            # ✅ ritorna direttamente JSON (più utile)
            return response.json()

        except requests.exceptions.RequestException as e:
            raise