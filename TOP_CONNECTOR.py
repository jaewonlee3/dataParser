import os
import git

def GitPull(AppName) :
    ServerDir = "/data/git"
    ServerName = "TOP"
    path = os.path.join(ServerDir, ServerName, AppName)
    g = git.Git(path)
    g.pull('origin', 'feature')
    return 0

def PathSearch(AppName) :
    ServerDir = "/data/git"
    ServerName = "TOP"
    path = os.path.join(ServerDir, ServerName, AppName)
    return path

def TopXmlConnector(AppName) :
    GitPull(AppName)
    Output = PathSearch(AppName)
    return Output
