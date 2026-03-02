def distribution_generate(dance_type, num):
    # 将舞种和数量合并在一起
    out = str()
    k = 0
    no = len(num) - num.count(0) - 1
    for i in range(0, len(num)):
        if num[i] != 0:
            if k < no:
                out = out + dance_type[i] + str(num[i]) + '首、'
                k = k + 1
            else:
                out = out + dance_type[i] + str(num[i]) + '首'
    return out


def collective_distribution_generate(dance_type, num):
    # 合并集体舞和数量合并在一起
    out = str()
    k = 0
    no = num.count(1) - 1
    for i in range(0, len(num)):
        if num[i] == 1:
            if k < no:
                out = out + dance_type[i] + '、'
                k = k + 1
            else:
                out = out + dance_type[i]
    if out != '':
        if out.count('、') >= 1:
            out = out + '各1首'
        else:
            out = out + '1首'
    no = len(num) - num.count(0) - num.count(1) - 1
    k = 0
    for i in range(0, len(num)):
        if num[i] > 1:
            if k == 0 and out != '':
                out = out + '、'
            if k < no:
                out = out + dance_type[i] + str(num[i]) + '首、'
                k = k + 1
            else:
                out = out + dance_type[i] + str(num[i]) + '首'
    return out


def dance_dis(dances):
    # handle_dis = dance_count(dances, handle)
    # frame_dis = dance_count(dances, frame)
    # ballroom_dis = dance_count(dances, ballroom)
    # collective_dis = dance_count(dances, collective)
    #
    # ballroom_dis[6] = ballroom_dis[6] - collective_dis[7]  # 从(国标)恰恰中删除集体恰恰的数目
    # collective_dis[0] = collective_dis[0] - collective_dis[1] - collective_dis[4] - collective_dis[
    #     5]  # 从16步中删除花火16步、青春16步、脱掉16步的数目

    handle = ['伦巴', '平四', '吉特巴']
    frame = ['慢四', '慢三', '并四', '快三', '中三', '中四']
    ballroom = ['华尔兹', '探戈', '维也纳', '狐步', '快步', '国标伦巴', '国标恰恰', '桑巴', '牛仔', '斗牛','阿根廷探戈']
    collective = ['青春16步', '花火16步', '32步', '64步', '兔子舞', '集体恰恰', '阿拉伯之夜',
                  '马卡琳娜', '玛卡琳娜', '蒙古舞']

    handle_dis = dances[0]
    frame_dis = dances[1]
    ballroom_dis = dances[2]
    collective_dis = dances[3]

    # 将舞曲名与数目拼接成可输出的文体格式
    out = [distribution_generate(handle, handle_dis), distribution_generate(frame, frame_dis),
           distribution_generate(ballroom, ballroom_dis), collective_distribution_generate(collective, collective_dis)]

    return out


