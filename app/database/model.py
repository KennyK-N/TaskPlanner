from sqlalchemy import Integer, TIMESTAMP, Numeric, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from . import db
from .config import TABLE_NAME


class Tasks(db.Model):
    """SQLAlchemy model representing a saved schedule in the tasks table."""

    __tablename__ = TABLE_NAME
    id = db.Column(Integer, primary_key=True)
    modified_at = db.Column(TIMESTAMP(timezone=True), default=func.now())
    data = db.Column(JSONB)
    oauth_id = db.Column(Numeric)
    name = db.Column(Text)

    def as_dict(self):
        """
        Serializes the model instance into a plain dict keyed by column name.
        Returns:
            dict: All column names and their current values for this row.
        """
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
