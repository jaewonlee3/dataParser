import os
import git



def GitPull(AppName, SgName) :
    ServerDir = "/data/git"
    ServerName = "PO"
    path = os.path.join(ServerDir,ServerName, AppName, SgName)
    g = git.Git(path)
    #feature로 pull 하겠다는 내용인데, 현재 인사팀의 경우는 develop branch로 개발중이다.
    #2-3팀 정책에 의해 feature로 개발하기로 하였으므로, 인사팀도 추후에 변경할 것 같다..
    g.pull('origin', 'feature')
    return 0

def PathSearch(AppName, SgName) :
    #아래의 data/git은 서버상에 저장될 top, po 파일들을 모아논 주소이다.
    #서버 이전시 바꿔줄 필요가 있다.
    ServerDir = "/data/git"
    ServerName = "PO"
    path = os.path.join(ServerDir,ServerName, AppName, SgName,"META-INF")
    file_list = os.listdir(path)
    file_list_py = [file for file in file_list if file.endswith("servicegroup.xml")]
    fileNumber = len(file_list_py)
    if (fileNumber != 1) :
        print("서비스그룹이 지정된 경로에 있지 않습니다. PO 빌드가 제대로 되었는지 확인해 주세요.")
    else :
        SgPath = os.path.join(path, file_list_py[0])
        return SgPath

if __name__ == "__main__" :
    AppName = input("Application Name : ")
    SgName = input("Service Group Name : ")
    GitPullUse = input("최신branch로 pull 하시겠습니까? :(Y/N) ")

    if (GitPullUse == "Y") :
        GitPull(AppName, SgName)
    SgPath = PathSearch(AppName, SgName)
    print(SgPath)
