from datetime import datetime, timedelta
from draft_manager import DraftManager
from models import models
from tkinter import Tk, ttk, Toplevel, StringVar, messagebox
from tkcalendar import Calendar


class OrganiserApp():


    def __init__(self) -> None:
        self.root = Tk()
        self.dm = DraftManager()
        self.root.title("Organiser")
        self.current_user = None
        self.current_profile_name = StringVar()
    

    def app_running(self) -> None:
        self.win_geometry(300, 400, self.root)
        frm = ttk.Frame(self.root, padding=10)
        frm.grid()
        self.user_select_create_window()
        ttk.Label(frm, text="Welcome to my organiser app").grid(column=0, row=0, padx=5, pady=5)
        ttk.Label(frm, text="Current profile:").grid(column=0, row=1, padx=5, pady=5)
        ttk.Label(frm, textvariable=self.current_profile_name).grid(column=1, row=1, padx=5, pady=5)
        ttk.Button(frm, text="Show tasks", command=lambda:[self.root.withdraw(), self.show_task()]).grid(column=0, row=2, padx=5, pady=5)
        ttk.Button(frm, text="Show all urgent tasks", command=lambda:[self.root.withdraw(), self.urgent_task()]).grid(column=0, row=3, padx=5, pady=5)
        ttk.Button(frm, text="Calendar", command=lambda:[self.root.withdraw(), self.calendar_view()]).grid(column=0, row=4, padx=5, pady=5)
        ttk.Button(frm, text="Add a new task", command=lambda:[self.root.withdraw(), self.add_task_window(self.root)]).grid(column=0, row=5, padx=5, pady=5)
        ttk.Button(frm, text="Delete or Edit a task", command=lambda:[self.root.withdraw(), self.edit_delete_task_window(self.root)]).grid(column=0, row=6, padx=5, pady=5)
        ttk.Button(frm, text="Select or Create new profile", command=lambda:[self.deselect_current_user(), self.user_select_create_window()]).grid(column=0, row=7, padx=5, pady=5)
        ttk.Button(frm, text="Delete or Edit existing profile", command=lambda:[self.root.withdraw(), self.edit_delete_user_window()]).grid(column=0, row=8, padx=5, pady=5)
        ttk.Button(frm, text="Quit", command=self.root.destroy).grid(column=0, row=9, padx=5, pady=5)
        self.root.protocol("WM_DELETE_WINDOW", lambda:[self.root.destroy()])
        self.root.mainloop()


    def calendar_view(self) -> None:
        def pass_date(i):
            self.cal_tasks(cal.get_date(), tasks)
        cal_window = Toplevel(self.root)
        self.win_geometry(300, 400, cal_window)
        date = StringVar(cal_window, Calendar.date.today().strftime("%d/%m/%y"))
        tasks = StringVar(cal_window)
        cal = Calendar(cal_window, selectmode="day", textvariable=date)
        cal.pack()
        ttk.Label(cal_window, textvariable=date).pack(padx=10, pady=10)
        ttk.Label(cal_window, text="Tasks for this date:").pack(padx=5, pady=5)
        ttk.Label(cal_window, textvariable=tasks).pack(padx=5, pady=5)
        ttk.Button(cal_window, text="Add task to this date", command=lambda:[cal_window.withdraw(), self.add_task_window(cal_window, cal.get_date())]).pack(padx=5, pady=5)
        ttk.Button(cal_window, text="Edit or Delete task on this date", command=lambda:[cal_window.withdraw(), self.edit_delete_task_window(cal_window, self.date_clean(cal.get_date()))]).pack(padx=5, pady=5)
        ttk.Button(cal_window, text="Return", command=lambda:[cal_window.destroy(), self.root.deiconify()]).pack(padx=10, pady=10)
        cal.bind("<<CalendarSelected>>", pass_date)
        cal_window.protocol("WM_DELETE_WINDOW", lambda:[cal_window.destroy(), self.root.destroy()])


    def cal_tasks(self, str_date: str, tasks_str: str) -> None:
        date = datetime.strptime(str_date, "%d/%m/%Y").date()
        if self.current_user.tasks.filter(models.Task.deadline==date).count() > 0:
            tasks = ""
            for model in self.current_user.tasks.filter(models.Task.deadline==date):
                tasks = tasks + "-" + model.task_type + ", " + model.description + "\n"
        else:
            tasks = "No tasks"
        tasks_str.set(tasks)


