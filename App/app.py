from datetime import datetime, date, time
from models import models
from tkinter import Tk, ttk, Toplevel, StringVar, messagebox, Spinbox
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
		ttk.Button(frm, text="Show tasks", command=lambda:[self.root.withdraw(), self.show_tasks()]).grid(column=0, row=2, padx=5, pady=5)
		ttk.Button(frm, text="Calendar", command=lambda:[self.root.withdraw(), self.calendar_view()]).grid(column=0, row=3, padx=5, pady=5)
		ttk.Button(frm, text="Add a new task", command=lambda:[self.root.withdraw(), self.add_task_window(self.root)]).grid(column=0, row=4, padx=5, pady=5)
		ttk.Button(frm, text="Delete or Edit a task", command=lambda:[self.root.withdraw(), self.edit_delete_task_window(self.root)]).grid(column=0, row=5, padx=5, pady=5)
		ttk.Button(frm, text="Select or Create new profile", command=lambda:[self.deselect_current_user(), self.user_select_create_window()]).grid(column=0, row=6, padx=5, pady=5)
		ttk.Button(frm, text="Delete or Edit existing profile", command=lambda:[self.root.withdraw(), self.edit_delete_user_window()]).grid(column=0, row=7, padx=5, pady=5)
		ttk.Button(frm, text="Setting for current profile", command=lambda:[self.root.withdraw(), self.show_user_settings()]).grid(column=0, row=8, padx=5, pady=5)
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

		# load tasks for default date opened on
		pass_date(1)

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
		cal_window.protocol("WM_DELETE_WINDOW", lambda:self.on_closing(cal_window))


	def cal_tasks(self, str_date: str, tasks_str: StringVar) -> None:
		'''
		Takes a string of the calendar date and a StringVar object.
		String date is converted to datetime and used to filter all current user tasks,
		task data is then concatenated into a string which is set as StringVar value.
		'''
		# convert string to datetime
		date = datetime.strptime(str_date, "%d/%m/%Y").date()

		tasks = ""

		# iterate over concatenating task info into string if deadline date is today
		for task in self.current_user.tasks:
			if task.deadline.date() == date:
				tasks = tasks + "-" + task.task_type + ", " + task.description + "\n"
		
		#if string is empty assign msg
		if not tasks:
			tasks = "No tasks"

		# set value of StringVar
		tasks_str.set(tasks)


