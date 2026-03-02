import os
# from tqdm import tqdm
import datetime
from pymediainfo import MediaInfo
import json
import hashlib


# from iteration_utils import duplicates

def dance_count(names, dance_type):
    # 查找names中还有多少首type
    length = len(dance_type)
    num = [0] * length
    for a in names:
        for i in range(0, length):
            if a.count(dance_type[i]) > 0:
                num[i] = num[i] + 1
    return num


def get_file_md5(file_name):
    """
    计算文件的md5
    :param file_name:
    :return:
    """
    m = hashlib.md5()  # 创建md5对象
    with open(file_name, 'rb') as fobj:
        while True:
            data = fobj.read(4096)
            if not data:
                break
            m.update(data)  # 更新md5对象

    return m.hexdigest()  # 返回md5对象


def read_info(file_path):
    # 读取舞曲信息 文件名/文件夹名/时长/title/album
    media_info = MediaInfo.parse(file_path)
    data = json.loads(media_info.to_json())
    # print(data['tracks'][0])
    datadic = data['tracks'][0]
    file_name = datadic['file_name_extension']
    if 'folder_name' in datadic.keys():
        folder_name = datadic['folder_name']
    else:
        folder_name = []
    if 'duration' in datadic:
        duration = datadic['duration']
    else:
        duration = 210*1000
    if 'title' in datadic:
        title = datadic['title']
    else:
        title = []
    if 'album' in datadic:
        album = datadic['album']
    else:
        album = []
    return file_name, folder_name, duration // 1000, title, album


def is_number(s):
    # 判断字符是否为数字
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False


def dance_type(dance):
    handle = ['伦巴', '平四', '吉特巴']
    frame = ['慢四', '慢三', '并四', '快三', '中三', '中四']
    ballroom = ['华尔兹', '探戈', '维也纳', '狐步', '快步', '国标伦巴', '恰恰', '桑巴', '牛仔', '斗牛','阿根廷探戈']
    collective = ['16步', '花火16步', '32步', '64步', '青春16步', '脱掉16步', '兔子舞', '集体恰恰', '阿拉伯之夜',
                  '马卡琳娜', '玛卡琳娜', '蒙古舞']

    if handle.count(dance) >= 1:
        dance_type = 'handle'
    elif frame.count(dance) >= 1:
        dance_type = 'frame'
    elif ballroom.count(dance) >= 1:
        dance_type = 'ballroom'
    elif collective.count(dance) >= 1:
        dance_type = 'collective'
    else:
        dance_type = None
    return dance_type


def slow_quick(dance):
    slow = ['伦巴', '慢四', '慢三', '华尔兹']
    middle = ['中三', '中四', '并四']
    quick = ['平四', '吉特巴', '快三', '维也纳']

    if slow.count(dance) >= 1:
        speed = 'slow'
    elif middle.count(dance) >= 1:
        speed = 'middle'
    elif quick.count(dance) >= 1:
        speed = 'quick'
    else:
        speed = None
    return speed


def dance_count(names, dance_type):
    # 查找names中还有多少首type
    length = len(dance_type)
    num = [0] * length
    for a in names:
        for i in range(0, length):
            if a.count(dance_type[i]) > 0:
                num[i] = num[i] + 1
    return num


def dance_counts(info):
    dances = []
    # print(type(info))
    if isinstance(info, dict):
        for i in info['music']:
            dances.append(i['dance'])
    else:
        dances = info
    # print(dances)
    handle = ['伦巴', '平四', '吉特巴']
    frame = ['慢四', '慢三', '并四', '快三', '中三', '中四']
    ballroom = ['华尔兹', '探戈', '维也纳', '狐步', '快步', '国标伦巴', '国标恰恰', '桑巴', '牛仔', '斗牛','阿根廷探戈']
    collective = ['青春16步', '花火16步', '32步', '64步', '兔子舞', '集体恰恰', '阿拉伯之夜',
                  '马卡琳娜', '玛卡琳娜', '蒙古舞']

    ballroom_num = dance_count(dances, ballroom)
    # print(ballroom_num)
    ballroom_num[1] = ballroom_num[1] - ballroom_num[10]  # 将阿根廷探戈从探戈中扣除
    # print(ballroom_num)
    return {
        'handle': dance_count(dances, handle),
        'frame': dance_count(dances, frame),
        'ballroom': ballroom_num,
        'collective': dance_count(dances, collective),
    }


