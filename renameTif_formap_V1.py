#   'reName deconvoluted tif V5'
#   Author: Zengyou
#   Date: 01/13/2017
#   Purpose: Autoquant will add '10_' to the filename after 3D deconvolution.
#           We need to remove '10_' for loading these file in bob's mapmanager
# 'Will remove 10_ from the name of deconvoluted tif'
#   20170124: add new function for changing aligned folder name from _channels to _aligned (ignor)
#               default deconvolution folder name will be <session>_raw under root
# type folder name as "F67,F68"

import os
import time
import shutil
import Tkinter, tkFileDialog

#rename file under folder start with ""
def renameOneFolder(src,startwith, endwith=''):
    if not os.path.isdir(src):
        print '\nERROR: renameOneFolder() did not find folder: ' + src + '\n'
    else:
        #deconTifs = [file for file in os.listdir(src) if file.startswith(startwith) and file.endswith(endwith)]
        deconTifs = [file for file in os.listdir(src) if file.startswith(startwith)] #change all decon file names
        startN = len(startwith) #remove first N letter
        #could add: endN = len(endwith) then file[startN:len(file)-endN]
        if len(deconTifs)<1:
            print "     -----%s: No more tif startswith %s" %(os.path.basename(src), startwith)
        else:
            for i, file in enumerate(deconTifs):
                filePath = os.path.join(src, file)
                newFilePath = os.path.join(src, file[startN:])   #remove '10_'
                if not os.path.isfile(newFilePath):
                    os.rename(filePath, newFilePath)
                    print "     Finish %d of %d files" %(i+1, len(deconTifs))
                else:
                    print "     Potential duplicate file (%d): %s" %(i+1, file)
        #leave a note with date modified
        txtFile = os.path.join(src,'rename_deconvolution.txt')
        f = open(txtFile, 'w')    #w for creating a new txt
        msg = 'Modified: ' + time.strftime("%a, %b-%d-%Y, %H:%M:%S",time.gmtime())
        f.write(msg)
        f.close()
        print '     Create a note txt'

if __name__ == '__main__':
    print "================================================="
    print "reName map's deconvoluted tif V1: 20170323"
    print '     Will remove 10_ from the name of deconvoluted tif'
    print '================================================='
    mapPath = "G:/ZY/MapManager3"
    mapNames = tuple(raw_input("list the mapName initial sep = ',' (leave empty for all):").split(','))   #enter will do all
    mapFolders = [f for f in os.listdir(mapPath) if f.startswith(mapNames) and os.path.isdir(os.path.join(mapPath,f))]
    if len(mapFolders ) > 0:
        print "The Number of folder: " + str(len(mapFolders))
        srcs = [mapPath + '/' + f + '/raw/raw_userRaw' for f in mapFolders]
        for src in srcs:
            print src
            renameOneFolder(src, startwith ='10_')
    print "Done all"