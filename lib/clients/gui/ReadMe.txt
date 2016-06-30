By convention I made most of the GUI components either 400x300 or 400x150.
The procedure I follow when creating a GUI and incorporating it into a client is:

	1) Use QtDesigner to create the GUI

	2) Name the input and display objects so they are easy to reference

	3) Edit the "ui to py convert.bat" file to perform the appropriate code generation.
	I have the output code written as "gui.py" as default, to be later renamed, so it
	doesn't overwrite any existing files.

	4) Open up the output .py file and make the following changes:
		- Change class name "Ui_Form" to a name describing the GUI
		- Change the inherited class to QtGui.QWidget
		- Delete the "Form" inputs in the function definitions
		- Delete the "Form" input in the self.retranslateUi() call under .setupUI()
		definition
		- Add the line "Form = self" to beginning of both the .setupUi() and
		.retranslateUi() definitions
	The reason for these changes is to change the class into an inheritable QWidget
	object.  That way, all you have to do is instantiate it, and call the function
	.setupUi() and it will set itself up (you will still need to call .show() to
	display it).  Otherwise, you end up having to instantiate more than one object in
	order to generate the widget.

	5) This class can then be imported and used in other code via the command:
	"from barium.lib.clients.gui.<file_name> import <class>" (remember, __init__.py
	files are required to exist in folders in order for classes to be imported in this
	way).  This is desired over extensive modification of the actual GUI code, because
	it allows us to continue to us QtDesigner to make any further changes to the GUI.

	6) Write a client that establishes the Signal and Slot connections between the GUI
	objects and functions.  Ideally, the client will
		- Perform any necessary asynchronous connections to LabRAD
		- Run the desired servers from the node server
		- Instantiate the desired GUI objects
		- Define the functions to be used as slots
		- Perform the Signal/Slot connections
		- Orient, embedd, modify, and display the GUI objects
	This is where the Qt documentation comes in handy (i.e. look up "QPushButton" to
	see its signals, functions, and parameters)

In short, I have the following client production scheme:
(QtDesigner) --> GUI --> (p4uic) --> GUI Class
(TextEditor) --> Client
and the following user interface scheme:
User Input --> (GUI Object) --> Signal --> (Slot on Client) --> Performs Tasks/Calls Server
Functions/Changes GUI Displays/Etc.

- Calvin He