def music_info(path):
    handle = ['伦巴', '平四', '吉特巴']
    frame = ['慢四', '慢三', '并四', '快三', '中三', '中四']
    ballroom = ['华尔兹', '探戈', '维也纳', '狐步', '快步', '国标伦巴', '国标恰恰', '桑巴', '牛仔', '斗牛','阿根廷探戈']
    collective = ['青春16步', '花火16步', '32步', '64步', '兔子舞', '集体恰恰', '阿拉伯之夜',
                  '马卡琳娜', '玛卡琳娜', '蒙古舞']
    other = ['开场曲', '结束曲']

    name, folder_name, duration, title, album = read_info(path)

    # 获取文件名
    # 通过"-"获取每首舞曲的 序号 舞种 舞曲名
    name = name.replace(" - ", "-")  # 将name中" - "替换为"-”
    name = name.replace("- ", "-")  # 将name中" - "替换为"-”
    name = name.replace(" -", "-")  # 将name中" - "替换为"-”
    name = name.replace("（", "(")  # 将name中"（"替换为")”
    name = name.replace("）", ")")  # 将name中"）"替换为"(”
    name = name.replace("(1)", "")  # 剔除name中的(1)
    name = name.replace("(2)", "")  # 剔除name中的(1)
    index0 = name.rfind('.')
    if name[0:2].isdigit() and not name[2] == '步':
        Num = int(name[0:2])  # 序号为文件名的前两个字符
        temName = name[3:index0]
    else:
        Num = None  # 序号为文件名的前两个字符
        temName = name[0: index0]
    # if temName[0] == ' ':
    #     temName = temName[1:-1]

    index = temName.find('-')
    # 替换 十八摸 16步 维也纳华尔兹
    if temName[0:index] == '十八摸':
        temName = temName.replace("十八摸", "玛卡琳娜", 1)
        index = 4
    if temName[0:index] == '马卡琳娜':
        temName = temName[0:index].replace("马卡琳娜", "玛卡琳娜", 1)
    if '16步' in temName[0:index] and '青春16步' not in temName[0:index] and '花火16步' not in temName[0:index]:
        temName = temName.replace("16步", "花火16步")
        index = 5
    if '16步脱掉' in temName[0:index]:
        temName = temName.replace("16步脱掉", "青春16步")
    if '脱掉16步' in temName[0:index]:
        temName = temName.replace("脱掉16步", "青春16步")
    if '维也纳华尔兹' in temName[0:index]:
        temName = temName.replace("维也纳华尔兹", "维也纳")
        index = 3


    if index == -1 or (temName[0:index] not in handle+frame+ballroom+collective+other):  # 如果未发现"-",将舞种、舞曲名定义为文件名
        # dance = temName
        dance = ''
        music = temName
        other = None
    else:
        dance = temName[0:index]
        # music = name_tem[index + 1:len(name_tem)]
        name_tem2 = temName[index + 1:len(temName)]
        index01 = name_tem2.find('-')
        if name_tem2[index01 + 1:len(temName)].find('-') == -1:
            index2 = -1
        else:
            index2 = index01 + 1 + name_tem2[index01 + 1:len(temName)].find('-')
        if index2 == -1:
            music = name_tem2
            other = None
        else:
            music = name_tem2[0:index2]
            other = name_tem2[index2 + 1:len(name_tem2)]

    # 处理folder_name

    # music = Music(Num, dance, music, duration, other, folder_name, title, md5)

    keyword = '点播'
    on_demand = False
    if other is None:
        if name.count(keyword) >= 1:
            on_demand = True
    elif other.count(keyword) >= 1 or name.count(keyword) >= 1:
        on_demand = True

    info = {
        'num': Num,
        'dance': dance,
        'title': music,
        'choose': on_demand,
        'duration': duration,
        'other': other,
        'speed': slow_quick(dance),
        'dancetype': dance_type(dance),
        'MD5': get_file_md5(path),
        'filepath': path,
        'filename': name,
        'folder_name': folder_name,
        'is_change': False,
    }

    return info


