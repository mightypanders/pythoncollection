import sys
import os
import shutil

def makeFolderList(pathtofolder):
	folder = next(os.walk(pathtofolder))
	return folder

def getFileExtension(file):
	return (os.path.splitext(file)[1]).replace(".","").lower()

def main():
	file = sys.argv[0]
	pathname = os.path.dirname(file)
	folderContent = makeFolderList(pathname)
	dirs,allfiles = folderContent[1],folderContent[2]
	extlist = []
	for file in allfiles:
		ext = getFileExtension(file)
		if ext not in extlist and ext is not "" and ext is not '':
			extlist.append(ext)
	for ext in extlist:
		if ext not in dirs:
			os.mkdir(pathname+"/"+ext,777)
	dirs = makeFolderList(pathname)[1]
	for file in allfiles:
		if file.__contains__(sys.argv[0]):
			continue
		ext = getFileExtension(file)
		abspath = os.path.abspath(file)
		dirpath = os.path.dirname(abspath)+"/"+ext+"/"+file
		if ext in dirs:
			newpath = shutil.move(abspath,dirpath)
			print(newpath)

if __name__ == '__main__':
	main()
