#!/bin/python
import sys
import os
import getopt
import paramiko
import time
import subprocess
import re



def scan(vmListFile,server,vc):

	vmList = readList(vmListFile)
	print vmList
	vmOnEsxiList = getVm(server,vc=vc)
	print vmOnEsxiList

	listFile = '%s-%s' % (vmListFile,server)
	with open(listFile, 'w+') as f:
		f.truncate()
		for vm in vmList:
			if vm in vmOnEsxiList:
				#vm = '%s\n' % (vm)
				f.write('%s\n' % (vm))

def getVm(server,user='root',vc='3.5'):	

	getallvms = []
	
	if vc == '3.5':
		getallvmsCMD = "vmware-vim-cmd vmsvc/getallvms | sed '1d' |awk  '{print $2}' |sort"
	else:
		getallvmsCMD = "vim-cmd vmsvc/getallvms | sed '1d' |awk  '{print $2}' |sort"
	print getallvmsCMD

	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	#keyPath = ''
	#pkey = paramiko.from_private_key_file(keyPath)
	#ssh.connect(hostname=server,username=user,pkey=pkey)
	ssh.connect(server,username=user)
	ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(getallvmsCMD)

	for line in ssh_stdout.readlines():
		getallvms.append(line.strip())
	getallvms = filter(None, getallvms)	
	ssh.close()

	return getallvms

def runCmd(server,script,user='root'):
	
	print script
	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	#keyPath = ''
	#pkey = paramiko.from_private_key_file(keyPath)
	#ssh.connect(hostname=server,username=user,pkey=pkey)
	ssh.connect(server,username=user)
	ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(script)
	print ssh_stdout.read()
	print ssh_stderr.read()
	#chan = ssh.get_transport().open_session()
	#chan.exec_command(script)
	#errcode = chan.recv_exit_status()
	#print errcode 
	errcode = 0
	ssh.close()

	return errcode

def toAllLog(errcode, logName, logPath):
    
    mesg = {
    	0 : lambda x : '%s: all vms backup SUCCESSED' % (x),
    	4 : lambda x : '%s: some vms backup FAILED' % (x),
    	6 : lambda x : '%s: all vms backup FAILED' % (x),
    }.get(errcode, lambda x : '%s: SOMETHING ERR' % (x))(logName)

    toLog(mesg, logPath)

def toLog(mesg, logPath):
	
	nowTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
	mesg = '%s -- %s' % (nowTime, mesg)
	
	with open(logPath, 'a')  as f:
		f.write('%s\n' % (mesg))
		
def readList(file):
	
	ls = []
	with open(file, "r") as f:
		for line in f.readlines():
			ls.append(line.strip())
	#ls = filter(None, ls)
	#ls = filter(lambda x: None if re.match('^#',x) else x,ls)
	ls = filter(lambda x: not re.match('^#',x) and x,ls)		
	return ls

def bash(cmd):
	pstat = subprocess.Popen(cmd,shell=True)
	return pstat

def echoHelp():
	print "-s      with 'Server ip' (string) or 'Server ip,Server ip' more"
	print "-b      with 'Backup name' (string)"
	print "-r      with 'Rotation count' (int) default: 7"
	print "-m      with 'Linux mount point' (string) default: /backup"
	print "-d      with 'Datastore name' (string) default: backup"
	print "-V      ESXI 5.5 6.0 6.5 to enable"
	print "-h      Echo help"