##  User table functions ##
    
    def user_select_create_window(self) -> None:
        if self.current_user == None:
            self.root.withdraw()
            task_window = Toplevel(self.root)
            self.win_geometry(300, 400, task_window)
            frm = ttk.Frame(task_window, padding=10)
            frm.grid()
            if models.session.query(models.User).count():
                ttk.Label(frm, text="Select a user profile or create a new one").grid(column=0, row=0, padx=5, pady=5)
                ttk.Button(frm, text="Select existing profile", command=lambda:[task_window.withdraw, self.select_user(task_window)]).grid(column=0, row=1, padx=5, pady=5)
                ttk.Button(frm, text="Create new profile", command=lambda:[task_window.withdraw(), self.create_user_window(task_window)]).grid(column=0, row=2, padx=5, pady=5)
            else:
                ttk.Label(frm, text="No user profiles detected please create a new profile").grid(column=0, row=0, padx=5, pady=5)
                ttk.Button(frm, text="Create new profile", command=lambda:[task_window.withdraw(), self.create_user_window(task_window)]).grid(column=0, row=1, padx=5, pady=5)
            ttk.Button(frm, text="Quit", command=lambda:[task_window.destroy(), self.root.destroy()]).grid(column=0, row=6, padx=5, pady=5)
            task_window.protocol("WM_DELETE_WINDOW", lambda:[task_window.destroy(), self.root.destroy()])
        

    def select_user(self, parent: Toplevel) -> None:
        task_window = Toplevel(self.root)
        self.win_geometry(300, 400, task_window)
        frm = ttk.Frame(task_window, padding=10)
        frm.grid()
        ttk.Label(frm, text="Select one of the existing profiles").grid(column=0, row=0)
        x = 1
        for user in models.session.query(models.User):
            ttk.Label(frm, text=user.user_name).grid(column=0, row=x)
            ttk.Button(frm, text="Select", command=lambda user=user:[task_window.destroy(), parent.destroy(), self.assign_current_user(user), self.user_assign_bad_date()]).grid(column=1, row=x)
            x += 1
        ttk.Button(frm, text="Return", command=lambda:[task_window.destroy(), parent.deiconify()]).grid(column=0, row=x)
        task_window.protocol("WM_DELETE_WINDOW", lambda:[task_window.destroy(), self.root.destroy()])


    def create_user_window(self, parent: Toplevel) -> None:
        task_window = Toplevel(self.root)
        self.win_geometry(300, 400, task_window)
        frm = ttk.Frame(task_window, padding=10)
        frm.grid()
        new_user_name = StringVar()
        new_user_email = StringVar()
        ttk.Label(frm, text="Enter a new profile name").grid(column=0, row=0)
        ttk.Entry(frm, textvariable=new_user_name).grid(column=1, row=0)
        ttk.Label(frm, text="Enter a your email address").grid(column=0, row=1)
        ttk.Entry(frm, textvariable=new_user_email).grid(column=1, row=1)
        ttk.Button(frm, text="Confirm", command=lambda:[task_window.withdraw(), parent.destroy(), self.create_user(new_user_name.get(), new_user_email.get(), task_window), self.user_assign_bad_date()]).grid(column=0, row=2)
        ttk.Button(frm, text="Return", command=lambda:[task_window.destroy(), parent.deiconify()]).grid(column=1, row=2)
        task_window.protocol("WM_DELETE_WINDOW", lambda:[task_window.destroy(), self.root.destroy()])

    
    def create_user(self, new_user_name: str, new_user_email: str, parent: Toplevel) -> None:
        if not new_user_name or not new_user_email:
            messagebox.showinfo(message="You need to enter both a user name and an email address")
            parent.deiconify()
            return
        for user in models.session.query(models.User):
            if user.user_name == new_user_name:
                messagebox.showinfo(message="Profile of same name already found, profile has not been created")
                parent.deiconify()
                return
        parent.destroy()
        new_user = models.User(user_name=new_user_name, user_email=new_user_email)
        models.session.add(new_user)
        models.session.commit()
        messagebox.showinfo(message="Profile created!")
        self.assign_current_user(new_user)


    def edit_delete_user_window(self) -> None:
        task_window = Toplevel(self.root)
        self.win_geometry(300, 400, task_window)
        frm = ttk.Frame(task_window, padding=10)
        frm.grid()
        ttk.Label(frm, text="Select a profile to Delete or Edit").grid(column=0, row=0)
        x = 1
        for user in models.session.query(models.User):
            ttk.Label(frm, text=user.user_name).grid(column=0, row=x)
            ttk.Button(frm, text="Delete", command=lambda user=user:[task_window.withdraw(), self.delete_user(user, task_window)]).grid(column=1, row=x)
            ttk.Button(frm, text="Edit", command=lambda user=user:[task_window.withdraw(), self.edit_user_new_value_window(user, task_window)]).grid(column=1, row=x)
            x += 1
        ttk.Button(frm, text="Return", command=lambda:[task_window.destroy(), self.root.deiconify()]).grid(column=0, row=x)
        task_window.protocol("WM_DELETE_WINDOW", lambda:[task_window.destroy(), self.root.deiconify()])


    def delete_user(self, user: models.User, parent: Toplevel) -> None:
        confirm = messagebox.askyesno(message=f"Are you sure you want to delete user profile: '{user.user_name}'", title="Delete profile?")
        if confirm:
            parent.destroy()
            if user == self.current_user:
                self.deselect_current_user()
            for task in user.tasks:
                if task.draft_id:
                    self.delete_draft(task.draft_id)
            models.session.delete(user)
            models.session.commit()
            messagebox.showinfo(message="Profile deleted")
            if self.current_user:
                self.root.deiconify()
            else:
                self.user_select_create_window()
        else:
            self.return_win(parent)


    def edit_user_new_value_window(self, user: models.User, parent: Toplevel) -> None:
        task_window = Toplevel(self.root)
        self.win_geometry(300, 400, task_window)
        frm = ttk.Frame(task_window, padding=10)
        frm.grid()
        edited_user_name = StringVar()
        edited_user_email = StringVar()
        ttk.Label(frm, text="Enter new values in any field you wish to edit, otherwise leave them blank").grid(column=0, row=0)
        ttk.Label(frm, text=f"Current User name: {user.user_name}").grid(column=0, row=1)
        ttk.Entry(frm, textvariable=edited_user_name).grid(column=1, row=1)
        ttk.Label(frm, text=f"Current User email: {user.user_email}").grid(column=0, row=2)
        ttk.Entry(frm, textvariable=edited_user_email).grid(column=1, row=2)
        ttk.Button(frm, text="Confirm", command=lambda:[parent.withdraw(), task_window.withdraw(), self.confirm_edit_user(edited_user_name, edited_user_email, user, task_window, parent)]).grid(column=0, row=4)
        ttk.Button(frm, text="Return", command=lambda:[task_window.destroy(), self.return_win(parent)]).grid(column=1, row=4)
        task_window.protocol("WM_DELETE_WINDOW", lambda:self.on_closing(task_window))

    
    def confirm_edit_user(self, edited_user_name: StringVar, edited_user_email: StringVar, user_to_edit: models.User, parent: Toplevel, grandparent: Toplevel) -> None:
        if edited_user_name.get():
            user_name = edited_user_name.get()
        else:
            user_name = user_to_edit.user_name
        if edited_user_email.get():
            user_email = edited_user_email.get()
        else:
            user_email = user_to_edit.user_email
        confirm = messagebox.askyesno(message=f"If you confirm this edit the new user values will be:\nUser name: {user_name}, User email: {user_email}", title="Edit user?")
        if confirm:
            parent.destroy()
            grandparent.destroy()
            if user_to_edit == self.current_user:
                self.deselect_current_user()
            user_to_edit.user_name = user_name
            user_to_edit.user_email = user_email
            models.session.commit()
            if edited_user_email.get():
                self.update_draft_new_email(user_email, user_to_edit)
            self.root.deiconify()
        else:
            self.return_win(parent)


