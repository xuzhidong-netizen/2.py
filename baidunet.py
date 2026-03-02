import requests
import json
from urllib.parse import urlencode
import os
import configparser
import hashlib
import time
from song_info import is_number


def jprint(obj):
    # create bai formatted string of the Python JSON object
    out = json.dumps(obj, sort_keys=True, indent=4, ensure_ascii=False)
    return out


def get_files_md5(dir_path):
    # 获取 dir_path 路径下的所有文件的 路径paths 和 MD5值md5s
    paths = []
    md5s = []
    for file_name in os.listdir(dir_path):
        path = os.path.join(dir_path, file_name)
        if not os.path.isdir(path) and not file_name.startswith('.'):
            md5 = get_file_md5(path)
            paths.append(path)
            md5s.append(md5)
    return paths, md5s


def get_file_md5(file_name):
    # 获取 file_name 路径下的MD5值
    m = hashlib.md5()  # 创建md5对象
    with open(file_name, 'rb') as fobj:
        # while True:
        #     data = fobj.read(4096)
        #     if not data:
        #         break
        # m.update(data)  # 更新md5对象
        data = fobj.read()
        m.update(data)  # 更新md5对象
    return m.hexdigest()  # 返回md5对象


def get_slice_md5(file_name):
    # 获取 file_name 路径下的前256kB片段的MD5值
    m = hashlib.md5()
    with open(file_name, 'rb') as fobj:
        data = fobj.read(256 * 1024)
        m.update(data)
    return m.hexdigest()


def get_str_md5(content):
    # 获取 字符串content 的MD5值，content要求为 UTF-8 编码 'how to use md5 in hashlib?'.encode('utf-8')
    m = hashlib.md5(content)  # 创建md5对象
    return m.hexdigest()


def split(fromfile, todir='.\\out\\', chunksize=int(4)):
    # 文件切片程序
    chunksize = chunksize * 1024 * 1024  # 将 单位MB 转换为 单位B
    if not os.path.exists(todir):  # 检查 todir 路径是否存在，若不存在则创建路径，若存在则删除所有文件
        os.mkdir(todir)
    else:
        for fname in os.listdir(todir):
            os.remove(os.path.join(todir, fname))

    paths = []  # 记录分片文件的路径
    partnum = 0  # 记录总分片数
    inputfile = open(fromfile, 'rb')  # 以二进制读模式打开 fromfile
    file_name = os.path.basename(fromfile)  # 获取文件名
    while True:
        chunk = inputfile.read(chunksize)  # 从 inputfile 中读取 chunksize 字节的数据
        if not chunk:  # 检查数据是否为空
            break
        partnum += 1
        if os.path.getsize(fromfile) <= chunksize:
            filename = os.path.join(todir, file_name)  # 分片文件名为 原始名.partxxxx的形式
        else:
            filename = os.path.join(todir, ('%s.part%04d' % (file_name, partnum)))  # 分片文件名为 原始名.partxxxx的形式
        paths.append(filename)
        fileobj = open(filename, 'wb')  # 新建分片文件
        fileobj.write(chunk)  # 写入分片文件
        fileobj.close()
    return paths


