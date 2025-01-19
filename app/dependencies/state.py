import pickle

import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.db.models import UserData
from app.dependencies.specs.graph import Graph


class StateManager:
    def __init__(self) -> None:
        """Singleton state manager based on UUID user_id."""
        self._user_sessions: dict[str, Graph] = {}

    def get_user_graph(self, user_id: str, db: Session) -> Graph:
        if user_id not in self._user_sessions:
            self._user_sessions[user_id] = self._load_graph_from_db(user_id, db)
        return self._user_sessions[user_id]

    def _load_graph_from_db(self, user_id: str, db: Session) -> Graph:
        try:
            user_data = db.query(UserData).filter_by(user_id=user_id).one()
        except sa.exc.NoResultFound:
            graph = Graph()
        else:
            graph = pickle.loads(user_data.graph_blob)
        return graph

    def _update_user_graph(self, user_id: str, graph: Graph) -> None:
        self._user_sessions[user_id] = graph

    def persist_all_to_db(self, db: Session) -> None:
        for user_id, graph in self._user_sessions.items():
            graph_blob = pickle.dumps(graph)
            existing_data = db.query(UserData).filter_by(user_id=user_id).first()

            if existing_data:
                existing_data.graph_blob = graph_blob
            else:
                new_data = UserData(user_id=user_id, graph_blob=graph_blob)
                db.add(new_data)

        db.commit()


app_state = StateManager()
