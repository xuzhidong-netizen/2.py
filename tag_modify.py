import datetime
import os
import struct
import base64

from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, TSO2, TCON, TRCK, TPOS, TDRC, PictureType
from mutagen.asf import ASF, ASFUnicodeAttribute, ASFByteArrayAttribute
from mutagen.oggvorbis import OggVorbis
from mutagen import File
from mutagen.flac import FLAC, Picture
import re


def DelAllCover(path):
    # 删除封面
    try:
        audio = ID3(path)
        del_list = []
        for i in audio:
            a = re.search(r"APIC", i)
            if a:
                del_list.append(i)
        for i in del_list:
            del (audio[i])
        audio.save()
        return True
    except Exception as error:
        # return error
        return False


def pack_image(data, mime='image/jpeg', type=3, description=u'Cover'):
    """
    Helper function to pack image data for a WM/Picture tag.
    See unpack_image for a description of the data format.
    """
    tag_data = struct.pack("<bi", type, len(data))
    tag_data += mime.encode("utf-16-le") + b"\x00\x00"
    tag_data += description.encode("utf-16-le") + b"\x00\x00"
    tag_data += data
    return tag_data


def SetMp3Info(path, tagInfo):
    # try:
    if 'picData' in tagInfo:
        DelAllCover(path)
        songFile = ID3(path)
        songFile['APIC'] = APIC(  # 插入封面
            encoding=0,
            mime='image/jpeg',
            type=3,
            desc=u'Cover',
            data=tagInfo['picData']
        )
    else:
        songFile = ID3(path)
    songFile['TIT2'] = TIT2(  # 插入歌名
        encoding=3,
        text=tagInfo['title']
    )
    if 'artist' not in tagInfo:
        tagInfo['artist'] = u'HBDC'
    songFile['TPE1'] = TPE1(  # 插入第一演奏家、歌手、等
        encoding=3,
        text=tagInfo['artist']
    )
    songFile['TALB'] = TALB(  # 插入专辑名
        encoding=3,
        text=u"华中科技大学国标舞俱乐部曲库"
    )
    songFile['TSO2'] = TSO2(  # 插入专辑名
        encoding=3,
        text=u"HBDC"
    )
    songFile['TDRC'] = TDRC(  # 年份
        encoding=3,
        text=tagInfo['year']
    )
    songFile['TCON'] = TCON(  # 流派
        encoding=3,
        text=tagInfo['genre']
    )
    songFile['TRCK'] = TRCK(  # 音轨
        encoding=3,
        text=['']
    )
    songFile['TPOS'] = TPOS(  # 碟号
        encoding=3,
        text=['']
    )
    songFile.save()
    return True
    # except Exception as error:
    #     print(error)  # 把错误信息打印出来
    #     return False


def SetWmaInfo(path, tagInfo):
    songFile = ASF(path)
    if 'picData' in tagInfo:
        if 'WM/Picture' in songFile:
            del songFile['WM/Picture']
        # pack_image(tagInfo['picData'])
        songFile['WM/Picture'] = [ASFByteArrayAttribute(pack_image(tagInfo['picData']))]
    songFile['Title'] = [ASFUnicodeAttribute(tagInfo['title'])]
    if 'artist' not in tagInfo:
        tagInfo['artist'] = u'HBDC'
    songFile['Author'] = [ASFUnicodeAttribute(tagInfo['artist'])]
    songFile['WM/AlbumTitle'] = [ASFUnicodeAttribute(u'华中科技大学国标舞俱乐部曲库')]
    songFile['WM/AlbumArtist'] = [ASFUnicodeAttribute(u'HBDC')]
    songFile['WM/Year'] = [ASFUnicodeAttribute(tagInfo['year'])]
    songFile['WM/Genre'] = [ASFUnicodeAttribute(tagInfo['genre'])]
    if 'WM/TrackNumber' in songFile:
        del songFile['WM/TrackNumber']
    if 'WM/PartOfSet' in songFile:
        del songFile['WM/PartOfSet']
    songFile.save()


def SetOggInfo(path, tagInfo):

    # songFile['metadata_block_picture'] = [ASFByteArrayAttribute(pack_image(tagInfo['picData']))]
    songFile = File(path)
    # picture = Picture()
    # picture.data = tagInfo['picData']
    # picture.type = PictureType.COVER_FRONT
    # # picture.desc = u"123"
    # picture.mime = u"image/jpeg"
    # picture.width = 1000
    # picture.height = 1000
    # picture.depth = 16
    #
    # picture_data = picture.write()
    # encoded_data = base64.b64encode(picture_data)
    # vcomment_value = encoded_data.decode("ascii")
    #
    # songFile["metadata_block_picture"] = [vcomment_value]

    songFile['title'] = tagInfo['title']
    if 'artist' not in tagInfo:
        tagInfo['artist'] = u'HBDC'
    songFile['artist'] = tagInfo['artist']
    songFile['album'] = u"华中科技大学国标舞俱乐部曲库"
    songFile['albumartist'] = u"HBDC"
    songFile['date'] = tagInfo['year']
    songFile['genre'] = tagInfo['genre']
    songFile['tracknumber'] = ''
    songFile['discnumber'] = ''
    songFile.save()