class BaiduNet:
    refresh_token = None
    access_token = None
    appKey = None
    secretKey = None
    expires_in = None
    get_time = None
    vip_type = None
    name = None

    # vip_type = None

    # signKey = None

    def __init__(self, appKey, secretKey):
        self.appKey = appKey
        self.secretKey = secretKey
        self.read_token()
        self.get_token()


    def test_connection(self):
        try:
            self.get_info()
            return [True]
        except Exception as e:
            url_code = 'http://openapi.baidu.com/oauth/2.0/authorize?response_type=token&client_id=' + self.appKey + '&redirect_uri=oob&scope=basic,netdisk'
            return [False, 'access_token 已失效', url_code]

    def get_access_token(self, url):
        self.access_token = url[url.find('access_token=') + 13:url.find('&session_secret=&session_key=')]
        self.write_token()

    def read_token(self, file_path='./token.ini'):
        # 从 file_path 路径的 ini 文件中读取 token
        config = configparser.ConfigParser()  # 类实例化
        config.read(file_path)
        self.refresh_token = config['token']['refresh']
        self.access_token = config['token']['access']
        return True

    def write_token(self, file_path='./token.ini'):
        # 将 token 写入 file_path 路径的 ini 文件中
        config = configparser.ConfigParser()  # 类实例化
        config.read(file_path)
        config.set('token', 'refresh', self.refresh_token)
        config.set('token', 'access', self.access_token)
        config.write(open(file_path, 'w'))
        return True

    def get_token(self):
        # 根据 refresh_token 获取 access_token， 如果无法获取则弹出网站，申请获取 授权码
        # url = 'https://openapi.baidu.com/oauth/2.0/token?'
        # query = {
        #     'grant_type': 'refresh_token',
        #     'refresh_token': self.refresh_token,
        #     'client_id': self.appKey,
        #     'client_secret': self.secretKey
        # }
        # payload = {}
        # files = {}
        # headers = {
        #     'User-Agent': 'pan.baidu.com'
        # }
        # url = url + urlencode(query)
        # # print(url)
        # try:
        #     resp = requests.request("GET", url, headers=headers, data=payload, files=files)
        #     text_dict = json.loads(resp.text)
        #     # print(text_dict)
        #     self.refresh_token = text_dict['refresh_token']
        #     self.access_token = text_dict['access_token']
        # except Exception as error:
        #     print('access_token 获取失败')  # 把错误信息打印出来
        #     query_code = {
        #         'response_type': 'code',
        #         'client_id': self.appKey,
        #         'redirect_uri': 'oob',
        #         'scope': 'basic,netdisk'
        #     }
        #     url_code = 'http://openapi.baidu.com/oauth/2.0/authorize?' + urlencode(query_code)
        #     print('请点击下面的链接获取百度网盘授权码')
        #     print(url_code)
        #     code = input('输入授权码：')
        #     query_token = {
        #         'grant_type': 'authorization_code',
        #         'code': code,
        #         'client_id': self.appKey,
        #         'client_secret': self.secretKey,
        #         'redirect_uri': 'oob',
        #     }
        #     url_token = 'https://openapi.baidu.com/oauth/2.0/token?' + urlencode(query_token)
        #     # print(url_token)
        #     resp = requests.request("GET", url_token, headers=headers, data=payload, files=files)
        #     text_dict = json.loads(resp.text)
        #     # print(text_dict)
        #     self.refresh_token = text_dict['refresh_token']
        #     self.access_token = text_dict['access_token']
        # self.write_token()
        return True

    def get_info(self):
        self.get_token()
        url0 = "https://pan.baidu.com/rest/2.0/xpan/nas?"
        query = {'method': 'uinfo',
                 'access_token': self.access_token
                 }
        payload = {}
        url = url0 + urlencode(query)
        resp = requests.request("GET", url, data=payload)
        res = json.loads(resp.text)
        self.name = res['baidu_name']
        self.vip_type = res['vip_type']
        return res

    def get_list(self, path, category='2', recursion='1', ext='', start='0', limit='1000', order='time', desc='1'):
        # 查询目录path下的指定类型category文件信息
        # 由于目前没有舞曲类型有1000首曲子，所以不进行递归
        self.get_token()
        url0 = "https://pan.baidu.com/rest/2.0/xpan/multimedia?"
        query = {
            'method': 'categorylist',
            'access_token': self.access_token,  # 接口鉴权参数
            'category': category,  # 文件类型，1 视频、2 音频、3 图片、4 文档、5 应用、6 其他、7 种子 多个category使用英文逗号分隔，示例：3,4
            'parent_path': path,  # 目录名称，为空时，parent_path = "/" && recursion = 1
            'recursion': recursion,  # 是否需要递归，0 不递归、1 递归
            'ext': ext,  # 需要的文件格式，多个格式以英文逗号分隔，示例: txt,epub，默认为category下所有格式
            'start': start,  # 查询起点
            'limit': limit,  # 查询数目，最大1000，默认1000
            'order': order,  # 排序字段：time按修改时间排序，name按文件名称排序，size按文件大小排序，默认为time
            'desc': desc  # 0为升序，1为降序，默认为1
        }
        payload = {}
        files = {}
        headers = {
            'User-Agent': 'pan.baidu.com'
        }
        url = url0 + urlencode(query)
        try:
            resp = requests.request("GET", url, headers=headers, data=payload, files=files)
            resp_dict = json.loads(resp.text)
            # print(resp_dict)
            info = []
            for file in resp_dict['list']:
                # print(file)
                info.append(FileInfo(file))
            return info
        except Exception as error:
            print("获取列表失败")  # 把错误信息打印出来
            return error

    def search_file(self, key, path='/HBDC舞曲库', recursion='1', num='1000', web='0'):
        # https://pan.baidu.com/union/doc/zksg0sb9z
        self.get_token()
        url0 = "https://pan.baidu.com/rest/2.0/xpan/file?"
        query = {
            'method': 'search',
            'access_token': self.access_token,  # 接口鉴权参数
            'key': key,  # 搜索关键字
            'dir': path,  # 搜索目录，默认根目录
            'recursion': recursion,  # 是否需要递归，0 不递归、1 递归
            'num': num,  # 每页条目数，默认为1000，最大值为1000
            'category': 2,  # 文件类型为音频
            'web': web  # 默认0，为1时返回缩略图信息
        }
        payload = {}
        files = {}
        headers = {
            'User-Agent': 'pan.baidu.com'
        }
        url = url0 + urlencode(query)
        # print(url)
        try:
            while True:
                resp = requests.request("GET", url, headers=headers, data=payload, files=files)
                resp_dict = json.loads(resp.text)
                # print(resp_dict)
                if resp_dict['errno'] != 31034:
                    break
                time.sleep(1)
            info = []
            if resp_dict['list']:
                for file in resp_dict['list']:
                    # print(file)
                    info.append(FileInfo(file))
                return info
            else:
                return False
        except Exception as error:
            print('-1', resp_dict)  # 把错误信息打印出来
            return error

    def query_file(self, fileinfo, path='/', thumb='0', dlink='1', extra='0'):
        # 利用文件ID数组fsids查询文件
        self.get_token()

        if type(fileinfo) == list:
            fsids = '['
            i = 0
            for f in fileinfo:
                if i == 0:
                    fsids += str(f.fs_id)
                else:
                    fsids += ',' + str(f.fs_id)
                i += 1
            fsids += ']'
        else:
            fsids = str(fileinfo.fs_id)

        url0 = "https://pan.baidu.com/rest/2.0/xpan/multimedia?"
        query = {
            'method': 'filemetas',
            'access_token': self.access_token,  # 接口鉴权参数
            'fsids': fsids,  # 文件id数组，数组中元素是uint64类型，数组大小上限是：100
            'path': path,  # 查询共享目录时需要，格式： /uk-fsid 其中uk为共享目录创建者id， fsid对应共享目录的fsid
            'thumb': thumb,  # 是否需要缩略图地址，0为否，1为是，默认为0
            'dlink': dlink,  # 是否需要下载地址，0为否，1为是，默认为0
            'extra': extra  # 图片是否需要拍摄时间、原图分辨率等其他信息，0 否、1 是，默认0
        }
        payload = {}
        files = {}
        headers = {
            'User-Agent': 'pan.baidu.com'
        }
        url = url0 + urlencode(query)
        # print(url)
        try:
            resp = requests.request("GET", url, headers=headers, data=payload, files=files)
            text_dict = json.loads(resp.text)
            if type(fileinfo) == list:
                i = 0
                for f in text_dict['list']:
                    fileinfo[i].file_name = f["filename"]
                    fileinfo[i].dlink = f["dlink"]
                    i += 1
            else:
                fileinfo.dlink = text_dict['list']["dlink"]
                fileinfo.file_name = text_dict['list']["filename"]
            return fileinfo
        except Exception as error:
            print(error)  # 把错误信息打印出来
            return error

    def download_file(self, fileinfo, save_path='.\\'):
        self.get_token()
        filename = fileinfo.filename
        file_path = save_path + filename
        query = {
            'access_token': self.access_token,  # 接口鉴权参数
        }
        payload = {}
        files = {}
        headers = {
            'User-Agent': 'pan.baidu.com'
        }
        url = fileinfo.dlink + '&' + urlencode(query)
        # print(url)
        try:
            resp = requests.request("GET", url, headers=headers, data=payload, files=files)
            self.get_token()
            with open(file_path, "wb") as code:
                code.write(resp.content)
            return file_path
        except Exception as error:
            print(error)  # 把错误信息打印出来
            return error

    def upload_file(self, file_path, remote_path):
        # 上传文件需要进行 预上传 -> 分片上传 -> 创建文件 三个步骤
        # 预上传时，需要完成 文件切分 和 MD5值计算
        # 参考 https://blog.csdn.net/z16   59655720/article/details/118752320

        # 判断会员类型，给出分片尺寸
        if self.vip_type == 0:
            chunk_size = int(4)
        elif self.vip_type == 1:
            chunk_size = int(16)
        else:
            chunk_size = int(32)
        # 根据分片尺寸进行分片，并计算出相应的 MD5值
        out_path = '.\\out\\'
        split(file_path, out_path, chunk_size)
        content_md5 = get_slice_md5(file_path)
        slice_md5 = get_slice_md5(file_path)
        files_path, files_md5 = get_files_md5(out_path)
        file_size = os.path.getsize(file_path)
        # 拼接 block_list 参数
        block_list = '['
        for md5 in files_md5:
            block_list += '"' + md5 + '",'
        block_list = block_list[0:-2] + '"]'
        # 预上传
        resp = self.pre_create_file(remote_path, file_size, block_list, content_md5, slice_md5)
        # print(resp)
        if resp['errno'] != 0:
            print('预上传失败！')
            return False
        upload_id = resp['uploadid']
        if resp['block_list'] == []:
            partseq = [0]
        else:
            partseq = resp['block_list']

        # 分片上传
        i = 0
        for file in files_path:
            self.part_upload(remote_path, upload_id, partseq[i], file)
            i += 1
        return self.create_remote_file(remote_path, upload_id, file_size, block_list)

    def pre_create_file(self, remote_path, file_size, block_list, content_md5, slice_md5):
        # 预上传 https://pan.baidu.com/union/doc/3ksg0s9r7
        # 返回值中 uploadid 和 partseq 后续分片上传需要
        self.get_token()
        url = "http://pan.baidu.com/rest/2.0/xpan/file?method=precreate&access_token=" + self.access_token
        query = {
            'path': remote_path,
            'size': file_size,
            'rtype': '1',  # 文件命名策略 0 为不重命名，返回冲突 1 为只要path冲突即重命名 2 为path冲突且block_list不同才重命名 3 为覆盖
            'isdir': '0',  # 是否为目录，0 文件，1 目录
            'autoinit': '1',
            'block_list': block_list,  # 文件各分片MD5数组的json串
            'content-md5': content_md5,  # 文件MD5，32位小写
            'slice-md5': slice_md5  # 文件校验段的MD5，32位小写，校验段对应文件前256KB
        }
        files = [

        ]
        headers = {
            'Cookie': 'BAIDUID=56BE0870011A115CFA43E19EA4CE92C2:FG=1; BIDUPSID=56BE0870011A115CFA43E19EA4CE92C2; PSTM=1535714267'
        }
        # url = url0 + urlencode(query)
        # print(url)
        resp = requests.request(method="POST", url=url, data=query, headers=headers, files=files)
        return json.loads(resp.text)

    def part_upload(self, remote_path, upload_id, partseq, local_path):
        # 分片上传
        # 文件小于4MB，直接上传一次即可。文件大于4MB 需要多次上传
        self.get_token()
        url0 = "https://d.pcs.baidu.com/rest/2.0/pcs/superfile2?"
        query = {'method': 'upload',
                 'access_token': self.access_token,
                 'type': 'tmpfile',
                 'path': remote_path,  # 上传后使用的文件绝对路径，需要urlencode，需要与上一个阶段预上传precreate接口中的path保持一致
                 'uploadid': upload_id,  # 上一个阶段预上传precreate接口下发的uploadid
                 'partseq': partseq  # 文件分片的位置序号，从0开始，参考上一个阶段预上传precreate接口返回的block_list
                 }
        payload = {}
        files = [
            ('util', open(local_path, 'rb'))
        ]
        headers = {
            'Cookie': 'BAIDUID=56BE0870011A115CFA43E19EA4CE92C2:FG=1; BIDUPSID=56BE0870011A115CFA43E19EA4CE92C2; PSTM=1535714267'
        }
        url = url0 + urlencode(query)
        resp = requests.request("POST", url, headers=headers, data=query, files=files)
        return json.loads(resp.text)

    def create_remote_file(self, remote_path, upload_id, size, block_list):
        # 创建文件
        self.get_token()
        url0 = "https://pan.baidu.com/rest/2.0/xpan/file?"
        payload = {'method': 'create',
                   'access_token': self.access_token,
                   'path': remote_path,  # 上传后使用的文件绝对路径，需要urlencode，需要与上一个阶段预上传precreate接口中的path保持一致
                   'size': size,  # 文件或目录的大小，必须要和文件真实大小保持一致，需要与预上传precreate接口中的size保持一致
                   'rtype': '1',
                   # 文件命名策略 0 为不重命名，返回冲突 1 为只要path冲突即重命名 2 为path冲突且block_list不同才重命名 3 为覆盖，需要与预上传precreate接口中的rtype保持一致
                   'isdir': '0',  # 是否目录，0 文件、1 目录，需要与预上传precreate接口中的isdir保持一致
                   'uploadid': upload_id,  # 同上
                   'block_list': block_list}  # 同上
        files = [

        ]
        headers = {
            'Cookie': 'BAIDUID=56BE0870011A115CFA43E19EA4CE92C2:FG=1; BIDUPSID=56BE0870011A115CFA43E19EA4CE92C2; PSTM=1535714267'
        }
        url = url0 + urlencode(payload)
        resp = requests.request("POST", url, headers=headers, data=payload, files=files)
        return json.loads(resp.text)

    def check_new(self, filepath, name_new, dance_new):
        # 根据舞曲名查找云盘中舞曲文件,并比对 md5 和 舞曲类型
        # 如果没有找到或者 md5 或 舞曲类型不匹配 则 上传至百度网盘（不在本函数中实现）
        # -----------------------------------
        # 返回值 (二进制) |  md5  |  dance |  name
        # -----------------------------------
        #   7  (111)    |   √   |   √    |    √
        #   6  (110)    |   √   |   √    |    ×
        #   5  (101)    |   √   |   ×    |    √
        #   4  (100)    |   √   |   ×    |    ×
        #   3  (011)    |   ×   |   √    |    √
        #   2  (010)    |   ×   |   √    |    ×
        #   1  (001)    |   ×   |   ×    |    √
        #   0  (000)    |   ×   |   ×    |    ×
        # 其中，返回值 7 6 5 4 说明存在该舞曲，但是舞曲命名name不同或舞曲类型dance不同
        # 返回值 3 2 说明存在 相似舞曲，可能是该舞曲的不同版本，也可能是舞曲类型dance不同
        # 返回值 0 说明完全不存在该舞曲
        # 为了方便查找，我们定义一个优先级
        # 7 > 6 > 5 > 4 > 3 > 1 > 0 也就是说当与多个文件比较时，优先返回大的返回值

        md5_new = get_file_md5(filepath)  # 获取新舞曲的 md5 值
        # 根据文件名和舞种从百度网盘中搜索文件，对比 md5值
        search1 = self.search_file(dance_new)
        time.sleep(1)
        search2 = self.search_file(name_new)
        if search1 and search2:
            search_res = search1
            search_res.extend(search2)
        elif search1 and not search2:
            search_res = search1
        elif not search1 and search2:
            search_res = search2
        elif not search1 and not search2:
            return 0

        # search_res = self.search_file(name_new)
        out = [0, 0, 0]
        for music in search_res:
            filename = music.filename
            # 根据网盘中舞曲命名规则  舞种-舞曲名.mp3 的格式获取舞种和舞曲名
            index1 = filename.find('-')
            # index2 = filename.find('-', index1 + 1)
            index3 = filename.find('.', index1 + 1)
            dance_old = filename[0:index1]
            name_old = filename[index1 + 1:index3]
            # print(dance_old,name_old)
            # if index2 == -1:
            #     name_old = filename[index1 + 1:index3]
            # else:
            #     name_old = filename[index1 + 1:index2]
            md5_old = music.md5
            if md5_new == md5_old:
                out[0] = 1  # 如果两者md5值相同，则进一步判断舞曲类型dance
                if dance_new == dance_old:  # 如果两者舞曲类型dance值相同，则进一步判断舞曲名name
                    out[1] = 1
                    if name_new == name_old:
                        out[2] = 1
                        break
                elif out[1] == 0 and dance_new != dance_old:  # 如果之前已经有舞曲类型相同的，则不再讨论不同的情况
                    if name_new == name_old:
                        out[2] = 1
            elif out[0] == 0 and md5_new != md5_old:  # 如果之前已经有md5值相同的，则不再讨论不同的情况
                if dance_new == dance_old:
                    out[1] = 1
                    if name_new == name_old:
                        out[2] = 1
                elif out[1] == 0 and dance_new != dance_old:
                    if name_new == name_old:
                        out[2] = 1
        return out[0] * 4 + out[1] * 2 + out[2]

    def upload_new(self, level, file_path):
        path = os.path.split(file_path)
        file_name = path[1]
        if is_number(file_name[0]):
            file_name = file_name[file_name.find('-')+1:]
        if '点播' in file_name:
            file_name = file_name[:file_name.rfind('-')] + file_name[file_name.rfind('.'):]
        remote_path = '/apps/Music/'
        # print(level)
        if level == 7:
            return -1
        elif level in [6, 4, 2, 0]:
            remote_path += 'NewMusic/' + file_name
        elif level in [5, 1]:
            remote_path += 'NewDance/' + file_name
        # elif level in [3]:
        #     remote_path += 'NewTag/' + file_name
        print(level, file_name+' 上传至 '+remote_path)
        return self.upload_file(file_path, remote_path)

    def upload_new_music(self, file_path, dance_new):
        #
        # list = info.list
        try:
            # for music in list:
            # file_path = music.path
            # if music.other is None:
            #     name_new = music.name
            # else:
            #     name_new = music.name + '-' + music.other
            # 因此 info.name 中的符号进行了替换，因此从路径中提取 曲名
            # Tem = os.path.split(file_path)
            # name_new = Tem
            file, extname = os.path.splitext(file_path)
            dance = file[file.find('-', 1) + 1:]
            name_new = dance[dance.find('-', 1) + 1:]
            dance_new = dance[:dance.find('-', 1)]
            # dance_new = music.dance
            level = self.check_new(file_path, name_new, dance_new)
            # print(level)
            self.upload_new(level, file_path)
            # time.sleep(1)
            return True
        except Exception as error:
            print(error)  # 把错误信息打印出来
            return False


