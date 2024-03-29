import calendar
import datetime
from sqlalchemy import ForeignKey, create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base, relationship


engine = create_engine("postgresql+psycopg2://jamie:pass@localhost:5432/organiser", echo=False)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()


class User(Base):
    __tablename__ = "Users"

    id = Column(Integer, primary_key=True)
    user_name = Column(String)
    user_email = Column(String)
    tasks = relationship("Task", backref="Users", cascade="all, delete, delete-orphan", lazy="dynamic", passive_deletes=True)
    settings = relationship("UserSettings", backref="Users", cascade="all, delete, delete-orphan", uselist=False, passive_deletes=True)


    def __str__(self) -> str:
        return f"User name: {self.user_name}, User email: {self.user_email}"


class Task(Base):
    __tablename__ = "Tasks"

    id = Column(Integer, primary_key=True)
    task_type = Column(String)
    description = Column(String)
    deadline = Column(DateTime, nullable=True)
    user_id = Column(Integer, ForeignKey("Users.id"), nullable=False)
    reminder_sent = Column(Integer, default=0)


    def __str__(self) -> str:
        if self.deadline:
            if self.deadline.hour != 0 and self.deadline.minute != 0:
                deadline = self.deadline.strftime("%d/%m/%Y :: %H:%M")
            else:
                deadline = self.deadline.strftime("%d/%m/%Y")
            return f"Task type: {self.task_type}, Description of task: {self.description}, needs to be completed by: {deadline}  which is a {calendar.day_name[self.deadline.weekday()]}."
        else:
            return f"Task type: {self.task_type}, Description of task: {self.description}, this task has no deadline."


class UserSettings(Base):
    __tablename__ = "Settings"

    id = Column(Integer, ForeignKey("Users.id"), primary_key=True)
    reminder_offset = Column(Integer, default=2)
    reminder_message = Column(String, default='')
    additional_reminder_offset = Column(Integer, default=0)
    additional_reminder_message = Column(String, default='')


Base.metadata.create_all(engine)