def main():

	servers = []
	backupName = ''
	rotation = 7
	mountPoint = '/backup'
	datastore = 'backup'
	vc = '3.5'

	try:
		opts,args = getopt.getopt(sys.argv[1:],"hVs:b:r:m:d:")
	except getopt.GetoptError: 
		echoHelp()
		sys.exit(1)	

	for opt, value in opts: 
		if opt == "-s":
			servers = value.split(',');
		
		elif opt == "-b": 
			backupName = value

		elif opt == '-r':	
			rotation = value

		elif opt == '-m':
			mountPoint = value

		elif opt == '-d':
			datastore = value

		elif opt == '-V':
			vc = '6.0'
		
		elif opt == '-h':
			echoHelp()
			sys.exit(0)		

	if not servers:
		print 'input "servers ip" with -s'
		print 'ex: 10.10.32.10  or  10.10.32.61,10.10.32.62'
		sys.exit(1)
	elif not backupName:
		print 'input "backup name" with -b'	
		sys.exit(1)

	#define var
	day = 30
	now = time.localtime() 
	nowDate = time.strftime("%Y-%m-%d", now)
	#nowTime = time.strftime("%Y-%m-%d %H:%M:%S", now)

	#BSWorkDir = '/backup/ghettoVCB'
	#workDir = '/vmfs/volumes/backup/ghettoVCB'
	#backupDir = '/vmfs/volumes/backup/%s' % ( backupName )
	BSWorkDir = '%s/ghettoVCB' % ( mountPoint )
	workDir = '/vmfs/volumes/%s/ghettoVCB' % ( datastore )
	backupDir = '/vmfs/volumes/%s/%s' % ( datastore, backupName )
	webDir = 'web/servers/%s' % ( backupName )

	cmd = 'ghettoVCB.sh'
	conf = 'ghettoVCB.conf'
	backupList = 'vm_list/%s.list' % ( backupName )
	log = 'log/%s.log' % ( backupName )
	allLog = 'log/ghettoVCB.log'
	vmListFile = '%s/%s' % (BSWorkDir, backupList)
	dname = '%s/%s' % (BSWorkDir, webDir)
	flag = False if len(servers) == 1 else True
	
	if not  os.path.isfile( vmListFile ):
		print 'create  file  %s' % vmListFile
		print 'input vm name in to the file'
		open(vmListFile, 'a').close()
		os.utime(vmListFile, None)
		sys.exit(1)	
	elif not  os.path.isdir( dname ):
		os.makedirs(dname,0755 )

	for server in servers:
		
		if flag:
			scan(vmListFile, server, vc)
			listFile = '%s-%s' % (backupList, server)
			logName = '%s-%s' % (backupName, server)	
		else:
			listFile = 	backupList
			logName = backupName
		
		script = '\
			export BACKUPNAME={backupName};\
			export ROTATION_COUNT={rotation};\
			export BACKUP_DIR={backupDir};\
			/bin/sh  {workDir}/{cmd} -f  {workDir}/{listFile} -g  {workDir}/{conf} -l {workDir}/{log} -L {workDir}/{webDir}/{backupName}-{nowDate}.html;\
			'.format(backupName=backupName, rotation=rotation, backupDir=backupDir, workDir=workDir, cmd=cmd, listFile=listFile, conf=conf, log=log, webDir=webDir, nowDate=nowDate)

		#script = script.format(backupName=backupName, rotation=rotation, backupDir=backupDir, workDir=workDir, cmd=cmd, listFile=listFile, conf=conf, log=log, webDir=webDir, nowDate=nowDate)

		#sys.exit()
		errcode = runCmd(server, script)
		#logPath = '%s/%s' % (BSWorkDir, allLog)
		#toAllLog(errcode, logName, logPath)

	if flag:

		htmlfile = '%s/%s/%s-%s.html' % (BSWorkDir, webDir, backupName, nowDate)
		#htmlTmep = '<tr class="danger"><td>{time}</td><td>{backupName}</td><td>{vm}</td><td>{size}</td><td>{status}</td></tr>\n'
		vmBackupList = []

		vmList = readList(vmListFile)
		print vmList
		
		for server in servers:
			listFile = '%s/%s-%s' % (BSWorkDir, backupList, server)
			vmBackupList += readList(listFile)
		print vmBackupList

		for vm in vmList:
			if vm not in vmBackupList:
				html = '<tr class="danger"><td>{time}</td><td>{backupName}</td><td>{vm}</td><td>{size}</td><td>{status}</td></tr>'\
				.format(time=time.strftime("%Y-%m-%d %H:%M:%S", now), backupName=backupName, vm=vm, size='null', status='FAILED')
				print html
				with open(htmlfile, 'a') as f:
					f.write('%s\n' % (html))

	findcCmd = 'find %s/%s  -type f -mtime +%d -exec rm -rf { } \\;' % (BSWorkDir, webDir, day)
	print findcCmd
	#pstat = subprocess.Popen(findcCmd,shell=True)
	pstat = bash(findcCmd)
		
	rsyncCmd ='/bin/rsync  -av --delete %s/web/ %s' % (BSWorkDir, '/var/www/html')
	print rsyncCmd
	#pstat = subprocess.Popen(rsyncCmd,shell=True)
	pstat = bash(rsyncCmd)


if __name__ == '__main__':
	main()





