import os

if __name__ == "__main__" :

    path = "/data/git"
    FolderList = os.listdir(path)

    for i in range(len(FolderList)) :
        ServiceName = FolderList[i]
        print('Service Name : %s' % (ServiceName))
        ServicePath = os.path.join(path, ServiceName)
        AppList = os.listdir(ServicePath)
        for j in range(len(AppList)) :
            print('     Application Name : %s' % (AppList[j]))
            AppPath = os.path.join(ServicePath, AppList[j])
            if (ServiceName == 'PO') :
                SgNameList = os.listdir(AppPath)
                for k in range(len(SgNameList)) :
                    print('         ServiceGroup Name : %s' % (SgNameList[k]))
