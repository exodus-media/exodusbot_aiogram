from .intentions import Intentions
from .rings_help import RingsHelp
from .event import Event
from .requisites import Requisites
from .status import Statuses
from .user import User
from .history_intention import HistoryIntention


class DBService:

    def __init__(self):
        self.users = User()
        self.statuses = Statuses()
        self.intentions = Intentions()
        self.events = Event()
        self.rings_help = RingsHelp()
        self.requisites = Requisites()
        self.history_intention = HistoryIntention()