##  User table functions ##
	
	def user_select_create_window(self) -> None:
		'''
		Intermediate window, if no current user then prompt user to select existing user or create one buttons,
		calling select_user and create_user_window respectively.
		'''
		# if no assigned user
		if self.current_user == None:
			# withdraw root window
			self.root.withdraw()

			# create window object
			task_window = Toplevel(self.root)

			# define window geometry and create window Frame
			self.win_geometry(300, 400, task_window)
			frm = ttk.Frame(task_window, padding=10)
			frm.grid()

			# if any users in query prompt for either selection or creating new user
			if models.session.query(models.User).count():
				ttk.Label(frm, text="Select a user profile or create a new one").grid(column=0, row=0, padx=5, pady=5)
				ttk.Button(frm, text="Select existing profile", command=lambda:[task_window.withdraw, self.select_user(task_window)]).grid(column=0, row=1, padx=5, pady=5)
				ttk.Button(frm, text="Create new profile", command=lambda:[task_window.withdraw(), self.create_user_window(task_window)]).grid(column=0, row=2, padx=5, pady=5)
			
			# if no users only prompt for user creation
			else:
				ttk.Label(frm, text="No user profiles detected please create a new profile").grid(column=0, row=0, padx=5, pady=5)
				ttk.Button(frm, text="Create new profile", command=lambda:[task_window.withdraw(), self.create_user_window(task_window)]).grid(column=0, row=1, padx=5, pady=5)

			# quit buton returns ends program
			ttk.Button(frm, text="Quit", command=lambda:[task_window.destroy(), self.root.destroy()]).grid(column=0, row=6, padx=5, pady=5)

			# protocol for X button in window
			task_window.protocol("WM_DELETE_WINDOW", lambda:[task_window.destroy(), self.root.destroy()])
		

	def select_user(self, parent: Toplevel) -> None:
		'''
		Window that displays current users available for selection.
		Selected user sets user as self.current_user
		'''
		# create window object
		task_window = Toplevel(self.root)

		# define window geometry and create window Frame
		self.win_geometry(300, 400, task_window)
		frm = ttk.Frame(task_window, padding=10)
		frm.grid()

		# define label objects, iterate through existing users assigning them to label and button objects with incrementing grid positioning
		ttk.Label(frm, text="Select one of the existing profiles").grid(column=0, row=0)
		x = 1
		for user in models.session.query(models.User):
			ttk.Label(frm, text=user.user_name).grid(column=0, row=x)
			ttk.Button(frm, text="Select", command=lambda user=user:[task_window.destroy(), parent.destroy(), self.assign_current_user(user), self.user_assign_bad_date()]).grid(column=1, row=x)
			x += 1

		# quit buton returns to root window
		ttk.Button(frm, text="Return", command=lambda:[task_window.destroy(), parent.deiconify()]).grid(column=0, row=x)

		# protocol for X button in window
		task_window.protocol("WM_DELETE_WINDOW", lambda:[task_window.destroy(), self.root.destroy()])


	def create_user_window(self, parent: Toplevel) -> None:
		'''
		Window for entering infomation to create user entry in DB, 
		infomation passed to create_user function.
		'''
		# create window object
		task_window = Toplevel(self.root)

		# define window geometry and create window Frame
		self.win_geometry(300, 400, task_window)
		frm = ttk.Frame(task_window, padding=10)
		frm.grid()

		# create StringVar objects to capture user input
		new_user_name = StringVar()
		new_user_email = StringVar()

		# define label and entry boxes for information
		ttk.Label(frm, text="Enter a new profile name").grid(column=0, row=0)
		ttk.Entry(frm, textvariable=new_user_name).grid(column=1, row=0)
		ttk.Label(frm, text="Enter a your email address").grid(column=0, row=1)
		ttk.Entry(frm, textvariable=new_user_email).grid(column=1, row=1)

		# confirm button to progress to creating user pass value of StringVars as strings to create_user function, return to return to parent window
		ttk.Button(frm, text="Confirm", command=lambda:[task_window.withdraw(), parent.destroy(), self.create_user(new_user_name.get(), new_user_email.get(), task_window), self.user_assign_bad_date()]).grid(column=0, row=2)
		ttk.Button(frm, text="Return", command=lambda:[task_window.destroy(), parent.deiconify()]).grid(column=1, row=2)
		
		# protocol for X button in window
		task_window.protocol("WM_DELETE_WINDOW", lambda:[task_window.destroy(), self.root.destroy()])

	
	def create_user(self, new_user_name: str, new_user_email: str, parent: Toplevel) -> None:
		'''
		Creates new user if parameters meet requirements, then destroys parent window to leave only root window.
		'''
		# catch if either param string empty, unhides parent window and returns
		if not new_user_name or not new_user_email:
			messagebox.showinfo(message="You need to enter both a user name and an email address")
			parent.deiconify()
			return
		
		# catch for user with the same name already existing, unhides parent window and returns
		for user in models.session.query(models.User):
			if user.user_name == new_user_name:
				messagebox.showinfo(message="Profile of same name already found, profile has not been created")
				parent.deiconify()
				return
			
		# destroy parent window
		parent.destroy()

		# create new User object
		new_user = models.User(user_name=new_user_name, user_email=new_user_email)

		# add and commit it to session
		models.session.add(new_user)
		models.session.commit()

		# create new UserSettings object
		new_user_settings = models.UserSettings(id=new_user.id)

		# add and commit it to session
		models.session.add(new_user_settings)
		models.session.commit()

		# feedback to user
		messagebox.showinfo(message="Profile created!")

		# assign created user as current user
		self.assign_current_user(new_user)


	def edit_delete_user_window(self) -> None:
		'''
		Window gives option to edit or delete existing users,
		calling edit_user and delete_user respectively.
		'''
		# create window object
		task_window = Toplevel(self.root)

		# define window geometry and create window Frame
		self.win_geometry(300, 400, task_window)
		frm = ttk.Frame(task_window, padding=10)
		frm.grid()

		# define label objects, iterate through existing users assigning them to label and button objects with incrementing grid positioning
		ttk.Label(frm, text="Select a profile to Delete or Edit").grid(column=0, row=0)
		x = 1
		for user in models.session.query(models.User):
			ttk.Label(frm, text=user.user_name).grid(column=0, row=x)
			ttk.Button(frm, text="Delete", command=lambda user=user:[task_window.withdraw(), self.delete_user(user, task_window)]).grid(column=1, row=x)
			ttk.Button(frm, text="Edit", command=lambda user=user:[task_window.withdraw(), self.edit_user(user, task_window)]).grid(column=1, row=x)
			x += 1

		# quit buton returns to root window	
		ttk.Button(frm, text="Return", command=lambda:self.on_closing(task_window)).grid(column=0, row=x)

		# protocol for X button in window
		task_window.protocol("WM_DELETE_WINDOW", lambda:self.on_closing(task_window))


	def delete_user(self, user: models.User, parent: Toplevel) -> None:
		'''
		Deletes user DB entry if confirmed by user destroying parent window and unhiding root,
		if not confirmed unhides parent window.
		'''
		# messagebox confirming user deletion
		confirm = messagebox.askyesno(message=f"Are you sure you want to delete user profile: '{user.user_name}'", title="Delete profile?")
		if confirm:
			# destroy parent window
			parent.destroy()

			# if user is current_user deselect it to avoid issues
			if user == self.current_user:
				self.deselect_current_user()

			# delete user and commit session changes
			models.session.delete(user)
			models.session.commit()

			# feedback to user
			messagebox.showinfo(message="Profile deleted")

			# if current user unhide root window, else open select or create user window
			if self.current_user:
				self.root.deiconify()
			else:
				self.user_select_create_window()
		else:
			self.return_to_prev_window(parent)


	def edit_user(self, user: models.User, parent: Toplevel) -> None:
		'''
		Window for entering infomation to edit user entry in DB, 
		infomation passed to confirm_edit_user function.
		'''
		# create window object
		task_window = Toplevel(self.root)

		# define window geometry and create window Frame
		self.win_geometry(300, 400, task_window)
		frm = ttk.Frame(task_window, padding=10)
		frm.grid()

		# create StringVar objects to capture user input
		edited_user_name = StringVar()
		edited_user_email = StringVar()

		# define label and entry boxes for information
		ttk.Label(frm, text="Enter new values in any field you wish to edit, otherwise leave them blank").grid(column=0, row=0)
		ttk.Label(frm, text=f"Current User name: {user.user_name}").grid(column=0, row=1)
		ttk.Entry(frm, textvariable=edited_user_name).grid(column=1, row=1)
		ttk.Label(frm, text=f"Current User email: {user.user_email}").grid(column=0, row=2)
		ttk.Entry(frm, textvariable=edited_user_email).grid(column=1, row=2)

		# confirm button to progress to editing user pass value of StringVars as strings to confirm_edit_user function, return to return to parent window
		ttk.Button(frm, text="Confirm", command=lambda:[parent.withdraw(), task_window.withdraw(), self.confirm_edit_user(edited_user_name.get(), edited_user_email.get(), user, task_window, parent)]).grid(column=0, row=4)
		ttk.Button(frm, text="Return", command=lambda:[task_window.destroy(), self.return_to_prev_window(parent)]).grid(column=1, row=4)
		
		# protocol for X button in window
		task_window.protocol("WM_DELETE_WINDOW", lambda:self.on_closing(task_window))

	
	def confirm_edit_user(self, edited_user_name: str, edited_user_email: str, user_to_edit: models.User, parent: Toplevel, grandparent: Toplevel) -> None:
		'''
		Edits user DB entry if confirmed by user destroying parent window and unhiding root,
		if not confirmed unhides parent window.
		'''
		# if strings not empty assign to variable else assign current user entry value to that variable
		if edited_user_name:
			user_name = edited_user_name
		else:
			user_name = user_to_edit.user_name
		if edited_user_email:
			user_email = edited_user_email
		else:
			user_email = user_to_edit.user_email

		# messagebox confirming edit and displaying what new values will be
		confirm = messagebox.askyesno(message=f"If you confirm this edit the new user values will be:\nUser name: {user_name}, User email: {user_email}", title="Edit user?")
		if confirm:
			# destroy all windows other than root
			parent.destroy()
			grandparent.destroy()

			# if current user is being edited, deselect to avoid issues
			if user_to_edit == self.current_user:
				self.deselect_current_user()

			# assign new values and commit to session
			user_to_edit.user_name = user_name
			user_to_edit.user_email = user_email
			models.session.commit()

			# unhide root window
			self.root.deiconify()
		else:
			self.return_to_prev_window(parent)


