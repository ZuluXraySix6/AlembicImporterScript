#DONT CREATE A PYTHON FILE outta this.
#This is for the Shelf Tool Script Tab ONLY
import importlib as il
import abcimporter as ai
import hou

il.reload(ai)

# Check whether the window already exists
if hasattr(hou.session, "abcImporterWindow"):
    try:
        if hou.session.abcImporterWindow.isVisible():
            hou.session.abcImporterWindow.raise_()
            hou.session.abcImporterWindow.activateWindow()
        else:
            hou.session.abcImporterWindow.show()
    except:
        hou.session.abcImporterWindow = ai.MainWindow()
        hou.session.abcImporterWindow.show()
else:
    hou.session.abcImporterWindow = ai.MainWindow()
    hou.session.abcImporterWindow.show()
