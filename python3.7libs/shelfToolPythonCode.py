#DONT CREATE A PYTHON FILE outta this.
#This is for the Shelf Tool Script Tab ONLY
import importlib as il
import abcimporter as ai
import hou

il.reload(ai)

try:
    hou.session.abcImporterWindow.close()
    hou.session.abcImporterWindow.deleteLater()
except:
    pass

hou.session.abcImporterWindow = ai.MainWindow()
hou.session.abcImporterWindow.show()