## User Settings functions ##

	def show_user_settings(self):
		'''
		Window displaying settings for currently seletected user,
		gets UserSettings entry associated with current user.
		'''
		# create window object
		task_window = Toplevel(self.root)

		# define window geometry and create window Frame
		self.win_geometry(300, 400, task_window)
		frm = ttk.Frame(task_window, padding=10)
		frm.grid()

		# create stringvar objects to capture user input
		user_message = StringVar()
		user_offset = StringVar()
		user_second_message = StringVar()
		user_second_offset = StringVar()

		# set default values for boxes to current db values
		user_message.set(self.current_user.settings.reminder_message)
		user_offset.set(str(self.current_user.settings.reminder_offset))
		user_second_message.set(self.current_user.settings.additional_reminder_message)
		user_second_offset.set(str(self.current_user.settings.additional_reminder_offset))

		# define labels and entry boxes
		ttk.Label(frm, text="Edit settings for current user").grid(column=0, row=0)
		ttk.Label(frm, text="Days before task for reminder to be sent").grid(column=0, row=1)
		ttk.Spinbox(frm, from_=0, to=10, textvariable=user_offset).grid(column=1, row=1)
		ttk.Label(frm, text="Write a custom message for the reminder").grid(column=0, row=2)
		ttk.Entry(frm, textvariable=user_message).grid(column=1, row=2)
		ttk.Label(frm, text="Days before task for second reminder to be sent").grid(column=0, row=3)
		ttk.Spinbox(frm, from_=0, to=10, textvariable=user_second_offset).grid(column=1, row=3)
		ttk.Label(frm, text="Write a custom message for the second reminder").grid(column=0, row=4)
		ttk.Entry(frm, textvariable=user_second_message).grid(column=1, row=4)

		# confirm button to progress to editing user pass value of StringVars as strings to confirm_new_settings function, return to return to parent window
		ttk.Button(frm, text="Confirm", command=lambda:[task_window.withdraw(), self.confirm_new_settings(int(user_offset.get()), user_message.get(), int(user_second_offset.get()), user_second_message.get(), task_window)]).grid(column=0, row=5)
		ttk.Button(frm, text="Return", command=lambda:[task_window.destroy(), self.root.deiconify()]).grid(column=1, row=5)
		
		# protocol for X button in window
		task_window.protocol("WM_DELETE_WINDOW", lambda:self.on_closing(task_window))

		
	def confirm_new_settings(self, user_offset: int, user_message: str, user_second_offset: int, user_second_message: str, parent: Toplevel):
		'''
		Commits edits to user settings db if confirmed by user, destroying parent and returning root window.
		If not unhides parent window.
		'''
		
		# messagebox asking user to confirm new values
		confirm = messagebox.askyesno(message=f"Confirm new settings for current user, new settings:\nReminder days before task: {user_offset}\nReminder message: {user_message}\nSecond reminder days before task: {user_second_offset}\nSecond reminder message: {user_second_message}")
		if confirm:
			# destroy parent window
			parent.destroy()

			# assign new values to settings fields and commit to db
			self.current_user.settings.reminder_offset = user_offset
			self.current_user.settings.reminder_message = user_message
			self.current_user.settings.additional_reminder_offset = user_second_offset
			self.current_user.settings.additional_reminder_message = user_second_message
			models.session.commit()

			# unhide root
			self.root.deiconify()
		else:
			# unhide parent win
			self.return_to_prev_window(parent)


