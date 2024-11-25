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

    access_token = os.getenv("ACCESS_TOKEN")
    id_token = os.getenv("ID_TOKEN")

    from custom_components.vitesy.vitesy import Vitesy
    VitesyObj = Vitesy(params={
        'access_token': access_token,
        'id_token': id_token,
    })

    import asyncio
    asyncio.run(VitesyObj.fetch_data())






