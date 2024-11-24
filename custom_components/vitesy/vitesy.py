import asyncio
import aiohttp
import async_timeout
import base64
import time
from datetime import datetime
from .const import CONF_ICCID, CONF_USERNAME, CONF_PASSWORD, SENSOR_VOLUME, SENSOR_TOTAL_VOLUME, SENSOR_EXPIRY_DATE

# ----------------------------------------------------------------------------------------------------------------------
#
# 1nce
#
# ----------------------------------------------------------------------------------------------------------------------

class Once:

    # Massimo numero di prove di login
    MAX_NUM_RETRIES = 1

    # Minimo tempo che deve trascorre tra due interrogazioni successive al router
    MIN_INTERVAL_S = 2

    def __init__(
        self,
        params = {}
    ):
        self._iccid = params.get(CONF_ICCID)
        self._username = params.get(CONF_USERNAME)
        self._password = params.get(CONF_PASSWORD)

        self._session = None
        self._sim_data = None
        self._access_token = None
        self._last_update_timestamp = None

    @property
    def iccid(self):
        return self._iccid

    def debug(self, msg):
        print(msg)

    def info(self, msg):
        print(msg)

    def warning(self, msg):
        print(msg)

    def error(self, msg):
        print(msg)

    async def fetch_data(self):
        return await self._get_sim_data()

    async def _get_sim_data(self, num_retries=MAX_NUM_RETRIES):

        if self._last_update_timestamp is None or time.time() > self._last_update_timestamp + self.MIN_INTERVAL_S:

            self._last_update_timestamp = time.time()

            if await self._get_access_token() is not None:

                sim_data = None

                url = "https://api.1nce.com/management-api/v1/sims/" + self._iccid + "/quota/data"

                headers = {
                    "accept": "application/json",
                    "authorization": "Bearer " + self._access_token
                }

                try:
                    async with async_timeout.timeout(10):  # Timeout di 10 secondi
                        await self._async_init_session()
                        async with self._session.get(url, headers=headers) as response:
                            if response.status == 200:
                                sim_data = await response.json()
                                await self._async_close_session()
                            else:
                                if num_retries > 0:
                                    self._access_token = None
                                    await self._async_close_session()
                                    sim_data = await self._get_sim_data(num_retries - 1)
                                else:
                                    msg = f"Request error {url}: {response.status}"
                                    code = 202
                                    await self._async_close_session()
                                    raise OnceError(msg, code)
                except aiohttp.ClientError as err:
                        msg = f"Connection error {url}: {err}"
                        code = 201
                        await self._async_close_session()
                        raise OnceError(msg, code)
                except asyncio.TimeoutError:
                    msg = f"Connection timeout {url}"
                    code = 200
                    await self._async_close_session()
                    raise OnceError(msg, code)

                if sim_data is not None:

                    # Converti la stringa in un oggetto datetime
                    expiry_date = datetime.strptime(sim_data["expiry_date"], "%Y-%m-%d %H:%M:%S").date()

                    self._sim_data = {
                        SENSOR_VOLUME: sim_data["volume"],
                        SENSOR_TOTAL_VOLUME: sim_data["total_volume"],
                        SENSOR_EXPIRY_DATE: expiry_date
                    }
                    self.debug(self._sim_data)

        return self._sim_data

    async def _get_access_token(self):

        if self._access_token is None:

            url = 'https://api.1nce.com/management-api/oauth/token'

            json = {
                "grant_type": "client_credentials"
            }

            user_pass_str = self._username + ":" + self._password
            base64_user_pass_bytes = base64.b64encode(bytes(user_pass_str, 'utf-8'))
            base64_user_pass_str = base64_user_pass_bytes.decode('utf-8')

            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "authorization": "Basic " + base64_user_pass_str
            }

            try:
                async with async_timeout.timeout(10):  # Timeout di 10 secondi
                    await self._async_init_session()
                    async with self._session.post(url, headers=headers, json=json) as response:
                        if response.status == 200:
                            json_arr = await response.json()
                            self._access_token = json_arr["access_token"]
                        else:
                            msg = f"Request error {url}: {response.status}"
                            await self._async_close_session()
                            code = 102
                            raise OnceError(msg, code)
            except aiohttp.ClientError as err:
                msg = f"Connection error {url}: {err}"
                code = 101
                await self._async_close_session()
                raise OnceError(msg, code)
            except asyncio.TimeoutError:
                msg = f"Connection timeout {url}"
                code = 100
                await self._async_close_session()
                raise OnceError(msg, code)

        return self._access_token

    async def test_connection(self):
        data = await self.fetch_data()
        return data is not None

    # ------------------------------------------------------------------------------------------------------------------
    # Session related methods
    # ------------------------------------------------------------------------------------------------------------------

    async def _async_init_session(self):
        """ Init session """
        if self._session is None:
            self._session = aiohttp.ClientSession()

    async def _async_close_session(self):
        """ Close session """
        if self._session:
            await self._session.close()
            self._session = None


class OnceAuthError(Exception):
    """Eccezione personalizzata che accetta un messaggio e un codice di errore."""

    def __init__(self, message, code):
        # Chiama il costruttore della classe base (Exception) con il messaggio di errore
        super().__init__(message)
        self.code = code

    def __str__(self):
        # Ritorna una rappresentazione stringa dell'errore, includendo il codice
        return f"[1nce Authentication Error {self.code}]: {self.args[0]}"


class OnceError(Exception):
    """Eccezione personalizzata che accetta un messaggio e un codice di errore."""

    def __init__(self, message, code):
        # Chiama il costruttore della classe base (Exception) con il messaggio di errore
        super().__init__(message)
        self.code = code

    def __str__(self):
        # Ritorna una rappresentazione stringa dell'errore, includendo il codice
        return f"[1nce Error {self.code}]: {self.args[0]}"