## Task table functions ##

	def show_tasks(self) -> None:
		'''
		Window displaying tasks for currently selected user, 
		gets all task entries with relationship to current user.
		'''
		# create window object
		task_window = Toplevel(self.root)

		# define window geometry and create window Frame
		self.win_geometry(300, 400, task_window)
		frm = ttk.Frame(task_window, padding=10)
		frm.grid()

		# if 1+ tasks associated with current user iterate through assigning string representation of entry to labels
		if self.current_user.tasks.count() >= 0:
			x = 1
			for reminder in self.current_user.tasks:
				ttk.Label(frm, text=reminder).grid(column=0, row=x)
				x += 1

		# else display no tasks label
		else:
			ttk.Label(frm, text="Currently no tasks for this profile").grid(column=0, row=0)

		# quit buton returns to root window	
		ttk.Button(frm, text="Return", command=lambda:self.on_closing(task_window)).grid(column=0, row=x)

		# protocol for X button in window
		task_window.protocol("WM_DELETE_WINDOW", lambda:self.on_closing(task_window))
		

	def add_task_window(self, parent: Toplevel, cal_deadline="") -> None:
		'''
		Window for adding tasks, can be accessed from root menu and calendar.
		When accessed from Calendar window, passes cal_deadline parameter to function of selected date in calendar.
		'''
		# if cal_deadline returns valid datetime object, but is a past date unhide parent window
		if self.date_clean(cal_deadline) and self.date_clean(cal_deadline) < datetime.now().date():
			messagebox.showinfo(message="Sorry you can't add tasks with past dates")
			parent.deiconify()
		else:

			# create window object
			task_window = Toplevel(self.root)

			# define window geometry and create window Frame
			self.win_geometry(300, 400, task_window)
			frm = ttk.Frame(task_window, padding=10)
			frm.grid()

			# create StringVar objects to capture user input
			new_task_type = StringVar()
			new_task_description = StringVar()
			new_task_date = StringVar()
			new_task_time = StringVar()

			# set value = to cal_deadline, either string of date passed from calendar or empty string
			new_task_date.set(cal_deadline)

			# define label and entry boxes for information
			ttk.Label(frm, text="Add a new task").grid(column=0, row=0)
			ttk.Label(frm, text="Enter what type of task").grid(column=0, row=1)
			ttk.Entry(frm, textvariable=new_task_type).grid(column=1, row=1)
			ttk.Label(frm, text="Enter a brief description of the task").grid(column=0, row=2)
			ttk.Entry(frm, textvariable=new_task_description).grid(column=1, row=2)
			ttk.Label(frm, text="Enter the task date, this is optional. Enter the date in numerical day-month-year format ie 22/07/1992").grid(column=0, row=3)
			ttk.Entry(frm, textvariable=new_task_date).grid(column=1, row=3)
			ttk.Label(frm, text="Enter the task time, this is optional but requires a date. Enter time in 24 hour format ie 20:30").grid(column=0, row=4)
			ttk.Entry(frm, textvariable=new_task_time).grid(column=1, row=4)

			# confirm button to progress to comfirming task creation pass value of StringVars as strings to confirm_add function, return to return to parent window
			ttk.Button(frm, text="Confirm", command=lambda:[task_window.withdraw(), self.confirm_add(new_task_type.get(), new_task_description.get(), new_task_date.get(), new_task_time.get(), task_window, parent)]).grid(column=0, row=5)
			ttk.Button(frm, text="Return", command=lambda:[task_window.destroy(), self.return_to_prev_window(parent)]).grid(column=1, row=5)
			
			# protocol for X button in window
			task_window.protocol("WM_DELETE_WINDOW", lambda:self.on_closing(task_window))

	
	def confirm_add(self, new_task_type: str, new_task_description: str, new_task_date: str, new_task_time: str, parent: Toplevel, grandparent: Toplevel) -> None:
		'''
		Checks user input will create valid SQL entry,
		Confirms with user that entered information is correct before adding as new DB entry.
		'''
		# if task type or description are empty strings unhide parent window and return
		if not new_task_type or not new_task_description:
			messagebox.showinfo(message="Sorry both the task type and task description are needed to create a new task.\nPlease enter values for these fields")
			parent.deiconify()
			return

		# if _Date object of string task date is past date unhide parent window and return
		deadline = self.date_clean(new_task_date)
		if deadline < datetime.now().date():
			messagebox.showinfo(message="Sorry you can't add tasks with past dates")
			parent.deiconify()
			return

		# if valid task time but no valid date unhide parent and return
		clean_time = self.time_clean(new_task_time)
		if clean_time and not deadline:
			messagebox.showinfo(message="Sorry you can't add tasks with a time but no valid date")
			parent.deiconify()
			return
		
		# if valid _Date deadline and _Time time then combine into datetime object
		elif deadline and clean_time:
			deadline = datetime.combine(deadline, clean_time)

		# if valid _Date deadline and no time combine with default time into datetime object
		elif deadline and not clean_time:
			default_time = time(0,0,0)
			deadline = datetime.combine(deadline, default_time)

		# check formatted data with user for confirmation
		confirm = messagebox.askyesno(message=f"You have entered {new_task_type} for the task type, {new_task_description} for the task description and {self.simple_date(deadline)} for the deadline. Is this correct?", title="check your info")
		if confirm:
			# create Task object
			new_task = models.Task(task_type = new_task_type, description=new_task_description, deadline=deadline, user_id=self.current_user.id)

			# add and commit to DB session
			models.session.add(new_task)
			models.session.commit()

			# destroy parent window
			parent.destroy()
			messagebox.showinfo(message="Task added!")

			# unhide grandparent window (root menu or calendar window)
			grandparent.deiconify()
		else:
			self.return_to_prev_window(parent)


	def edit_delete_task_window(self, parent: Toplevel, cal_date=None) -> None:
		'''
		Window displaying all tasks associated with current user with option to edit or delete.
		Can be accessed from root menu and calendar window, from calendar window entries filtered by passed cal_date paremeter.
		links through to edit or delete task windows.
		'''
		# create window object
		task_window = Toplevel(self.root)

		# define window geometry and create window Frame
		self.win_geometry(300, 400, task_window)
		frm = ttk.Frame(task_window, padding=10)
		frm.grid()

		ttk.Label(frm, text="Choose a task to delete").grid(column=0, row=0)
		x = 1

		# if accessed from root window display all tasks associated with current user
		if cal_date is None:
			for task in self.current_user.tasks:
				ttk.Label(frm, text=task).grid(column=0, row=x)
				ttk.Button(frm, text="Edit", command=lambda task=task:[task_window.withdraw(), self.edit_task(task, task_window, parent)]).grid(column=1, row=x)
				ttk.Button(frm, text="Delete", command=lambda task=task:[task_window.withdraw(), self.delete_task(task, task_window, parent)]).grid(column=2, row=x)
				x +=1

		# if cal_date passed from calendar window filter tasks of current user for this date
		else:
			for task in self.current_user.tasks:
				if task.deadline.date() == cal_date:
					ttk.Label(frm, text=task).grid(column=0, row=x)
					ttk.Button(frm, text="Edit", command=lambda task=task:[task_window.withdraw(), self.edit_task(task, task_window, parent)]).grid(column=1, row=x)
					ttk.Button(frm, text="Delete", command=lambda task=task:[task_window.withdraw(), self.delete_task(task, task_window, parent)]).grid(column=2, row=x)
					x +=1

		# quit buton returns to root window
		ttk.Button(frm, text="Return", command=lambda:[task_window.destroy(), self.return_to_prev_window(parent)]).grid(column=0, row=x)

		# protocol for X button in window
		task_window.protocol("WM_DELETE_WINDOW", lambda:self.on_closing(task_window))


	def delete_task(self, task: models.Task, parent: Toplevel, grandparent: Toplevel) -> None:
		'''
		Deletes task DB entry if confirmed by user then either destroying window returning to root or to edit/delete task window,
		if not confirmed unhides parent window.		
		'''
		confirm = messagebox.askyesno(message=f"You have selected '{task}' task to delete. Is this correct?", title="Delete task?")
		if confirm:
			# delete task entry and commit to session
			models.session.delete(task)
			models.session.commit()

			# destroy parent window
			parent.destroy()

			messagebox.showinfo(message="Task deleted!")

			# check for tasks with 'bad' past dates that need amending or deleting
			if self.past_date_check():
				self.amend_past_dates()
			else:
				# choice to return to amend/delete additional tasks
				menu_select = messagebox.askyesno(message="Would you like to Edit or Delete additional tasks?", title="Return to Edit/Delete menu?")
				if menu_select:
					self.edit_delete_task_window(self.root)
				else:
					# unhide grandparent (root menu or calendar window)
					grandparent.deiconify()
		else:
			self.return_to_prev_window(parent)

	
	def edit_task(self, task: models.Task, parent: Toplevel, grandparent: Toplevel) -> None:
		'''
		Window for entering infomation to edit task entry in DB, 
		infomation passed to confirm_edit_task function.
		'''
		# create window object
		task_window = Toplevel(self.root)

		# define window geometry and create window Frame
		self.win_geometry(300, 400, task_window)
		frm = ttk.Frame(task_window, padding=10)
		frm.grid()

		# create StringVar objects to capture user input/display current
		edited_task_type = StringVar()
		edited_task_description = StringVar()
		edited_task_date = StringVar()
		edited_task_time = StringVar()

		# get string format of the task's current deadline date from datetime
		current_task_date = task.deadline.date().strftime("%d/%m/%Y")

		# get string format of the task's current deadline time from datetime
		current_task_time = task.deadline.time().strftime("%H:%M")

		# define label and entry boxes for information
		ttk.Label(frm, text="Enter new values in any field you wish to edit, otherwise leave them blank").grid(column=0, row=0)
		ttk.Label(frm, text=f"Current type of task: {task.task_type}").grid(column=0, row=1)
		ttk.Entry(frm, textvariable=edited_task_type).grid(column=1, row=1)
		ttk.Label(frm, text=f"Current description: {task.description}").grid(column=0, row=2)
		ttk.Entry(frm, textvariable=edited_task_description).grid(column=1, row=2)
		ttk.Label(frm, text=f"Current date: {current_task_date}").grid(column=0, row=3)
		ttk.Entry(frm, textvariable=edited_task_date).grid(column=1, row=3)
		ttk.Label(frm, text=f"Current time: {current_task_time}").grid(column=0, row=4)
		ttk.Entry(frm, textvariable=edited_task_time).grid(column=1, row=4)		

		# confirm button to progress to comfirming task creation pass value of StringVars as strings to confirm_add function, return to return to parent window
		ttk.Button(frm, text="Confirm", command=lambda:[parent.destroy(), task_window.withdraw(), self.confirm_edit_task(edited_task_type.get(), edited_task_description.get(), edited_task_date.get(), edited_task_time.get(), task, task_window, grandparent)]).grid(column=0, row=5)
		ttk.Button(frm, text="Return", command=lambda:[task_window.destroy(), self.return_to_prev_window(parent)]).grid(column=1, row=5)

		# protocol for X button in window
		task_window.protocol("WM_DELETE_WINDOW", lambda:self.on_closing(task_window))


	def confirm_edit_task(self, edited_task_type: str, edited_task_description: str, edited_task_date: str, edited_task_time: str, task_to_edit: models.Task, parent: Toplevel, origin_window: Toplevel) -> None:# account for date -> datetime
		'''
		Edits task DB entry if confirmed by user destroying parent window and unhiding root,
		if not confirmed unhides parent window.
		'''
		# get _Date and _Time objects from string representations
		date_object = self.date_clean(edited_task_date)
		time_object = self.time_clean(edited_task_time)

		# if date object is past date unhide parent and return
		if date_object and date_object < datetime.now().date():
			messagebox.showinfo(message="Sorry you can't edit a deadline to be a past date")
			parent.deiconify()
			return
		
		# if valid _Date and _Time objects, combine into datetime object
		if date_object and time_object:
			deadline = datetime.combine(date_object, time_object)

		# if valid _Date but no _Time object combine with current task _Time into datetime object
		elif date_object and not time_object:
			task_current_deadline = task_to_edit.deadline
			deadline = datetime.combine(date_object, task_current_deadline.time())

		# if valid _Time object but no _Date object combine with current task _Date into datetime object
		elif not date_object and time_object:
			task_current_deadline = task_to_edit.deadline
			deadline = datetime.combine(task_current_deadline.date(), time_object)

		# else get current deadline datetime
		else:
			deadline = task_to_edit.deadline

		# if new task type assign it to type var if not assign current task type to var
		if edited_task_type:
			type = edited_task_type
		else:
			type = task_to_edit.task_type

		# if new task description assign it to type var if not assign current task description to var
		if edited_task_description:
			description = edited_task_description
		else:
			description = task_to_edit.description

		# confirm new values with user
		confirm = messagebox.askyesno(message=f"If you confirm this edit the new task values will be:\nTask type: {type}, Description: {description}, Deadline: {self.simple_date(deadline)}", title="Edit task?")
		if confirm:

			# assign variables as new task properties
			task_to_edit.task_type = type
			task_to_edit.description = description
			task_to_edit.deadline = deadline

			# commit to session
			models.session.commit()

			# destroy parent window
			parent.destroy()

			messagebox.showinfo(message="Task edited!")

			# check for tasks with 'bad' past dates that need amending or deleting
			if self.past_date_check():
				self.amend_past_dates()
			else:
				# unhide grandparent (root menu or calendar window)
				origin_window.deiconify()
		else:
			self.return_to_prev_window(parent)


	def amend_past_dates(self) -> None:
		'''
		Window displaying all past dates giving users option of editing task to have future date or deleting the task.
		Can call edit_task and delete_task.
		'''
		current_date = datetime.now()

		# hide root
		self.root.withdraw()

		# create window object
		task_window = Toplevel(self.root)

		# define window geometry and create window Frame
		self.win_geometry(300, 400, task_window)
		frm = ttk.Frame(task_window, padding=10)
		frm.grid()

		# iteratively create labels and buttons for each task with past date
		x = 0
		for reminder in self.current_user.tasks.filter((models.Task.deadline.isnot(None)) & (models.Task.deadline < current_date)):
			ttk.Label(frm, text=f"{reminder.description} is scheduled to have already happened would you like to delete or edit this entry?").grid(column=0, row=x)
			ttk.Button(frm, text="Edit task", command=lambda:[task_window.withdraw(), self.edit_task(reminder, task_window, self.root)]).grid(column=1, row=x)
			ttk.Button(frm, text="Delete task", command=lambda:[task_window.withdraw(), self.delete_task(reminder, task_window, self.root)]).grid(column=2, row=x)
			x +=1

		# protocol for X button in window
		task_window.protocol("WM_DELETE_WINDOW", lambda:self.on_closing(task_window))


