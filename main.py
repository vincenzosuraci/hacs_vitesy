from dotenv import load_dotenv
import os
import importlib

# ----------------------------------------------------------------------------------------------------------------------
#
# MAIN - To be used for tests only!
#
# ----------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":

    # Load the .env file
    load_dotenv()

    from custom_components.vitesy.vitesy import Vitesy
    from custom_components.vitesy.const import CONF_ACCESS_TOKEN, CONF_ID_TOKEN
    VitesyObj = Vitesy(params={
        CONF_ACCESS_TOKEN: os.getenv("ACCESS_TOKEN"),
        CONF_ID_TOKEN: os.getenv("ID_TOKEN"),
    })

    import asyncio
    asyncio.run(VitesyObj.fetch_data())






