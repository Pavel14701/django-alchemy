from config import Config
from dishka import make_container
from ioc import CatalogProvider

config = Config.load()
container = make_container(
    CatalogProvider(),
    context={Config: config}
)
