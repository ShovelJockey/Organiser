from sqlalchemy import ForeignKey, create_engine, Column, Integer, String, Date
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
import calendar
from datetime import datetime, timedelta


engine = create_engine("sqlite:///organiser.db", echo=False)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()


class User(Base):
    __tablename__ = "Users"

    id = Column(Integer, primary_key=True)
    user_name = Column(String)
    tasks = relationship("Task", backref="Users", cascade="all, delete, delete-orphan", lazy='dynamic', passive_deletes=True)

    def __repr__(self):
        return self.user_name


class Task(Base):
    __tablename__ = "Tasks"

    id = Column(Integer, primary_key=True)
    task_type = Column(String)
    description = Column(String)
    deadline = Column(Date, nullable=True)
    user_id = Column(Integer, ForeignKey("Users.id"), nullable=False)

    def __repr__(self):
        if self.deadline:
            deadline = self.deadline.strftime("%d/%m/%Y")
            return f"Task type: {self.task_type}, Description of task: {self.description}, needs to be completed by: {deadline}  which is a {calendar.day_name[self.deadline.weekday()]}."
        else:
            return f"Task type: {self.task_type}, Description of task: {self.description}, this task has no deadline."


def date_clean(date):
    for fmt in ["%d-%m-%Y", "%d.%m.%Y", "%d/%m/%Y", "%d %m %Y"]:
        try:
            cleaned_date = datetime.strptime(date, fmt).date()
        except ValueError:
            pass
        else:
            return cleaned_date
    return None

Base.metadata.create_all(engine)
