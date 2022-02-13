from dataclasses import dataclass
import httpx


@dataclass
class SkyblockApi:
    key: str

    def Bazaar(self) -> dict:
        import requests
        assert self.key != None
        endpoint = requests.get('https://api.hypixel.net/skyblock/bazaar', params={'key':self.key})
        return endpoint.json()

    def Key(self) -> dict:
        assert self.key != None
        return httpx.get('https://api.hypixel.net/key', params={'key':self.key}).json()
