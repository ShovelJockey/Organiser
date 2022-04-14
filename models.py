from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.schema import MetaData
import calendar


class DBmaker():
    

    def __init__(self, DB_name):
        self.DB_name = DB_name
        self.table_names = []
        global engine
        engine = create_engine(self.DB_name, echo=False)
        Session = sessionmaker(bind=engine)
        global session
        session = Session()


    def create_models(self, table_name):
        Base = declarative_base()
        class Task(Base):
            __tablename__ = table_name

            id = Column(Integer, primary_key=True)
            task_type = Column(String)
            description = Column(String)
            deadline = Column(Date, nullable=True)


            def __repr__(self):
                if self.deadline:
                    deadline = self.deadline.strftime("%d/%m/%Y")
                    return f'Task type: {self.task_type}, Description of task: {self.description}, needs to be completed by: {deadline}  which is a {calendar.day_name[self.deadline.weekday()]}'
                else:
                    return f'Task type: {self.task_type}, Description of task: {self.description}, this task has no deadline.'
        Base.metadata.create_all(engine)
        return Task

    
    def get_model(self, user_name):
        DynamicBase = declarative_base(class_registry=dict())
        class Task(DynamicBase):
            __tablename__ = user_name

            id = Column(Integer, primary_key=True)
            task_type = Column(String)
            description = Column(String)
            deadline = Column(Date, nullable=True)


            def __repr__(self):
                if self.deadline:
                    deadline = self.deadline.strftime("%d/%m/%Y")
                    return f'Task type: {self.task_type}, Description of task: {self.description}, needs to be completed by: {deadline}  which is a {calendar.day_name[self.deadline.weekday()]}'
                else:
                    return f'Task type: {self.task_type}, Description of task: {self.description}, this task has no deadline.'
        return Task


    def get_table_names(self):
        meta = MetaData()
        meta.reflect(bind=engine)
        return meta.tables.keys()
    