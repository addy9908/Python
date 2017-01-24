#   'reName deconvoluted tif V5'
#   Author: Zengyou
#   Date: 01/13/2017
#   Purpose: Autoquant will add '10_' to the filename after 3D deconvolution.
#           We need to remove '10_' for loading these file in bob's mapmanager
# 'Will remove 10_ from the name of deconvoluted tif'
#   20170124: add new function for changing aligned folder name from _channels to _aligned
#               default deconvolution folder name will be <session>_out under root

import os, time
import shutil
import Tkinter, tkFileDialog

def renameOneFolder(src,startwith, endwith):
    if not os.path.isdir(src):
        print '\nERROR: renameOneFolder() did not find folder: ' + src + '\n'
    else:
        #leave a note with date modified
        txtFile = os.path.join(src,'rename_deconvolution.txt')
        f = open(txtFile, 'w')    #w for creating a new txt
        msg = 'modified time:' + time.strftime("%H:%M:%S")
        f.write(msg)
        f.close()
        print '     Create a note txt'

        #deconTifs = [file for file in os.listdir(src) if file.startswith(startwith) and file.endswith(endwith)]
        deconTifs = [file for file in os.listdir(src) if file.startswith(startwith)] #change all decon file names
        if len(deconTifs)<1:
            print "     -----%s: No more tif startswith %s" %(os.path.basename(src), startwith)
        else:
            for i, file in enumerate(deconTifs):
                filePath = os.path.join(src, file)
                newFilePath = os.path.join(src, file[3:])   #remove '10_'
                os.rename(filePath, newFilePath)
                print "     Finish %d of %d files" %(i+1, len(deconTifs))

def runOneMouse(mouseDir):
    mouseID = os.path.basename(mouseDir)

    ## change the name of aligned folder to <session>_aligned
    alignFolder = mouseID + '_channels'
    new_alignFolder = mouseID + '_aligned'
    alignPath = os.path.join(mouseDir, alignFolder)
    new_alignPath = os.path.join(mouseDir, new_alignFolder)
    if os.path.isdir(alignPath):
        os.rename(alignPath,new_alignPath)
        print "     -----Finish changing aligned folder: %s" % mouseID
    # end of changing aligned folder

    ## move and rename folder: _align/deconvolution to root as <session>_out
    deconPath = os.path.join(new_alignPath,'deconvolution')
    outputFolder = mouseID + '_out'
    outputPath = os.path.join(mouseDir, outputFolder)
    if os.path.isdir(deconPath) and not os.path.isdir(outputPath):
       os.rename(deconPath,outputPath)
   # end of move and rename folder

   # rename deconvoluted tif
    if os.path.isdir(outputPath):
        renameOneFolder(outputPath,'10_','tif')
        print "     -----Finish changing file name: %s" %mouseID
    else:
        print "     -----No deconvoluted tif for mouse: %s" %mouseID
   # end of rename file

def runOneDate(dateDir):
    mouseDirs = [file for file in os.listdir(dateDir) if os.path.isdir(os.path.join(dateDir,file))]
    numMouse = len(mouseDirs)
    dateInfo = os.path.basename(dateDir)
    print "     Number of mouse imaged in %s is %d" %(dateInfo,numMouse)
    ind = 1
    for mouseID in mouseDirs:
        mouseName = mouseID.split('_')[1]
        print "     *Running mouse %s (%d/%d)" %(mouseName, ind,numMouse)
        mouseFolder = os.path.join(dateDir,mouseID)
        runOneMouse(mouseFolder)
        ind += 1

def runOneMonth(monthDir):
    dateDirs = [file for file in os.listdir(monthDir) if os.path.isdir(os.path.join(monthDir,file))]
    numDates = len(dateDirs)
    monthInfo = os.path.basename(monthDir)
    print " Number of dates imaged in month %s is %d" %(monthInfo,numDates)
    ind = 1
    for imageDate in dateDirs:
        print "*Running imaging date %s (%d/%d)" %(imageDate, ind,numDates)
        dateDir = os.path.join(monthDir,imageDate)
        runOneDate(dateDir)
        ind += 1


if __name__ == '__main__':
    print "================================================="
    print 'reName deconvoluted tif V5'
    print '     Will remove 10_ from the name of deconvoluted tif'
    print '================================================='
    root = Tkinter.Tk()
    root.withdraw()
    dataPath = "G:\ZY\imaging_2p\Sutter"
    srcDir = tkFileDialog.askdirectory(parent=root,initialdir=dataPath,title='Please select a source directory')
    if len(srcDir ) > 0:
        print "The Source folder is: %s" % srcDir
        if len(os.path.basename(srcDir)) == 8:
            runOneDate(srcDir)
            print 'Finish runOneDate()'
        if len(os.path.basename(srcDir)) < 3:
            runOneMonth(srcDir)
            print 'Finish runOneMonth()'