## Functions not for task or user creation/editing/deletion ##

	def date_clean(self, date_str: str)  -> None | date:
		'''
		Takes string as arguement and iterates through 4 accepted date format trying to successfully format into a date object.
		If no format will produce valid date then returns None.
		'''
		# iterate over format strings
		for fmt in ["%d-%m-%Y", "%d.%m.%Y", "%d/%m/%Y", "%d %m %Y"]:
			# try each format execepting value error and returning upon valid date
			try:
				date_object = datetime.strptime(date_str, fmt).date()
			except ValueError:
				continue
			else:
				return date_object
		# if ValueError raised each time return None
		return None


	def time_clean(self, time_str: str) -> None | time:
		'''
		Takes string as arguement and tries to format into time object with "%H:%M" format.
		If ValueError raised return None.
		'''
		try:
			time_object = datetime.strptime(time_str, "%H:%M").time()
		except ValueError:
			return None
		else:
			return time_object


	def past_date_check(self)  -> bool:
		'''
		If self.current_user, filters user tasks for past dates.
		Returns False if no current user or bool of whether query is empty.
		'''
		if self.current_user != None:
			current_date = datetime.now()
			return (self.current_user.tasks.filter((models.Task.deadline.isnot(None)) & (models.Task.deadline < current_date))).count() != 0
		else:
			return False


	def user_assign_bad_date(self) -> None:
		'''
		Checks for past dates calling amend_past_dates if True,
		otherwise unhides root menu window.
		'''
		if self.past_date_check():
			self.amend_past_dates()
		else:
			self.root.deiconify()


	def return_to_prev_window(self, current_parent: Toplevel) -> None:
		'''
		If current_parent a window object exists, unhides this window,
		otherwise unhides root menu window.
		'''
		if current_parent:
			current_parent.deiconify()
		else:
			self.root.deiconify()


	def on_closing(self, current_window: Toplevel) -> None:
		'''
		Defines window protocol when using close X in window.
		Destroys current window and unhides root menu window.
		'''
		current_window.destroy()
		self.root.deiconify()


	def simple_date(self, deadline: datetime) -> str:
		'''
		Takes datetime as arguement and formats it into string.
		If datetime time is default 0:0:0 then only format date information into string.
		returns string of datetime or "No deadline" if deadline parameter None.
		'''
		# for DB entries with None deadline
		if not deadline:
			return "No deadline"
		if deadline.time() == time(0,0,0):
			deadline = deadline.strftime("%d/%m/%Y")
		else:
			deadline = deadline.strftime("%d/%m/%Y :: %H:%M")
		return deadline

	
	def assign_current_user(self, user: models.User) -> None:
		'''
		Takes models.User sqlalchemy class as parameter and assigns it as current user,
		also updating root menu windows displayed current user.
		'''
		self.current_user = user
		self.current_profile_name.set(self.current_user.user_name)
		

	def deselect_current_user(self) -> None:
		'''
		Deselects current user and sets profile name to none.
		'''
		self.current_user = None
		self.current_profile_name.set("None")


	def win_geometry(self, width: int, height: int, window: Toplevel) -> None:
		'''
		Takes: ints of width and height and a window object as arguements.
		Uses ints to calculate window object size and position relative to root window.
		'''
		sw = self.root.winfo_screenwidth()
		sh = self.root.winfo_screenheight()
		x = (sw/2) - (width/2)
		y = (sh/2) - (height/2)
		window.geometry("+%d+%d" % (x, y))


if __name__ == "__main__":
	app = OrganiserApp()
	app.app_running()