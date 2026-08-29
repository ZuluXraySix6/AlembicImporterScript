NO FAIR USAGE. Use it as you like it. IT'S FREE.

Making the Shelf Tool
1. Make a shelf Tool.
2. Save the shelf tool.
3. Goto the Script Tab. Insert this code below :

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

This will tie the tool to Houdini Session. So, clicking the tool multiple times wont create multiple instances.

4. Save the Shelf Tool Again.

Saving the Python Files : 
1. Create a folder "python3.9libs" or "python3.11libs" depending on your Houdini version and place it inside the Documents/houdini20.5 or houdini21.0 or houdini22.0 folder.
2. After all this. Just Click on the Shelf button u have created and you will have a WORKING UI.
3. Thanks.

![image](https://github.com/ZuluXraySix6/AlembicImporterScript/assets/108427116/fa17c769-7fbf-496c-986b-7c8bffced654)


