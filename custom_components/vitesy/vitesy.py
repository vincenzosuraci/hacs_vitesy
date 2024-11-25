import asyncio
import aiohttp
import async_timeout
import base64
import time
from datetime import datetime
from .const import CONF_ACCESS_TOKEN, CONF_ID_TOKEN, SENSOR_XXX

# ----------------------------------------------------------------------------------------------------------------------
#
# 1nce
#
# ----------------------------------------------------------------------------------------------------------------------

class Vitesy:

    # Minimo tempo che deve trascorre tra due interrogazioni successive
    MIN_INTERVAL_S = 1

    def __init__(
        self,
        params = {}
    ):
        self._access_token = params.get(CONF_ACCESS_TOKEN)
        self._id_token = params.get(CONF_ID_TOKEN)

        self._data = None
        self._session = None
        self._last_update_timestamp = None


    @property
    def access_token(self):
        return self._access_token

    @property
    def id_token(self):
        return self._id_token

    def debug(self, msg):
        print(msg)

    def info(self, msg):
        print(msg)

    def warning(self, msg):
        print(msg)

    def error(self, msg):
        print(msg)

    async def fetch_data(self):
        return await self._get_data()

    async def _get_data(self):

        if self._last_update_timestamp is None or time.time() > self._last_update_timestamp + self.MIN_INTERVAL_S:

            self._last_update_timestamp = time.time()

            self._data = await self._create_api_key()

            """
            sim_data = None

            url = "https://v1.api.vitesyhub.com/" + self._iccid + "/quota/data"

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
                                raise VitesyError(msg, code)
            except aiohttp.ClientError as err:
                    msg = f"Connection error {url}: {err}"
                    code = 201
                    await self._async_close_session()
                    raise VitesyError(msg, code)
            except asyncio.TimeoutError:
                msg = f"Connection timeout {url}"
                code = 200
                await self._async_close_session()
                raise VitesyError(msg, code)

            if sim_data is not None:

                # Converti la stringa in un oggetto datetime
                expiry_date = datetime.strptime(sim_data["expiry_date"], "%Y-%m-%d %H:%M:%S").date()

                self._sim_data = {
                    SENSOR_VOLUME: sim_data["volume"],
                    SENSOR_TOTAL_VOLUME: sim_data["total_volume"],
                    SENSOR_EXPIRY_DATE: expiry_date
                }
                self.debug(self._sim_data)
            """

        return self._data

    async def _create_api_key(self):

        url = "https://v1.api.vitesyhub.com/users/me/api-key"

        headers = {
            "accept": "application/json",
            "authorization": "Bearer " + self._access_token
        }

        try:
            async with async_timeout.timeout(10):  # Timeout di 10 secondi
                await self._async_init_session()
                async with self._session.post(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.info(data)
                        await self._async_close_session()
                    else:
                        msg = f"Request error {url}: {response.status}"
                        code = 102
                        await self._async_close_session()
                        raise VitesyError(msg, code)
        except aiohttp.ClientError as err:
            msg = f"Connection error {url}: {err}"
            code = 101
            await self._async_close_session()
            raise VitesyError(msg, code)
        except asyncio.TimeoutError:
            msg = f"Connection timeout {url}"
            code = 100
            await self._async_close_session()
            raise VitesyError(msg, code)

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


class VitesyAuthError(Exception):
    """Eccezione personalizzata che accetta un messaggio e un codice di errore."""

    def __init__(self, message, code):
        # Chiama il costruttore della classe base (Exception) con il messaggio di errore
        super().__init__(message)
        self.code = code

    def __str__(self):
        # Ritorna una rappresentazione stringa dell'errore, includendo il codice
        return f"[1nce Authentication Error {self.code}]: {self.args[0]}"


class VitesyError(Exception):
    """Eccezione personalizzata che accetta un messaggio e un codice di errore."""

    def __init__(self, message, code):
        # Chiama il costruttore della classe base (Exception) con il messaggio di errore
        super().__init__(message)
        self.code = code

    def __str__(self):
        # Ritorna una rappresentazione stringa dell'errore, includendo il codice
        return f"[1nce Error {self.code}]: {self.args[0]}"