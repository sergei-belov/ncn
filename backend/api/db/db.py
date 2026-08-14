from api.db.agents import AgentsDb
from api.db.board_preferences import BoardPreferencesDb
from api.db.epics import EpicAssigneesDb, EpicsDb
from api.db.project_users import ProjectUsersDb
from api.db.projects import ProjectsDb
from api.db.states import ProjectStatesDb
from api.db.users import UsersDb
from api.db.work_items import WorkItemAssigneesDb, WorkItemsDb


class Database:
    """Expose initialized repositories through a shared database hub."""

    agents = AgentsDb()
    projects = ProjectsDb()
    users = UsersDb()
    project_users = ProjectUsersDb()
    states = ProjectStatesDb()
    work_items = WorkItemsDb()
    work_item_assignees = WorkItemAssigneesDb()
    epics = EpicsDb()
    epic_assignees = EpicAssigneesDb()
    board_preferences = BoardPreferencesDb()
