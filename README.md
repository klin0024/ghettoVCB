# Overview
![image](img/overview.JPG?raw=true "Overview") <br />
<br />
# Architecture
![image](img/architecture.JPG?raw=true "Architecture") <br />
<br />
## 使用說明
### 1. 準備一台NAS作為備份儲存空間
### 2. 將Esx/Esxi和Centos掛載NAS的儲存空間
Esx/Esxi Datastore名稱為 backup <br />
Centos 掛載點為 /backup <br />
### 3. 將Centos和Esx/Esxi交換金鑰
$ ssh-copy-id root@< ESXI IP > <br />
### 4. 登入Esx/Esxi,將公鑰輸入到特定檔案
\# cat .ssh/authorized_keys >> /etc/ssh/keys-root/authorized_keys
### 5. 切換到/backup,執行git clone
$ git clone https://github.com/klin0024/ghettoVCB.git
### 6. backup 目錄下有 backup.py,是備份執行檔
$ python backup/backup.py –s < IP Address > –b < Backup Name >
### 7. 第一次執行,會在 vm_list目錄下建立清單,編輯VM清單
$ vi vm_list/<Backup Name>.list <br />
VM-1 <br />
\#VM-2 <br />	
### 8. 再次執行VM備份
$ python backup/backup.py –s < IP Address > –b < Backup Name >
### 9. 備份完成後, Dashboard會顯示備份狀態
![image](img/dashboard.JPG?raw=true "Dashboard") <br />


### backup.py操作說明:
-s with 'Server ip' (string) or 'Server ip,Server ip' more <br />
-b with 'Backup name' (string) <br />
-r with 'Rotation count' (int) default: 7 <br />
-m with 'Linux mount point' (string) default: /backup <br />
-d with 'Datastore name' (string) default: backup <br />
-V ESXI 5.5 6.0 6.5 to enable <br />
-h help <br />