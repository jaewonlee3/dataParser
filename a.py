from git import Repo

if __name__ == '__main__' :

    USER_NAME = input('유저 아이디를 입력해주세요 : ')
    PASSWORD = input('비밀번호를 입력해주세요 : ')

    HTTPS_REMOTE_URL = 'http://' + USER_NAME + ':' + PASSWORD + '@' + '192.168.155.77:9900/HR/HR_PO.git'
    DEST_NAME = '/data/git/HR'
    cloned_repo = Repo.clone_from(HTTPS_REMOTE_URL, DEST_NAME, branch='develop')
