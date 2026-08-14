from api.managers.agents import AgentsManager
from api.managers.auth import AuthManager
from api.managers.authorization import AuthorizationManager
from api.managers.board import BoardManager
from api.managers.epics import EpicsManager
from api.managers.projects import ProjectsManager
from api.managers.states import StatesManager
from api.managers.work_items import WorkItemsManager


class Managers:
    """Expose initialized domain managers through a shared application hub."""

    agents = AgentsManager()
    auth = AuthManager()
    authorization = AuthorizationManager()
    projects = ProjectsManager()
    states = StatesManager()
    work_items = WorkItemsManager()
    board = BoardManager()
    epics = EpicsManager()
