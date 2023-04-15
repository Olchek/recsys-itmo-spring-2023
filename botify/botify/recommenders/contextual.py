from .random import Random
from .recommender import Recommender
import random

from .toppop import TopPop


class Contextual(Recommender):
    """
    Recommend tracks closest to the previous one.
    Fall back to the random recommender if no
    recommendations found for the track.
    """

    def __init__(self, tracks_redis, catalog, session_history = {}, topPop=None):
        self.tracks_redis = tracks_redis
        if topPop is not None:
            self.fallback = TopPop(tracks_redis, topPop[:100])
        else:
            self.fallback = Random(tracks_redis)
        self.catalog = catalog
        self.session_history = session_history

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        session_history = self.session_history.get(user, {})
        if session_history:
            prev_track = session_history[0]
            prev_track_time = session_history[1]
        previous_track = self.tracks_redis.get(prev_track)
        if previous_track is None:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)

        previous_track = self.catalog.from_bytes(previous_track)
        recommendations = previous_track.recommendations
        if not recommendations:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)

        shuffled = list(recommendations)
        random.shuffle(shuffled)
        return shuffled[0]