## Task table functions ##

    def show_task(self) -> None:
        task_window = Toplevel(self.root)
        self.win_geometry(300, 400, task_window)
        frm = ttk.Frame(task_window, padding=10)
        frm.grid()
        if self.current_user.tasks.count() == 0:
            ttk.Label(frm, text="Currently no tasks for this profile").grid(column=0, row=0)
        x = 1
        for reminder in self.current_user.tasks:
            ttk.Label(frm, text=reminder).grid(column=0, row=x)
            x += 1
        ttk.Button(frm, text="Return", command=lambda:[task_window.destroy(), self.root.deiconify()]).grid(column=0, row=x)
        task_window.protocol("WM_DELETE_WINDOW", lambda:self.on_closing(task_window))
        

    def add_task_window(self, parent: Toplevel, cal_deadline="") -> None:
        if self.date_clean(cal_deadline) and self.date_clean(cal_deadline) < datetime.now().date():
            messagebox.showinfo(message="Sorry you can't add tasks with past dates")
            parent.deiconify()
        else:
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
            ttk.Label(frm, text="Enter the task deadline, if it has one. Enter the date in numerical day-month-year format ie 22/07/1992").grid(column=0, row=3)
            ttk.Entry(frm, textvariable=new_task_deadline).grid(column=1, row=3)
            ttk.Button(frm, text="Confirm", command=lambda:[task_window.withdraw(), self.confirm_add(new_task_type, new_task_description, new_task_deadline, task_window, parent)]).grid(column=0, row=4)
            ttk.Button(frm, text="Return", command=lambda:[task_window.destroy(), self.return_win(parent)]).grid(column=1, row=4)
            task_window.protocol("WM_DELETE_WINDOW", lambda:self.on_closing(task_window))

    
    def confirm_add(self, new_task_type: StringVar, new_task_description: StringVar, new_task_deadline: StringVar, parent: Toplevel, grandparent: Toplevel) -> None:
        clean_deadline = self.date_clean(new_task_deadline.get())
        task_draft_id = None
        if not new_task_type.get() or not new_task_description.get():
            messagebox.showinfo(message="Sorry both the task type and task description are needed to create a new task.\nPlease enter values for these fields")
            parent.deiconify()
        elif clean_deadline < datetime.now().date():
            messagebox.showinfo(message="Sorry you can't add tasks with past dates")
            parent.deiconify()
        else:
            confirm = messagebox.askyesno(message=f"You have entered {new_task_type.get()} for the task type, {new_task_description.get()} for the task description and {self.simple_date(clean_deadline)} for the deadline. Is this correct?", title="check your info")
            if confirm:
                if clean_deadline:
                    task_draft_id = self.send_to_draft(new_task_description.get(), clean_deadline)
                new_task = models.Task(task_type = new_task_type.get(), description=new_task_description.get(), deadline=clean_deadline, user_id=self.current_user.id, draft_id=task_draft_id)
                models.session.add(new_task)
                models.session.commit()
                parent.destroy()
                messagebox.showinfo(message="Task added!")
                grandparent.deiconify()
            else:
                self.return_win(parent)


    def edit_delete_task_window(self, parent: Toplevel, cal_date=None) -> None:
        task_window = Toplevel(self.root)
        self.win_geometry(300, 400, task_window)
        frm = ttk.Frame(task_window, padding=10)
        frm.grid()
        ttk.Label(frm, text="Choose a task to delete").grid(column=0, row=0)
        x = 1
        if cal_date is None:
            for task in self.current_user.tasks:
                ttk.Label(frm, text=task).grid(column=0, row=x)
                ttk.Button(frm, text="Edit", command=lambda task=task:[task_window.withdraw(), self.edit_task(task, task_window, parent)]).grid(column=1, row=x)
                ttk.Button(frm, text="Delete", command=lambda task=task:[task_window.withdraw(), self.delete_task(task, task_window, parent)]).grid(column=2, row=x)
                x +=1
        else:
            for task in self.current_user.tasks.filter(models.Task.deadline==cal_date):
                ttk.Label(frm, text=task).grid(column=0, row=x)
                ttk.Button(frm, text="Edit", command=lambda task=task:[task_window.withdraw(), self.edit_task(task, task_window, parent)]).grid(column=1, row=x)
                ttk.Button(frm, text="Delete", command=lambda task=task:[task_window.withdraw(), self.delete_task(task, task_window, parent)]).grid(column=2, row=x)
                x +=1
        ttk.Button(frm, text="Return", command=lambda:[task_window.destroy(), self.return_win(parent)]).grid(column=0, row=x)
        task_window.protocol("WM_DELETE_WINDOW", lambda:self.on_closing(task_window))


    def delete_task(self, task: models.Task, parent: Toplevel, grandparent: Toplevel) -> None:
        confirm = messagebox.askyesno(message=f"You have selected '{task}' task to delete. Is this correct?", title="Delete task?")
        if confirm:
            if task.draft_id:
                self.delete_draft(task.draft_id)       
            models.session.delete(task)
            models.session.commit()
            parent.destroy()
            messagebox.showinfo(message="Task deleted!")
            if self.bad_date_check():
                self.amend_bad_dates()
            else:
                menu_select = messagebox.askyesno(message="Would you like to Edit or Delete additional tasks?", title="Return to Edit/Delete menu?")
                if menu_select:
                    self.edit_delete_task_window(self.root)
                else:
                    grandparent.deiconify()
        else:
            self.return_win(parent)

    
    def edit_task(self, task: models.Task, parent: Toplevel, grandparent: Toplevel) -> None:
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
        ttk.Button(frm, text="Confirm", command=lambda:[parent.destroy(), task_window.withdraw(), self.confirm_edit(edited_task_type, edited_task_description, edited_task_deadline, task, task_window, grandparent)]).grid(column=0, row=4)
        ttk.Button(frm, text="Return", command=lambda:[task_window.destroy(), self.return_win(parent)]).grid(column=1, row=4)
        task_window.protocol("WM_DELETE_WINDOW", lambda:self.on_closing(task_window))


    def confirm_edit(self, edited_task_type: StringVar, edited_task_description: StringVar, edited_task_deadline: StringVar, task_to_edit: models.Task, parent: Toplevel, origin_window: Toplevel) -> None:
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
            if clean_deadline > datetime.now().date():
                deadline = clean_deadline
            else:
                messagebox.showinfo(message="Sorry you can't edit a deadline to be a past date")
                parent.deiconify()
        else:
            deadline = task_to_edit.deadline
        confirm = messagebox.askyesno(message=f"If you confirm this edit the new task values will be:\nTask type: {type}, Description: {description}, Deadline: {self.simple_date(deadline)}", title="Edit task?")
        if confirm:
            if deadline and task_to_edit.deadline:
                self.update_draft(description, deadline, task_to_edit.draft_id)
            if deadline and not task_to_edit.draft_id:
                draft_id = self.send_to_draft(description, deadline)
                task_to_edit.draft_id = draft_id
            task_to_edit.task_type = type
            task_to_edit.description = description
            task_to_edit.deadline = deadline
            models.session.commit()
            parent.destroy()
            messagebox.showinfo(message="Task edited!")
            if self.bad_date_check():
                self.amend_bad_dates()
            else:
                origin_window.deiconify()
        else:
            self.return_win(parent)


    def urgent_task(self) -> None:
        urgent_time = datetime.now() + timedelta(days=3)
        urgent_time = urgent_time.date()
        current_time = datetime.now().date()
        task_window = Toplevel(self.root)
        self.win_geometry(300, 400, task_window)
        frm = ttk.Frame(task_window, padding=10)
        frm.grid()
        x = 0
        urgent_tasks = self.current_user.tasks.filter((models.Task.deadline.isnot(None)) & (models.Task.deadline <= urgent_time))
        if (urgent_tasks).count() != 0:
            for reminder in urgent_tasks:
                ttk.Label(frm, text=reminder).grid(column=0, row=x)
                ttk.Label(frm, text=f"This is in {reminder.deadline - current_time}").grid(column=0, row=x+1)
                x +=1
        else:
            ttk.Label(frm, text=f"No tasks have deadlines before {urgent_time}").grid(column=0, row=x)
        ttk.Button(frm, text="Return", command=lambda:[task_window.destroy(), self.root.deiconify()]).grid(column=0, row=x+2)
        task_window.protocol("WM_DELETE_WINDOW", lambda:self.on_closing(task_window))


