@echo off
REM 声明采用UTF-8编码chcp 65001
chcp 65001
@REM pipenv shell
pipenv run echo  "开始打包！"
pipenv run pyinstaller.exe -F -w .\main.py -i .\css\HBDC.ico
pipenv run move /Y .\dist\main.exe .\main.exe
pipenv run rename .\main.exe 舞曲列表生成器.exe
pipenv run del main.spec
pipenv run rmdir /s/q dist
@REM pipenv run rmdir /s/q build   # 删除build文件夹f，不删除可以提高打包效率
pipenv run echo "打包结束！"
pause