def SetFlacInfo(path, tagInfo):
    songFile = FLAC(path)

    pic = Picture()
    pic.data = tagInfo['picData']
    pic.type = PictureType.COVER_FRONT
    pic.mime = u"image/jpeg"
    pic.width = 500
    pic.height = 500
    pic.depth = 16  # color depth
    songFile.add_picture(pic)

    songFile['title'] = tagInfo['title']
    if 'artist' not in tagInfo:
        tagInfo['artist'] = u'HBDC'
    songFile['artist'] = tagInfo['artist']
    songFile['album'] = u"华中科技大学国标舞俱乐部曲库"
    songFile['albumartist'] = u"HBDC"
    songFile['year'] = tagInfo['year']
    songFile['genre'] = tagInfo['genre']
    songFile['tracknumber'] = ''
    songFile['discnumber'] = ''
    songFile.save()
    # return True


def SetTag(filePath, title, genre,
           artist=u'HBDC', year=str(datetime.date.today().year), picPath='.\\css\\HBDC2.jpg'):
    with open(picPath, 'rb') as f:
        picData = f.read()
    tagInfo = {
        'picData': picData,
        'title': title,
        'artist': artist,
        'year': year,
        'genre': genre
    }
    Path, extName = os.path.splitext(filePath)
    try:
        if extName == '.mp3':
            SetMp3Info(filePath, tagInfo)
        elif extName == '.wma':
            SetWmaInfo(filePath, tagInfo)
        elif extName == '.ogg':
            SetOggInfo(filePath, tagInfo)
        elif extName == '.flac':
            SetFlacInfo(filePath, tagInfo)
        else:
            return False
        return True
    except Exception as e:
        print(e)


def GetTag(filePath):
    Path, extName = os.path.splitext(filePath)
    try:
        if extName == '.mp3':
                out0 = ID3(filePath)
                # 无法提取年份标签
                # print(out0.keys(),'TCON' in out0.keys())
                # if 'TCON' in out0.keys():
                #     print(out0['TCON'].text)
                genre = None
                if 'TCON' in out0.keys() and out0['TCON'].text:
                    genre = out0['TCON'].text[0]
                tagInfo = {
                    'title': out0['TIT2'].text[0] if 'TIT2' in out0.keys() else None,
                    'artist': out0['TPE1'].text[0] if 'TPE1' in out0.keys() else None,
                    'year': out0['TDRC'].text[0] if 'TDRC' in out0.keys() else None,
                    'genre': genre,
                    'album': out0["TALB"].text[0] if 'TALB' in out0.keys() else None
                }
        elif extName == '.wma':
            out0 = ASF(filePath)
            tagInfo = {
                'title': out0['Title'][0].value if 'Title' in out0.keys() else None,
                'artist': out0['Author'][0].value if 'Author' in out0.keys() else None,
                'year': out0['WM/Year'][0].value if 'WM/Year' in out0.keys() else None,
                'genre': out0['WM/Genre'][0].value if 'WM/Genre' in out0.keys() else None,
                'album': out0["WM/AlbumTitle"][0].value if 'WM/AlbumTitle' in out0.keys() else None
            }
        elif extName == '.ogg':
            out0 = File(filePath)
            tagInfo = {
                'title': out0['title'][0] if 'title' in out0.keys() else None,
                'artist': out0['artist'][0] if 'artist' in out0.keys() else None,
                'year': out0['date'][0] if 'date' in out0.keys() else None,
                'genre': out0['genre'][0] if 'genre' in out0.keys() else None,
                'album': out0["album"][0] if 'album' in out0.keys() else None
            }
        elif extName == '.flac':
            out0 = FLAC(filePath)
            tagInfo = {
                'title': out0['title'][0] if 'title' in out0.keys() else None,
                'artist': out0['artist'][0] if 'artist' in out0.keys() else None,
                'year': out0['year'][0] if 'year' in out0.keys() else None,
                'genre': out0['genre'][0] if 'genre' in out0.keys() else None,
                'album': out0["album"][0] if 'album' in out0.keys() else None
            }
        else:
            tagInfo = {
                'title': None,
                'artist': None,
                'year': None,
                'genre': None,
                'album': None
            }
    except Exception as e:
        print(e)
        tagInfo = {
            'title': None,
            'artist': None,
            'year': None,
            'genre': None,
            'album': None
        }
    return tagInfo


if __name__ == "__main__":

    path = 'C:\\Users\\Yanch\\Desktop\\团圆舞会歌单\\23-慢三-时间煮雨.ogg'
    out0 = File(path)
    # print(out0['metadata_block_picture'])
    print(GetTag(path))
    SetTag(path, 'ti122tle', 'genre')
    out0 = File(path)
    # print(out0)
    # print(out0)

