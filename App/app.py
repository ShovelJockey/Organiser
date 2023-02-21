from datetime import datetime, timedelta, _Time, _Date, time
from models import models
from tkinter import Tk, ttk, Toplevel, StringVar, messagebox
from tkcalendar import Calendar


class OrganiserApp():


	def __init__(self) -> None:
		self.root = Tk()
		self.root.title("Organiser")
		self.current_user = None
		self.current_profile_name = StringVar()
	

	def app_running(self) -> None:
		'''
		Creates main app window only closes when program does, otherwise is withdrawn.
		'''
		# define window geometry and create window frame for root window
		self.win_geometry(300, 400, self.root)
		frm = ttk.Frame(self.root, padding=10)
		frm.grid()

		# force user to create or select existing user
		self.user_select_create_window()

		# define labels and buttons
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
		
		# protocol for X button in top window
		self.root.protocol("WM_DELETE_WINDOW", lambda:[self.root.destroy()])

		# equivilent to while loop preventing premature function end
		self.root.mainloop()


	def calendar_view(self) -> None:
		'''
		Create alendar view window, will load relevant tasks for selected day, 
		and link through to task creation, editing and deletion windows for repective day.
		'''
		# define function to pass to bind function updating tasks to current selected dates
		def pass_date(i):
			self.cal_tasks(cal.get_date(), tasks)

		# create window object
		cal_window = Toplevel(self.root)

		# define window geometry
		self.win_geometry(300, 400, cal_window)

		# create StringVar objects to capture user input
		date = StringVar(cal_window, Calendar.date.today().strftime("%d/%m/%y"))
		tasks = StringVar(cal_window)

		# create tkinter Calendar object
		cal = Calendar(cal_window, selectmode="day", textvariable=date)
		cal.pack()

		# define labels and buttons
		ttk.Label(cal_window, textvariable=date).pack(padx=10, pady=10)
		ttk.Label(cal_window, text="Tasks for this date:").pack(padx=5, pady=5)
		ttk.Label(cal_window, textvariable=tasks).pack(padx=5, pady=5)
		ttk.Button(cal_window, text="Add task to this date", command=lambda:[cal_window.withdraw(), self.add_task_window(cal_window, cal.get_date())]).pack(padx=5, pady=5)
		ttk.Button(cal_window, text="Edit or Delete task on this date", command=lambda:[cal_window.withdraw(), self.edit_delete_task_window(cal_window, self.date_clean(cal.get_date()))]).pack(padx=5, pady=5)
		ttk.Button(cal_window, text="Return", command=lambda:[cal_window.destroy(), self.root.deiconify()]).pack(padx=10, pady=10)
		
		# use get date function to update calendar tasks for the selected day info
		cal.bind("<<CalendarSelected>>", pass_date)

		# protocol for X button in window
		cal_window.protocol("WM_DELETE_WINDOW", lambda:[cal_window.destroy(), self.root.destroy()])


	def cal_tasks(self, str_date: str, tasks_str: StringVar) -> None:
		'''
		Takes a string of the calendar date and a StringVar object.
		String date is converted to datetime and used to filter all current user tasks,
		task data is then concatenated into a string which is set as StringVar value.
		'''
		# convert string to datetime
		date = datetime.strptime(str_date, "%d/%m/%Y").date()

		# check if any tasks for date, if so iterate over concatenating task info into string
		if self.current_user.tasks.filter(models.Task.deadline==date).count() > 0:
			tasks = ""
			for model in self.current_user.tasks.filter(models.Task.deadline==date):
				tasks = tasks + "-" + model.task_type + ", " + model.description + "\n"
		else:
			tasks = "No tasks"

		# set value of StringVar
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
			new_task_date = StringVar()
			new_task_time = StringVar()
			new_task_date.set(cal_deadline)
			ttk.Label(frm, text="Add a new task").grid(column=0, row=0)
			ttk.Label(frm, text="Enter what type of task").grid(column=0, row=1)
			ttk.Entry(frm, textvariable=new_task_type).grid(column=1, row=1)
			ttk.Label(frm, text="Enter a brief description of the task").grid(column=0, row=2)
			ttk.Entry(frm, textvariable=new_task_description).grid(column=1, row=2)
			ttk.Label(frm, text="Enter the task date, this is optional. Enter the date in numerical day-month-year format ie 22/07/1992").grid(column=0, row=3)
			ttk.Entry(frm, textvariable=new_task_date).grid(column=1, row=3)
			ttk.Label(frm, text="Enter the task time, this is optional but requires a date. Enter time in 24 hour format ie 20:30").grid(column=0, row=4)
			ttk.Entry(frm, textvariable=new_task_time).grid(column=1, row=4)
			ttk.Button(frm, text="Confirm", command=lambda:[task_window.withdraw(), self.confirm_add(new_task_type, new_task_description, new_task_date, new_task_time, task_window, parent)]).grid(column=0, row=5)
			ttk.Button(frm, text="Return", command=lambda:[task_window.destroy(), self.return_win(parent)]).grid(column=1, row=5)
			task_window.protocol("WM_DELETE_WINDOW", lambda:self.on_closing(task_window))

	
	def confirm_add(self, new_task_type: StringVar, new_task_description: StringVar, new_task_date: StringVar, new_task_time: StringVar, parent: Toplevel, grandparent: Toplevel) -> None:

		if not new_task_type.get() or not new_task_description.get():
			messagebox.showinfo(message="Sorry both the task type and task description are needed to create a new task.\nPlease enter values for these fields")
			parent.deiconify()

		deadline = self.date_clean(new_task_date.get())
		if deadline < datetime.now().date():
			messagebox.showinfo(message="Sorry you can't add tasks with past dates")
			parent.deiconify()

		clean_time = self.time_clean(new_task_time.get())
		if clean_time and not deadline:
			messagebox.showinfo(message="Sorry you can't add tasks with a time but no valid date")
			parent.deiconify()
		elif deadline and clean_time:
			deadline = datetime.combine(deadline, clean_time)
		elif deadline and not clean_time:
			default_time = time(0,0,0)
			deadline = datetime.combine(deadline, default_time)

		confirm = messagebox.askyesno(message=f"You have entered {new_task_type.get()} for the task type, {new_task_description.get()} for the task description and {self.simple_date(deadline)} for the deadline. Is this correct?", title="check your info")
		if confirm:
			new_task = models.Task(task_type = new_task_type.get(), description=new_task_description.get(), deadline=deadline, user_id=self.current_user.id)
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
		edited_task_date = StringVar()
		edited_task_time = StringVar()
		current_task_date = task.deadline.date().strftime("%d/%m/%Y")
		current_task_time = task.deadline.time().strftime("%H:%M")
		ttk.Label(frm, text="Enter new values in any field you wish to edit, otherwise leave them blank").grid(column=0, row=0)
		ttk.Label(frm, text=f"Current type of task: {task.task_type}").grid(column=0, row=1)
		ttk.Entry(frm, textvariable=edited_task_type).grid(column=1, row=1)
		ttk.Label(frm, text=f"Current description: {task.description}").grid(column=0, row=2)
		ttk.Entry(frm, textvariable=edited_task_description).grid(column=1, row=2)
		ttk.Label(frm, text=f"Current date: {current_task_date}").grid(column=0, row=3)
		ttk.Entry(frm, textvariable=edited_task_date).grid(column=1, row=3)
		ttk.Label(frm, text=f"Current time: {current_task_time}").grid(column=0, row=4)
		ttk.Entry(frm, textvariable=edited_task_time).grid(column=1, row=4)		
		ttk.Button(frm, text="Confirm", command=lambda:[parent.destroy(), task_window.withdraw(), self.confirm_edit(edited_task_type, edited_task_description, edited_task_date, edited_task_time, task, task_window, grandparent)]).grid(column=0, row=5)
		ttk.Button(frm, text="Return", command=lambda:[task_window.destroy(), self.return_win(parent)]).grid(column=1, row=5)
		task_window.protocol("WM_DELETE_WINDOW", lambda:self.on_closing(task_window))


	def confirm_edit(self, edited_task_type: StringVar, edited_task_description: StringVar, edited_task_date: StringVar, edited_task_time: StringVar, task_to_edit: models.Task, parent: Toplevel, origin_window: Toplevel) -> None:# account for date -> datetime
		date_object = self.date_clean(edited_task_date.get())
		time_object = self.time_clean(edited_task_time.get())

		if date_object and date_object < datetime.now().date():
			messagebox.showinfo(message="Sorry you can't edit a deadline to be a past date")
			parent.deiconify()
		
		if date_object and time_object:
			deadline = datetime.combine(date_object, time_object)
		elif date_object and not time_object:
			task_current_deadline = task_to_edit.deadline
			deadline = datetime.combine(date_object, task_current_deadline.time())
		elif not date_object and time_object:
			task_current_deadline = task_to_edit.deadline
			deadline = datetime.combine(task_current_deadline.date(), time_object)
		else:
			deadline = task_to_edit.deadline

		if edited_task_type.get():
			type = edited_task_type.get()
		else:
			type = task_to_edit.task_type

		if edited_task_description.get():
			description = edited_task_description.get()
		else:
			description = task_to_edit.description

		confirm = messagebox.askyesno(message=f"If you confirm this edit the new task values will be:\nTask type: {type}, Description: {description}, Deadline: {self.simple_date(deadline)}", title="Edit task?")
		if confirm:        
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


	def urgent_task(self) -> None:# account for date -> datetime
		urgent_time = datetime.now() + timedelta(days=3)
		current_time = datetime.now()
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

	def date_clean(self, date: str)  -> None | _Date:
		for fmt in ["%d-%m-%Y", "%d.%m.%Y", "%d/%m/%Y", "%d %m %Y"]:
			try:
				date_object = datetime.strptime(date, fmt).date()
			except ValueError:
				continue
			else:
				return date_object
		return None


	def time_clean(self, time: str) -> None | _Time:
		try:
			time_object = datetime.strptime(time, "%H:%M").time()
		except ValueError:
			return None
		else:
			return time_object


	def bad_date_check(self)  -> None | bool:
		if self.current_user != None:
			current_date = datetime.now()
			if (self.current_user.tasks.filter((models.Task.deadline.isnot(None)) & (models.Task.deadline < current_date))).count() != 0:
				return True
				

	def amend_bad_dates(self) -> None:
		current_date = datetime.now()
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
		if not deadline:
			return "No deadline"
		if deadline.time() == time(0,0,0):
			deadline = deadline.strftime("%d/%m/%Y")
		else:
			deadline = deadline.strftime("%d/%m/%Y :: %H:%M")
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


if __name__ == "__main__":
	app = OrganiserApp()
	app.app_running()