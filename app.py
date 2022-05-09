import models
from datetime import datetime, timedelta
from tkinter import Tk, ttk, Toplevel, StringVar, messagebox
from tkcalendar import Calendar


class OrganiserApp():


    def __init__(self):
        self.root = Tk()
        self.root.title("Organiser")
        self.DBmng = models.DBmaker('sqlite:///organiser.db')
        self.current_table = None
        self.current_profile_name = StringVar()
    

    def app_running(self):
        self.win_geometry(300, 400, self.root)
        frm = ttk.Frame(self.root, padding=10)
        frm.grid()
        self.table_select_window()
        ttk.Label(frm, text="Welcome to my organiser app").grid(column=0, row=0, padx=5, pady=5)
        ttk.Label(frm, text="Current profile:").grid(column=0, row=1, padx=5, pady=5)
        ttk.Label(frm, textvariable=self.current_profile_name).grid(column=1, row=1, padx=5, pady=5)
        ttk.Button(frm, text="Show tasks", command=lambda:[self.root.withdraw(), self.show_task()]).grid(column=0, row=2, padx=5, pady=5)
        ttk.Button(frm, text="Show all urgent tasks", command=lambda:[self.root.withdraw(), self.urgent_task()]).grid(column=0, row=3, padx=5, pady=5)
        ttk.Button(frm, text="Calendar", command=lambda:[self.root.withdraw(), self.calendar_view()]).grid(column=0, row=4, padx=5, pady=5)
        ttk.Button(frm, text="Add a new task", command=lambda:[self.root.withdraw(), self.add_task_window()]).grid(column=0, row=5, padx=5, pady=5)
        ttk.Button(frm, text="Delete or Edit a task", command=lambda:[self.root.withdraw(), self.edit_delete_task_window()]).grid(column=0, row=6, padx=5, pady=5)
        ttk.Button(frm, text="Select or create new profile", command=lambda:[self.deselect_current_table(), self.table_select_window()]).grid(column=0, row=7, padx=5, pady=5)
        ttk.Button(frm, text="Delete existing profile", command=lambda:[self.root.withdraw(), self.delete_table_window()]).grid(column=0, row=8, padx=5, pady=5)
        ttk.Button(frm, text="Quit", command=self.root.destroy).grid(column=0, row=9, padx=5, pady=5)
        self.root.mainloop()


    def calendar_view(self):
        def pass_date(i):
            self.cal_tasks(cal.get_date(), tasks)
        global cal_window
        cal_window = Toplevel(self.root)
        self.win_geometry(300, 400, cal_window)
        date = StringVar(cal_window, Calendar.date.today().strftime("%d/%m/%y"))
        tasks = StringVar(cal_window)
        cal = Calendar(cal_window, selectmode='day', textvariable=date)
        cal.pack()
        ttk.Label(cal_window, textvariable=date).pack(padx=10, pady=10)
        ttk.Label(cal_window, text="Tasks for this date:").pack(padx=5, pady=5)
        ttk.Label(cal_window, textvariable=tasks).pack(padx=5, pady=5)
        ttk.Button(cal_window, text="Add task to this date", command=lambda:[cal_window.withdraw(), self.add_task_window(cal.get_date())]).pack(padx=5, pady=5)
        ttk.Button(cal_window, text="Return", command=lambda:[cal_window.destroy(), self.root.deiconify()]).pack(padx=10, pady=10)
        cal.bind("<<CalendarSelected>>", pass_date)
        cal_window.protocol("WM_DELETE_WINDOW", lambda:[cal_window.destroy(), self.root.destroy()])


    def cal_tasks(self, date, tasks_str):
        date = datetime.strptime(date, "%d/%m/%Y").date()
        if models.session.query(self.current_table).filter_by(deadline=date).count() > 0:
            tasks = ""
            for model in models.session.query(self.current_table).filter_by(deadline=date):
                tasks = tasks + "-" + model.task_type + ", " + model.description + "\n"
        else:
            tasks = "No tasks"
        tasks_str.set(tasks)


    def table_select_window(self):
        if self.current_table == None:
            self.root.withdraw()
            task_window = Toplevel(self.root)
            self.win_geometry(300, 400, task_window)
            frm = ttk.Frame(task_window, padding=10)
            frm.grid()
            if self.DBmng.get_table_names():
                ttk.Label(frm, text="Select a user profile or create a new one").grid(column=0, row=0, padx=5, pady=5)
                ttk.Button(frm, text="Select existing profile", command=lambda:[task_window.withdraw, self.select_table(task_window)]).grid(column=0, row=1, padx=5, pady=5)
                ttk.Button(frm, text="Create new profile", command=lambda:[task_window.withdraw(), self.create_table(task_window)]).grid(column=0, row=2, padx=5, pady=5)
            else:
                ttk.Label(frm, text="No user profiles detected please create a new profile").grid(column=0, row=0, padx=5, pady=5)
                ttk.Button(frm, text="Create new profile", command=lambda:[task_window.withdraw(), self.create_table(task_window)]).grid(column=0, row=1, padx=5, pady=5)
            ttk.Button(frm, text="Quit", command=lambda:[task_window.destroy(), self.root.destroy()]).grid(column=0, row=6, padx=5, pady=5)
            task_window.protocol("WM_DELETE_WINDOW", lambda:[task_window.destroy(), self.root.destroy()])
        

    def select_table(self, parent):
        tables = self.DBmng.get_table_names()
        task_window = Toplevel(self.root)
        self.win_geometry(300, 400, task_window)
        frm = ttk.Frame(task_window, padding=10)
        frm.grid()
        ttk.Label(frm, text="Select one of the existing profiles").grid(column=0, row=0)
        x = 1
        for table in tables:
            ttk.Label(frm, text=table).grid(column=0, row=x)
            ttk.Button(frm, text='Select', command=lambda table=table:[task_window.destroy(), parent.destroy(), self.assign_current_table(table), self.profile_name_update(), self.date_check(), self.root.deiconify()]).grid(column=1, row=x)
            x += 1
        ttk.Button(frm, text="Return", command=lambda:[task_window.destroy(), parent.deiconify()]).grid(column=0, row=x)
        task_window.protocol("WM_DELETE_WINDOW", lambda:[task_window.destroy(), self.root.destroy()])


    def create_table(self, parent):
        task_window = Toplevel(self.root)
        self.win_geometry(300, 400, task_window)
        frm = ttk.Frame(task_window, padding=10)
        frm.grid()
        new_table_name = StringVar()
        ttk.Label(frm, text="Enter a new profile name").grid(column=0, row=0)
        ttk.Entry(frm, textvariable=new_table_name).grid(column=1, row=0)
        ttk.Button(frm, text="Confirm", command=lambda:[task_window.destroy(), parent.destroy(), self.profile_creation_msg(new_table_name.get()), self.DBmng.create_models(new_table_name.get()), self.assign_current_table(new_table_name.get()), self.root.deiconify()]).grid(column=0, row=1)
        ttk.Button(frm, text="Return", command=lambda:[task_window.destroy(), parent.deiconify()]).grid(column=1, row=1)
        task_window.protocol("WM_DELETE_WINDOW", lambda:[task_window.destroy(), self.root.destroy()])


    def delete_table_window(self):
        tables = self.DBmng.get_table_names()
        task_window = Toplevel(self.root)
        self.win_geometry(300, 400, task_window)
        frm = ttk.Frame(task_window, padding=10)
        frm.grid()
        ttk.Label(frm, text="Select a profile to delete").grid(column=0, row=0)
        x = 1
        for table in tables:
            ttk.Label(frm, text=table).grid(column=0, row=x)
            ttk.Button(frm, text='Delete', command=lambda table=table:[task_window.withdraw(), self.delete_table(table, task_window)]).grid(column=1, row=x)
            x += 1
        ttk.Button(frm, text="Return", command=lambda:[task_window.destroy(), self.root.deiconify()]).grid(column=0, row=x)
        task_window.protocol("WM_DELETE_WINDOW", lambda:[task_window.destroy(), self.root.deiconify()])


    def delete_table(self, table_name, parent):
        confirm = messagebox.askyesno(message=f"Are you sure you want to delete user profile: '{table_name}'", title="Delete profile?")
        if confirm:
            table_to_del = self.DBmng.get_model(table_name)
            parent.destroy()
            if table_to_del.__tablename__ == self.current_table.__tablename__:
                self.deselect_current_table()
            table_to_del.__table__.drop(models.engine)
            messagebox.showinfo(message="Profile deleted")
            if self.current_table:
                self.root.deiconify()
            else:
                self.table_select_window()
        else:
            self.return_win(parent)


    def show_task(self):
        task_window = Toplevel(self.root)
        self.win_geometry(300, 400, task_window)
        frm = ttk.Frame(task_window, padding=10)
        frm.grid()
        if models.session.query(self.current_table).count() == 0:
            ttk.Label(frm, text="Currently no tasks for this profile").grid(column=0, row=0)
        x = 1
        for reminder in models.session.query(self.current_table):
            ttk.Label(frm, text=reminder).grid(column=0, row=x)
            x += 1
        ttk.Button(frm, text="Return", command=lambda:[task_window.destroy(), self.root.deiconify()]).grid(column=0, row=x)
        task_window.protocol("WM_DELETE_WINDOW", lambda:self.on_closing(task_window))
        

    def add_task_window(self, cal_deadline=""):
        task_window = Toplevel(self.root)
        self.win_geometry(300, 400, task_window)
        frm = ttk.Frame(task_window, padding=10)
        frm.grid()
        new_task_type = StringVar()
        new_task_description = StringVar()
        new_task_deadline = StringVar()
        new_task_deadline.set(cal_deadline)
        ttk.Label(frm, text="Add a new task").grid(column=0, row=0)
        ttk.Label(frm, text="Enter what type of task").grid(column=0, row=1)
        ttk.Entry(frm, textvariable=new_task_type).grid(column=1, row=1)
        ttk.Label(frm, text="Enter a brief description of the task").grid(column=0, row=2)
        ttk.Entry(frm, textvariable=new_task_description).grid(column=1, row=2)
        ttk.Label(frm, text="Enter the task deadline, if it has one. Enter the date in numerical day-month-year format ie 22-07-1992").grid(column=0, row=3)
        ttk.Entry(frm, textvariable=new_task_deadline).grid(column=1, row=3)
        ttk.Button(frm, text="Confirm", command=lambda:[task_window.withdraw(), self.confirm_add(new_task_type, new_task_description, new_task_deadline, task_window)]).grid(column=0, row=4)
        ttk.Button(frm, text="Return", command=lambda:[task_window.destroy(), self.root.deiconify()]).grid(column=1, row=4)
        task_window.protocol("WM_DELETE_WINDOW", lambda:self.on_closing(task_window))

    
    def confirm_add(self, new_task_type, task_description, task_deadline, parent):
        if not new_task_type.get() or not task_description.get():
            messagebox.showinfo(message="Sorry both the task type and task description are needed to create a new task.\nPlease enter values for these fields")
            parent.deiconify()
        else:
            clean_deadline = self.date_clean(task_deadline.get())
            confirm = messagebox.askyesno(message=f"You have entered {new_task_type.get()} for the task type, {task_description.get()} for the task description and {self.simple_date(clean_deadline)} for the deadline. Is this correct?", title="check your info")
            if confirm:
                new_task = self.current_table(task_type = new_task_type.get(), description=task_description.get(), deadline=clean_deadline)
                models.session.add(new_task)
                models.session.commit()
                parent.destroy()
                messagebox.showinfo(message="Task added!")
                try:
                    if cal_window.winfo_exists():
                        cal_window.deiconify()
                except NameError:
                    pass
                else:
                    self.root.deiconify()
            else:
                self.return_win(parent)


    def edit_delete_task_window(self):
        task_window = Toplevel(self.root)
        self.win_geometry(300, 400, task_window)
        frm = ttk.Frame(task_window, padding=10)
        frm.grid()
        ttk.Label(frm, text="Choose a task to delete").grid(column=0, row=0)
        x = 1
        for task in models.session.query(self.current_table):
            ttk.Label(frm, text=task).grid(column=0, row=x)
            ttk.Button(frm, text='Edit', command=lambda task=task:[task_window.withdraw(), self.edit_task(task, task_window)]).grid(column=1, row=x)
            ttk.Button(frm, text='Delete', command=lambda task=task:[task_window.withdraw(), self.delete_task(task, task_window)]).grid(column=2, row=x)
            x +=1
        ttk.Button(frm, text='Return', command=lambda:[task_window.destroy(), self.root.deiconify()]).grid(column=0, row=x)
        task_window.protocol("WM_DELETE_WINDOW", lambda:self.on_closing(task_window))


    def delete_task(self, task, parent):
        confirm = messagebox.askyesno(message=f"You have selected '{task}' task to delete. Is this correct?", title="Delete task?")
        if confirm:       
            models.session.delete(task)
            models.session.commit()
            parent.destroy()
            messagebox.showinfo(message="Task deleted!")
            self.root.deiconify()
        else:
            self.return_win(parent)

    
    def edit_task(self, task, parent):
        task_window = Toplevel(self.root)
        self.win_geometry(300, 400, task_window)
        frm = ttk.Frame(task_window, padding=10)
        frm.grid()
        edited_task_type = StringVar()
        edited_task_description = StringVar()
        edited_task_deadline = StringVar()
        ttk.Label(frm, text="Enter new values in any field you wish to edit, otherwise leave them blank").grid(column=0, row=0)
        ttk.Label(frm, text=f"Current type of task: {task.task_type}").grid(column=0, row=1)
        ttk.Entry(frm, textvariable=edited_task_type).grid(column=1, row=1)
        ttk.Label(frm, text=f"Current description: {task.description}").grid(column=0, row=2)
        ttk.Entry(frm, textvariable=edited_task_description).grid(column=1, row=2)
        ttk.Label(frm, text=f"Current deadline: {self.simple_date(task.deadline)}").grid(column=0, row=3)
        ttk.Entry(frm, textvariable=edited_task_deadline).grid(column=1, row=3)
        ttk.Button(frm, text="Confirm", command=lambda:[parent.destroy(), task_window.withdraw(), self.confirm_edit(edited_task_type, edited_task_description, edited_task_deadline, task, task_window)]).grid(column=0, row=4)
        ttk.Button(frm, text="Return", command=lambda:[task_window.destroy(), self.return_win(parent)]).grid(column=1, row=4)
        task_window.protocol("WM_DELETE_WINDOW", lambda:self.on_closing(task_window))


    def confirm_edit(self, edited_task_type, edited_task_description, edited_task_deadline, task_to_edit, parent):
        clean_deadline = self.date_clean(edited_task_deadline.get())
        if edited_task_type.get():
            type = edited_task_type.get()
        else:
            type = task_to_edit.task_type
        if edited_task_description.get():
            description = edited_task_description.get()
        else:
            description = task_to_edit.description
        if clean_deadline:
            deadline = clean_deadline
        else:
            deadline = task_to_edit.deadline
        confirm = messagebox.askyesno(message=f"If you confirm this edit the new task values will be:\nTask type: {type}, Description: {description}, Deadline: {self.simple_date(deadline)}", title="Edit task?")
        if confirm:
            task_to_edit.task_type = type
            task_to_edit.description = description
            task_to_edit.deadline = deadline
            models.session.commit()
            parent.destroy()
            messagebox.showinfo(message="Task edited!")
            self.root.deiconify()
        else:
            self.return_win(parent)


    def urgent_task(self):
        urgent_time = datetime.now() + timedelta(days=3)
        urgent_time = urgent_time.date()
        current_time = datetime.now().date()
        task_window = Toplevel(self.root)
        self.win_geometry(300, 400, task_window)
        frm = ttk.Frame(task_window, padding=10)
        frm.grid()
        x = 0
        if len(list(models.session.query(self.current_table).filter(self.current_table.deadline.isnot(None)).filter(self.current_table.deadline <= urgent_time))) != 0:
            for reminder in models.session.query(self.current_table).filter(self.current_table.deadline.isnot(None)).filter(self.current_table.deadline <= urgent_time):
                ttk.Label(frm, text=reminder).grid(column=0, row=x)
                ttk.Label(frm, text=f"This is in {reminder.deadline - current_time}").grid(column=0, row=x+1)
                x +=1
        else:
            ttk.Label(frm, text=f"No tasks have deadlines before {urgent_time}").grid(column=0, row=x)
        ttk.Button(frm, text="Return", command=lambda:[task_window.destroy(), self.root.deiconify()]).grid(column=0, row=x+2)
        task_window.protocol("WM_DELETE_WINDOW", lambda:self.on_closing(task_window))


    def date_clean(self, date):
        for fmt in ["%d-%m-%Y", '%d.%m.%Y', '%d/%m/%Y', '%d %m %Y']:
            try:
                cleaned_date = datetime.strptime(date, fmt).date()
            except ValueError:
                pass
            else:
                return cleaned_date
        return None


    def date_check(self):
        if self.current_table != None:
            current_date = datetime.now().date()
            if len(list(models.session.query(self.current_table).filter(self.current_table.deadline.isnot(None)).filter(self.current_table.deadline < current_date))):
                task_window = Toplevel(self.root)
                self.win_geometry(300, 400, task_window)
                frm = ttk.Frame(task_window, padding=10)
                frm.grid()
                x = 0
                for reminder in models.session.query(self.current_table).filter(self.current_table.deadline.isnot(None)).filter(self.current_table.deadline < current_date):
                    ttk.Label(frm, text=f"{reminder.description} is scheduled to have already happened would you like to delete or edit this entry?").grid(column=0, row=x)
                    ttk.Button(frm, text='Edit task', command=lambda:[task_window.withdraw(), self.edit_task_window(reminder, task_window)]).grid(column=1, row=x)
                    ttk.Button(frm, text='Delete task', command=lambda:[task_window.withdraw(), self.delete_task(reminder, task_window), self.date_check()]).grid(column=2, row=x)
                    x +=1
                task_window.protocol("WM_DELETE_WINDOW", lambda:self.on_closing(task_window))

    
    def return_win(self, current_parent):
        if current_parent:
            current_parent.deiconify()
        else:
            self.root.deiconify()


    def on_closing(self, current_window):
        current_window.destroy()
        self.root.deiconify()


    def simple_date(self, deadline):
        if deadline:
            deadline = deadline.strftime("%d/%m/%Y")
        return deadline

    
    def assign_current_table(self, table_name):
        self.current_table = self.DBmng.get_model(table_name)
        

    def deselect_current_table(self):
        self.current_table = None


    def profile_creation_msg(self, table_name):
        if table_name in self.DBmng.get_table_names():
            messagebox.showinfo(message="Profile of same name already found, profile has not been created")
        else:
            messagebox.showinfo(message="Profile created!")


    def profile_name_update(self):
        if self.current_table:
            self.current_profile_name.set(self.current_table.__tablename__)


    def win_geometry(self, width, height, window):
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw/2) - (width/2)
        y = (sh/2) - (height/2)
        return window.geometry('+%d+%d' % (x, y))



if __name__ == '__main__':
    app = OrganiserApp()
    app.app_running()