def list_info(path):
    # 从路径path获取音乐文件的信息
    # 读取上一级目录下的所有文件及其子目录下的 mp3/wav 文件，至获取路径，不读取其他信息

    extNames = ['.mp3', '.wma', '.ogg', '.m4a', '.flac']

    count_tot = 0
    paths = []
    for file in os.listdir(path):
        filepath = os.path.join(path, file)
        if os.path.isdir(filepath):
            for file1 in os.listdir(filepath):
                filepath1 = os.path.join(filepath, file1)
                files, extname = os.path.splitext(filepath1)
                if not os.path.isdir(filepath1) and (extname in extNames):
                    paths.append(filepath1)
        else:
            files, extname = os.path.splitext(file)
            if extname in extNames:
                paths.append(filepath)

    dances = []
    list_dist = {
        'duration': None,
        'count': None,
        'distribution': None,
        'path': path,
        'list': [
            {
                'part_title': None,
                'count': None,
                'duration': None,
                'music': [],
            },
        ],
    }
    count_tot = 0
    duration_tot = 0
    durations = 0
    count = 0
    for i in range(0, len(paths)):
        # print(paths[i])
        info = music_info(paths[i])

        folder_name = info['folder_name']
        if folder_name == path:
            folder_name = []
        else:
            folder_name = folder_name[folder_name.rfind('\\') + 1:]  # 取得子文件夹名字
            folder_name = folder_name[folder_name.find('-') + 1:]

        if i == 0:
            j = 0
            list_dist['list'][0]['part_title'] = folder_name
            count = 0
            durations = 0
        if folder_name != list_dist['list'][j]['part_title']:
            list_dist['list'][j]['duration'] = durations
            list_dist['list'][j]['count'] = count
            durations = 0
            count = 0
            list_dist['list'].append(
                {
                    'part_title': folder_name,
                    'count': None,
                    'duration': None,
                    'music': [],
                })
            j += 1

        count += 1
        durations += info['duration']
        count_tot += 1
        duration_tot += info['duration']
        list_dist['list'][j]['music'].append(info)
        dances.append(info['dance'])

    list_dist['list'][-1]['duration'] = durations
    list_dist['list'][-1]['count'] = count
    list_dist['duration'] = duration_tot
    list_dist['count'] = count_tot

    list_dist['distribution'] = dance_counts(dances)

    return list_dist


# global handle, frame, ballroom, collective
# # 定义舞曲类型

if __name__ == '__main__':
    # print(list_info("D:/Guokr/Docement/wuqu/Code/Music"))
    # a = music_info("F:\\SongList_Gen\\Music\\新建文件夹\\03-并四-芒种-赵方婧.mp3")
    # print(a)
    # a = music_info("F:\\SongList_Gen\\Music\\新建文件夹\\02-伦巴-橘子汽水-南拳妈妈-果壳点播.mp3")
    # print(a)
    # a = music_info("F:\\SongList_Gen\\Music\\新建文件夹\\01-兔子舞-兔子舞.mp3")
    # print(a)
    # handle = ['伦巴', '平四', '吉特巴']
    # frame = ['慢四', '慢三', '并四', '快三', '中三', '中四']
    # ballroom = ['华尔兹', '探戈', '维也纳', '狐步', '快步', '国标伦巴', '国标恰恰', '桑巴', '牛仔', '斗牛']
    # collective = [ '青春16步', '花火16步', '32步', '64步', '兔子舞', '集体恰恰', '阿拉伯之夜',
    #               '马卡琳娜', '玛卡琳娜', '蒙古舞']
    # print('吉特巴' in collective)
    print(music_info("C:\\Users\\Yanch\\Desktop\\团圆舞会歌单\\22-十八摸-玛卡琳娜-MACARENA-3'36''版.mp3"))