## Functions not for task or user creation/editing/deletion ##

    def date_clean(self, date: str)  -> None | datetime:
        for fmt in ["%d-%m-%Y", "%d.%m.%Y", "%d/%m/%Y", "%d %m %Y"]:
            try:
                cleaned_date = datetime.strptime(date, fmt).date()
            except ValueError:
                pass
            else:
                return cleaned_date
        return None


    def bad_date_check(self)  -> None | bool:
        if self.current_user != None:
            current_date = datetime.now().date()
            if (self.current_user.tasks.filter((models.Task.deadline.isnot(None)) & (models.Task.deadline < current_date))).count() != 0:
                return True
                

    def amend_bad_dates(self) -> None:
        current_date = datetime.now().date()
        self.root.withdraw()
        task_window = Toplevel(self.root)
        self.win_geometry(300, 400, task_window)
        frm = ttk.Frame(task_window, padding=10)
        frm.grid()
        x = 0
        for reminder in self.current_user.tasks.filter((models.Task.deadline.isnot(None)) & (models.Task.deadline < current_date)):
            ttk.Label(frm, text=f"{reminder.description} is scheduled to have already happened would you like to delete or edit this entry?").grid(column=0, row=x)
            ttk.Button(frm, text="Edit task", command=lambda:[task_window.withdraw(), self.edit_task(reminder, task_window, self.root)]).grid(column=1, row=x)
            ttk.Button(frm, text="Delete task", command=lambda:[task_window.withdraw(), self.delete_task(reminder, task_window, self.root)]).grid(column=2, row=x)
            x +=1
        task_window.protocol("WM_DELETE_WINDOW", lambda:self.on_closing(task_window))


    def user_assign_bad_date(self) -> None:
        if self.bad_date_check():
            self.amend_bad_dates()
        else:
            self.root.deiconify()


    def return_win(self, current_parent: Toplevel) -> None:
        if current_parent:
            current_parent.deiconify()
        else:
            self.root.deiconify()


    def on_closing(self, current_window: Toplevel) -> None:
        current_window.destroy()
        self.root.deiconify()


    def simple_date(self, deadline: datetime) -> str:
        if deadline:
            deadline = deadline.strftime("%d/%m/%Y")
        return deadline

    
    def assign_current_user(self, user: models.User) -> None:
        self.current_user = user
        self.profile_name_update()
        

    def deselect_current_user(self) -> None:
        self.current_user = None


    def profile_name_update(self) -> None:
        if self.current_user:
            self.current_profile_name.set(self.current_user.user_name)


    def win_geometry(self, width: int, height: int, window: Toplevel) -> None:
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw/2) - (width/2)
        y = (sh/2) - (height/2)
        window.geometry("+%d+%d" % (x, y))


## Draft functions ##

    def send_to_draft(self, task_desc: str, task_deadline: datetime) -> str:
        email_content = f"This is a gentle reminder that on {self.simple_date(task_deadline)} you have the task with the description: '{task_desc}',\nwhich is tomorrow!"
        draft_id = self.dm.create_draft(email_content, self.current_user.user_email, "A Gentle Reminder")
        return draft_id
        

    def update_draft(self, updated_message: str, updated_deadline: datetime, draft_id: str) -> bool:
        email_content = f"This is a gentle reminder that on {self.simple_date(updated_deadline)} you have the task with the description: '{updated_message}',\nwhich is tomorrow!"
        return self.dm.update_draft(email_content, self.current_user.user_email, "A Gentle Reminder", draft_id)


    def delete_draft(self, draft_id: str) -> bool:
        return self.dm.delete_draft(draft_id)


    def update_draft_new_email(self, new_email: str, user: models.User) -> bool:
        for task in user.tasks.filter(models.Task.draft_id.isnot(None)):
            if not self.dm.update_draft_email_only(new_email, task.draft_id):
                return False
        return True


if __name__ == "__main__":
    app = OrganiserApp()
    app.app_running()