def s2hms(time):
    # 将时长从秒数转换为 XX m XX s 的形式
    hour = time // 3600
    time += - hour * 3600
    if time // 60 < 10:
        min = '0' + str(time // 60)
    else:
        min = str(time // 60)
    if time % 60 < 10:
        sec = '0' + str((time % 60) // 1)
    else:
        sec = str((time % 60) // 1)
    if hour > 0:
        times = str(hour) + ':' + min + ':' + sec
    else:
        times = min + ':' + sec
    return times


def txt(info, path, filename="舞曲列表"):
    # 将字典类型转换成 先前类型
    # title = info['title']
    author = info['name']
    duration_tot = info['duration']
    distribution = []
    distribution.append(info['distribution']['handle'])
    distribution.append(info['distribution']['frame'])
    distribution.append(info['distribution']['ballroom'])
    distribution.append(info['distribution']['collective'])
    distribution = dance_dis(distribution)
    session = [[], []]
    if info['list'][0]['part_title']:
        j = 0
        session[0].append(0)
        for i in range(len(info['list'])):
            session[1].append(info['list'][i]['part_title'])
            if i != 0:
                num = info['list'][i-1]['count']
                session[0].append(num)
            j += 1
    dance_list = []
    for i in info['list']:
        for j in i['music']:
            dance_list.append((str(j['num']) if j['num'] > 10 else '0' + str(j['num'])) + '-' + j['dance'] + '-' + j[
                'title'] + ' (' + s2hms(j['duration']) + ')')
    date = info['date']

    file_id = open(path + "\\" + filename + ".txt", 'w+', encoding='utf-8')

    out0 = '本次舞曲由 ' + author + ' 编排，共' + str(len(dance_list)) + '首曲子（包括清场与开场曲目），总时长为' + str(
        duration_tot // 3600) + '小时' + str(
        (duration_tot % 3600) // 60) + '分' + str(duration_tot % 60) + '秒。'

    print(out0, file=file_id)
    print('\r', file=file_id)

    for o in distribution:
        if o == '各1首':
            continue
        print(o, file=file_id)
    print('\r', file=file_id)
    i = 0
    for o in dance_list:
        if i in session[0]:
            print('=====' + session[1][session[0].index(i)] + '=====', file=file_id)
        print(o, file=file_id)
        i = i + 1
    print('\r', file=file_id)

    print(date, file=file_id)
    file_id.close()


def html(info0, path, filename="song-list"):
    author = info0['name']
    duration_tot = info0['duration']
    distribution = []
    distribution.append(info0['distribution']['handle'])
    distribution.append(info0['distribution']['frame'])
    distribution.append(info0['distribution']['ballroom'])
    distribution.append(info0['distribution']['collective'])
    distribution = dance_dis(distribution)
    session = [[], []]
    if info0['list'][0]['part_title']:
        j = 0
        session[0].append(0)
        for i in range(len(info0['list'])):
            session[1].append(info0['list'][i]['part_title'])
            if i != 0:
                num = info0['list'][i-1]['count']
                session[0].append(num)
            j += 1
    num = []
    info = []
    duration = []
    on_demand = []
    for i in info0['list']:
        for j in i['music']:
            num.append(str(j['num']) if j['num'] >= 10 else '0' + str(j['num']))
            if j['choose'] and j['other']:
                info.append(j['dance'] + '-' + j['title'] + '-' + j['other'])
            else:
                info.append(j['dance'] + '-' + j['title'])
            duration.append(j['duration'])
            on_demand.append(j['choose'])
    date = info0['date']
    # 计算舞曲累计时长
    duration_sum = [duration[0]]
    timestamp = []
    for i in range(1, len(duration)):
        duration_sum.append(duration[i]+duration_sum[i-1])
        if duration_sum[i] >= 3600*(len(timestamp)+1):
            timestamp.append(i-1)

    html = open(path + "\\" + filename + ".html", 'w+', encoding='utf-8')

    # 生成文件头和标题
    n = 3 * (11 - len(info0['title'])) // (len(info0['title']) - 1)
    title = ''
    for i in info0['title'][0:-1]:
        title += i + '&nbsp;' * n
    title += info0['title'][-1]

    html.write(
        "<!DOCTYPE html>\n<html>\n<head>\n<meta charset='utf-8'>\n<title>" + info0[
            'title'] + "</title>\n<link rel='stylesheet' "
                       "href='./css/wuqu_phone.css'>\n</head>\n<body>\n<div "
                       "id='bg'>\n<header>\n<h2>" + title + "</h2>\n</header>")
    # 生成排曲人员信息
    header = "\n<section class='info'>\n本次舞曲由<strong class='name'>" + author + "</strong>编排，共<strong class='num'>" + str(
        len(num)) + "</strong>首曲子（包括清场与开场曲目），总时长为<strong class='time'>" + str(
        duration_tot // 3600) + "小时" + str(
        (duration_tot % 3600) // 60) + "分" + str(duration_tot % 60) + "秒。</strong>\n</section>"
    html.write(header)
    # 舞会信息

    partInfo = "\n<div class='clearfix'>\n<div class='center, party_info'>\n<tbody>\n<table>\n<tr>\n<td id='place'>" \
               + info0['place'] + "</td>\n<td id='startTime'>" + info0['time'][0] + ' ' + info0['time'][1] \
               + "</td>\n</tr>\n</table>\n</tbody>\n</div>\n</div>"
    html.write(partInfo)

    # 生成舞曲分布
    nav1 = "\n<nav class='clearfix'>\n<div class='center'>\n<h3>舞&nbsp;&nbsp;曲&nbsp;&nbsp;分&nbsp;&nbsp;布</h3>\n<div " \
           "class='dis'>\n<div class='left'>\n<tbody>\n<table> "

    nav2 = ""
    j = 1
    for o in distribution:
        if len(o) == 0:  # 如果拉手舞、架型舞、国标舞、集体舞一种没有就跳过
            continue
        nav2 = nav2 + "\n<tr><td>" + o + "</td></tr>"
        if j == 2:  # 架型舞结束后换列
            nav2 = nav2 + "\n</table>\n</tbody>\n</div>\n<div class='right'>\n<tbody>\n<table>"
        j = j + 1

    nav3 = "\n</table>\n</tbody>\n</div>\n</div>\n</div>\n</nav>"

    html.write(nav1 + nav2 + nav3)

    # 生成舞曲列表
    sec1 = "\n<section class='list'>\n<div class='center'>\n<h3>舞&nbsp;&nbsp;曲&nbsp;&nbsp;列&nbsp;&nbsp;表</h3>\n<div " \
           "class='cont'>"

    sec2 = ""

    for i in range(len(info)):
        if not session[0] and i == 0:
            sec2 = sec2 + "\n<tbody>\n<table>"
        if i in session[0]:
            if session[0].index(i) != 0:
                sec2 = sec2 + "\n</table>\n</tbody>"
            sec2 = sec2 + "\n<div class='sessions'>" + session[1][
                session[0].index(i)] + "</div>\n<tbody>\n<table>" + "\n<div class='sessdur'>" + \
                   s2hms(info0['list'][session[0].index(i)]['duration']) + "</div>"
        if on_demand[i]:
            sec2 = sec2 + "\n<tr><td class='no'>" + num[i] + "</td><td class='music choose'>" + info[
                i] + "</td><td class='dur'>" + s2hms(duration[i]) 
        else:
            sec2 = sec2 + "\n<tr><td class='no'>" + num[i] + "</td><td class='music'>" + info[
                i] + "</td><td class='dur'>" + s2hms(duration[i])
        if i in timestamp:
            sec2 = sec2 + "</td><td class='timestamp_gap'></td></tr>"
        else:
            sec2 = sec2 + "</td><td class='timestamp'></td></tr>"

    sec3 = "\n</table>\n</tbody>\n<footer class='right'>\n<p class='hbdc'>" + info0['club'] \
           + "</p>\n<p class='date'>" + date + "</p>\n</footer>\n</div>\n</div>\n</section>"

    end = "\n<div class='aim'>\n让交谊舞走进每个人的生活\n</div>\n<div " \
          "class='security'>\n伟大的果壳大人永垂不朽！\n</div>\n</body>\n</body>\n</html> "

    html.write(sec1 + sec2 + sec3 + end)
    html.close()


if __name__ == "__main__":
    # print(get_width(ord('々')))
    # print(ceil(str_len('平四-最强のフュージョン《龙珠剧场版》-V.A——花正仁点播') / (16.5 * 2)))
    from song_info import *

    a = list_info("D:\Guokr\Docement\wuqu\SongList_Gen2\Music")
    a['title'] = '11'
    a['name'] = '12'
    a['date'] = '2022年12月11日'
    a['club'] = '2022年12月11日'
    a['title'] = '青春舞会舞曲'
    path = '..'
    html(a, path)
    txt(a, path)