class FileInfo:
    fs_id = None
    path = None
    filename = None
    size = None
    category = None
    md5 = None
    dlink = None

    # server_mtime = None
    # server_ctime = None
    # local_mtime = None
    # local_ctime = None
    # isdir = None
    # dir_empty = None
    # thumbs = None

    def __init__(self, file_info):
        # response_dict = json.loads(response.text)
        # for file_info in response_dict['list']:
        # self.isdir = file_info["isdir"]
        self.path = file_info["path"]
        self.fs_id = file_info["fs_id"]
        self.category = file_info["category"]
        if "md5" in file_info:
            self.md5 = file_info["md5"]
        else:
            self.md5 = "-1"
        self.size = file_info["size"]
        if "server_filename" in file_info:
            self.filename = file_info["server_filename"]
        elif "file_name" in file_info:
            self.filename = file_info["file_name"]
        else:
            self.filename = 'None'


# class BaiduFile:
#     lsit = []


if __name__ == "__main__":
    client_id = 'FSSKhNGwkSzrLf3E6BlcmcE54PSEFeaa'
    client_secret = 'vWM6ADj5cEPLojzkGAZWrv9iGWWaZp91'

    # # 登录百度网盘账号，获取 token
    bai = BaiduNet(client_id, client_secret)
    var = bai.test_connection()
    if not var[0]:
        print(var[2])
        url = input('')
        bai.get_access_token(url)
    # filepath1 = 'C:\\Users\\Yanch\\Desktop\\20230910 青春舞会舞曲by星尘\\06-青春16步-YMCA-unknown-点播.mp3'
    # filepath2 = 'C:\\Users\\Yanch\\Desktop\\20230910 青春舞会舞曲by星尘\\07-伦巴-而我知道-五月天.mp3'
    # print(bai.check_new(filepath1, 'YMCA-unknown', '青春16步'))
    # print(bai.check_new(filepath2, '而我知道-五月天', '伦巴'))
    path = 'C:\\Users\\Yanch\\Desktop\\20230910 青春舞会舞曲by星尘'
    for files in os.listdir(path):
        file, extname = os.path.splitext(files)
        dance = file[file.find('-',1)+1:]
        name = dance[dance.find('-',1)+1:]
        dance = dance[:dance.find('-',1)]
        # print(name,dance)
        print(file, bai.check_new(path +'\\' + files, name, dance))
        # print(bai.check_new(filepath1, 'YMCA-unknown', '青春16步'))
        # print(bai.check_new(filepath2, '而我知道-五月天', '伦巴'))
    # print(bai.upload_new(3, filepath1))

    #
    # # check_new
    # filepath = '.\\20190920 排曲\\05-兔子舞-卖汤圆.mp3'
    # name_new = '卖汤圆'
    # dance_new = '兔子舞'
    # re = bai.check_new(filepath, name_new, dance_new)
    # print(re)
    # Tem = os.path.split('.\\20190920 排曲\\05-兔子舞-卖汤圆.mp3')
    # print(Tem[1][Tem[1].find('-', 3)+1:Tem[1].rfind('.')])
    # 上传文件测试
    # print(split('.\\舞曲列表生成器.exe', chunksize=16))
    # bai.upload_file('.\\舞曲列表生成器.exe', '/apps/test/舞曲列表生成器.exe')

    # 获取文件列表测试
    # response = bai.get_list('/HBDC舞曲库/1.拉手舞/1.伦巴')
    # print(response)

    # res = bai.query_file(response)
    # print(bai.refresh_token,bai.access_token)
    # print(res[3])

    # 搜索文件测试
    # filepath = 'D:\\Guokr\\Docement\\wuqu\\Code\\Music\\09-伦巴-情非得已-庾澄庆.mp3'
    # filepath = 'C:\\Users\\Yanch\\Desktop\\music\\3.mp3'
    # out = bai.check_new(filepath, '情非得已-庾澄庆', '伦巴')
    # print(out)
    # response = bai.search_file('情非得已-庾澄庆')
    # print(response)
    # print(response[1].filename)

    # 下载文件测试
    # resp = bai.search_file('美丽大草原')
    # bai.download_file(resp[1])
    # print(bai.download_file(resp[0]))

    # back = 'https://openapi.baidu.com/oauth/2.0/login_success#expires_in=2592000&access_token=123.278cf420653e4989e76126b72ab582c9.YQfC87m0V8fG3jDXsmDAs5v3QvZyPr7QXGyPh5w.EIgGvA&session_secret=&session_key=&scope=basic+netdisk'
    # print(back[back.find('access_token=')+13:back.find('&session_secret=&session_key=')])

