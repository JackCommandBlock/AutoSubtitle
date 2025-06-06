# -*- coding: utf-8 -*-
import cv2
import itertools
import time
import os
import numpy as np
import configparser
from config import flagStylePath, globalConfigPath, styleSheetPath, flagConfigPath

# import easygui as eg

stylecode = open(flagStylePath, 'r', encoding="utf-8").read()
config = configparser.ConfigParser()
config.read(globalConfigPath)
debug = False if {section: dict(config[section]) for section in config.sections()}['config'][
                     'debug_subtitle'] == "0" else True

# opening_old = ['1000011010001100010000000000000000000000000000000000000000000000',
#                '1100100000010000110010111001011101100100001000000001001011000001',
#                '1100100000010000110010111001011001100100001000000001001011000001']
# opening_new = ['1110010111001100000100010111000010010000000100000001001100000110',
#                '1110010110001110000100110010001010011000000110000000001100000110',
#                '1101010010110011010001111001000101100000000100000011100010000001',
#                '1101010010110011010000111001000101100000000110000011100000000001']
opening_old = ('1010001000010101100010000000010010011001001000001000100000000000', 315, 5)
opening_new = ('1110010111001100000100010111000010010000000100000001001100000110', 184, 2)
opening_3_long = ('1000111010010001100100001100101011000011011000010011001010000110', 1450, 18)
opening_3_short = ('1010101010101100010101010011010100110101100100001010100010001000', 616, 9)
openings = [opening_old, opening_new, opening_3_long, opening_3_short]

subtitle_head = f"""
[Script Info]
Title: AutoSubtitle Aegisub file
ScriptType: v4.00+
WrapStyle: 2
ScaledBorderAndShadow: yes
YCbCr Matrix: None
PlayResX: 1920
PlayResY: 1080

[Aegisub Project Garbage]
Audio File: $$FILE$$
Video File: $$FILE$$

[V4+ Styles]
{stylecode}

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
config2 = configparser.ConfigParser()
config2.read(flagConfigPath, encoding='utf-8')
config_dict = {section: dict(config2[section]) for section in config2.sections()}
for key, subkey in config_dict.items():
    if 'filter_lower' in subkey:
        subkey['filter_lower'] = [int(i) for i in subkey['filter_lower'].split(',')]
    if 'filter_upper' in subkey:
        subkey['filter_upper'] = [int(i) for i in subkey['filter_upper'].split(',')]
    subkey['disabled'] = 'disabled' in subkey and config2.getboolean(key, 'disabled')
# print(config_dict)


def phash(img):
    # 加载并调整图片为32x32灰度图片
    img = cv2.resize(img, (8, 8), interpolation=cv2.INTER_CUBIC)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = img.astype(np.float32)
    # 离散余弦变换
    img = cv2.dct(img)
    hash_str = ''
    img = img[0:8, 0:8]
    avg = sum(img[i, j] for i, j in itertools.product(range(8), range(8)))
    avg = avg / 64
    # 获得hash
    for i, j in itertools.product(range(8), range(8)):
        hash_str = f'{hash_str}1' if img[i, j] > avg else f'{hash_str}0'
    return hash_str


def get_color_rate(frame, lower, upper):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower, upper)
    ratio_green = cv2.countNonZero(mask) / (frame.size / 3)
    colorPercent = (ratio_green * 100)
    return np.round(colorPercent, 2)


def hamming_distance(str1, str2):
    # 计算汉明距离
    if len(str1) != len(str2):
        return 0
    return sum(str1[i] != str2[i] for i in range(len(str1)))


def isset(v):
    try:
        type(eval(v))
    except NameError:
        return 0
    return 1


def frames_to_timecode(framerate, frames):
    # 视频 通过视频帧转换成时间|framerate: 视频帧率|frames: 当前视频帧数|return:时间（00:00:01.001）
    return '{0:02d}:{1:02d}:{2:02d}.{3:02d}'.format(int(frames / (3600 * framerate)),
                                                    int(frames / (60 * framerate) % 60),
                                                    int(frames / framerate % 60),
                                                    int(frames / framerate % 1 * 100))


def get_people(img):
    # mobuo_rate = get_color_rate(img, np.array([101, 125, 212]), np.array([106, 211, 255]))
    # flag_rate = get_color_rate(img, np.array([30, 130, 244]), np.array([35, 205, 255]))
    # renai_rate = get_color_rate(img, np.array([148, 52, 214]), np.array([159, 103, 255]))
    # seizon_rate = get_color_rate(img, np.array([73, 89, 231]), np.array([81, 179, 255]))
    # mobumi_rate = get_color_rate(img, np.array([20, 57, 217]), np.array([28, 120, 255]))
    # lightpurple_rate = get_color_rate(img, np.array([126, 88, 159]), np.array([134, 141, 227]))
    # dongyun_rate = get_color_rate(img, np.array([0, 83, 225]), np.array([10, 125, 255]))
    # yanghong_rate = get_color_rate(img, np.array([159, 168, 198]), np.array([165, 219, 240]))
    # siturenn_rate = get_color_rate(img, np.array([84, 56, 214]), np.array([95, 130, 255]))
    # rose_rate = get_color_rate(img, np.array([168, 122, 172]), np.array([172, 210, 245]))
    # green_rate = get_color_rate(img, np.array([55, 53, 191]), np.array([72, 117, 235]))
    # hametsu_rate = get_color_rate(img, np.array([82, 167, 199]), np.array([87, 247, 255]))
    # # nana_rate = get_color_rate(img, np.array([3, 109, 192]), np.array([11, 183, 250]))
    # nana_rate = get_color_rate(img, np.array([1, 118, 190]), np.array([7, 176, 254]))
    # orange_rate = get_color_rate(img, np.array([3, 109, 192]), np.array([11, 183, 250]))
    # purple_rate = get_color_rate(img, np.array([135, 52, 159]), np.array([147, 145, 225]))
    # red_rate = get_color_rate(img, np.array([164, 139, 195]), np.array([176, 190, 231]))
    # lightpink_rate = get_color_rate(img, np.array([158, 95, 202]), np.array([166, 149, 255]))
    # blue_rate = get_color_rate(img, np.array([117, 96, 194]), np.array([125, 145, 252]))
    # lightgreen_rate = get_color_rate(img, np.array([51, 61, 242]), np.array([62, 131, 255]))
    # kami_rate = get_color_rate(img, np.array([22, 16, 231]), np.array([36, 83, 255]))
    # # 不常用的颜色
    # # winered_rate = get_color_rate(img, np.array([158, 183, 169]), np.array([167, 252, 221]))
    # # darkred_rate = get_color_rate(img, np.array([172, 221, 175]), np.array([177, 255, 233]))
    # # new pattern
    # fen_rate = get_color_rate(img, np.array([2, 161, 191]), np.array([36, 241, 253]))
    # mashiro_rate = get_color_rate(img, np.array([6, 112, 110]), np.array([17, 253, 155]))
    # siratuchi_rate = get_color_rate(img, np.array([176, 213, 190]), np.array([180, 230, 210]))
    # rerooze_rate = get_color_rate(img, np.array([139, 116, 188]), np.array([161, 198, 233]))
    # new pattern
    narrator_rate = get_color_rate(img, np.array([0, 0, 225]), np.array([175, 5, 255]))

    # rate_list = [mobuo_rate, flag_rate, renai_rate, seizon_rate, mobumi_rate, fen_rate, mashiro_rate, siratuchi_rate , rerooze_rate, lightpurple_rate, dongyun_rate,
    #              yanghong_rate, siturenn_rate, rose_rate, green_rate, hametsu_rate, nana_rate,purple_rate, red_rate, lightpink_rate, orange_rate,
    #              blue_rate, lightgreen_rate, kami_rate]
    # people_list = ["mobuo", "flag", "renai", "seizon", "mobumi", "fen", "mashiro", "siratuchi", "rerooze", "lightpurple", "dongyun", "yanghong", "siturenn",
    #                "rose", "green", "hametsu", "nana","purple", "red", "lightpink","orange", "blue", "lightgreen", "kami"]
    people_list = [key for key in config_dict
                   if 'filter_lower' in config_dict[key] and 'filter_upper' in config_dict[key]
                   and not config_dict[key]['disabled']]
    rate_list = [get_color_rate(img, np.array(subkey['filter_lower']), np.array(subkey['filter_upper']))
                 for key, subkey in config_dict.items()
                 if 'filter_lower' in config_dict[key] and 'filter_upper' in config_dict[key]
                 and not config_dict[key]['disabled']]
    # print(dict(zip(people_list, rate_list)))
    max_rate = max(rate_list)
    if max_rate < 0.2:
        if narrator_rate > 25:
            return "narrator"
        else:
            return "undefined"
    # else:
    #     if len([x for x in rate_list if x > 4]) > 1:
    #         return "undefined"
    return people_list[rate_list.index(max_rate)]


# def people2style(people):
#     config = configparser.ConfigParser()
#     config.read(styleSheetPath, encoding='utf-8')
#
#     style_dict = {section: dict(config[section]) for section in config.sections()}['flag']
#     return style_dict[people.lower()]

def people2style(people):
    return config_dict[people]['style']


def add_sub(subtext, begintime, endingtime, subpeople):
    global sub_num
    style = people2style(subpeople)
    newsub = f'Dialogue: 1,{begintime},{endingtime},{style},{subpeople},0,0,0,,{subtext}{str(sub_num) if debug else ""}\n'

    outputFile.write(newsub)
    sub_num += 1


def add_op(frame_rate, begin_frame_num, opType):
    match opType:
        case 0:
            add_sub("没有任何优点的路人男",
                    frames_to_timecode(frame_rate, begin_frame_num),
                    frames_to_timecode(frame_rate, begin_frame_num + (1.62 * frame_rate)), "Opening")
            add_sub("在路人男面前出现的女孩，她的真实身份是...?",
                    frames_to_timecode(frame_rate, begin_frame_num + (1.62 * frame_rate)),
                    frames_to_timecode(frame_rate, begin_frame_num + (4.32 * frame_rate)), "Opening")
            add_sub("死亡flag?",
                    frames_to_timecode(frame_rate, begin_frame_num + (4.32 * frame_rate)),
                    frames_to_timecode(frame_rate, begin_frame_num + (5.52 * frame_rate)), "Opening")
            add_sub("路人男能成功回避死亡flag吗!?",
                    frames_to_timecode(frame_rate, begin_frame_num + (5.52 * frame_rate)),
                    frames_to_timecode(frame_rate, begin_frame_num + (8.22 * frame_rate)), "Opening")
            add_sub("全力回避flag酱!",
                    frames_to_timecode(frame_rate, begin_frame_num + (8.22 * frame_rate)),
                    frames_to_timecode(frame_rate, begin_frame_num + (10.59 * frame_rate)), "Opening")
        case 1:
            add_sub("立起来了!",
                    frames_to_timecode(frame_rate, begin_frame_num + (2.77 * frame_rate)),
                    frames_to_timecode(frame_rate, begin_frame_num + (4.0 * frame_rate)), "Opening")
            add_sub("全力回避flag酱!",
                    frames_to_timecode(frame_rate, begin_frame_num + (4.86 * frame_rate)),
                    frames_to_timecode(frame_rate, begin_frame_num + (6.99 * frame_rate)), "Opening")
        case 2:
            add_sub("flag回收",
                    frames_to_timecode(frame_rate, begin_frame_num + (0.40 * frame_rate)),
                    frames_to_timecode(frame_rate, begin_frame_num + (2.15 * frame_rate)), "narrator")
            add_sub("是引导灵魂走向正确的命运的",
                    frames_to_timecode(frame_rate, begin_frame_num + (2.15 * frame_rate)),
                    frames_to_timecode(frame_rate, begin_frame_num + (4.82 * frame_rate)), "narrator")
            add_sub("天界之使命",
                    frames_to_timecode(frame_rate, begin_frame_num + (4.82 * frame_rate)),
                    frames_to_timecode(frame_rate, begin_frame_num + (6.69 * frame_rate)), "narrator")
            add_sub("而威胁flag回收的存在——",
                    frames_to_timecode(frame_rate, begin_frame_num + (6.69 * frame_rate)),
                    frames_to_timecode(frame_rate, begin_frame_num + (9.23 * frame_rate)), "narrator")
            add_sub("恶魔，从地狱出现了",
                    frames_to_timecode(frame_rate, begin_frame_num + (9.23 * frame_rate)),
                    frames_to_timecode(frame_rate, begin_frame_num + (11.86 * frame_rate)), "narrator")
            add_sub("没能被回收flag的灵魂",
                    frames_to_timecode(frame_rate, begin_frame_num + (11.86 * frame_rate)),
                    frames_to_timecode(frame_rate, begin_frame_num + (14.15 * frame_rate)), "narrator")
            add_sub("会因为走向错误的命运而堕入地狱",
                    frames_to_timecode(frame_rate, begin_frame_num + (14.15 * frame_rate)),
                    frames_to_timecode(frame_rate, begin_frame_num + (17.65 * frame_rate)), "narrator")
            add_sub("为了阻止试图扩大地狱势力的恶魔",
                    frames_to_timecode(frame_rate, begin_frame_num + (17.65 * frame_rate)),
                    frames_to_timecode(frame_rate, begin_frame_num + (20.78 * frame_rate)), "narrator")
            add_sub("flag们今天也要战斗!",
                    frames_to_timecode(frame_rate, begin_frame_num + (20.78 * frame_rate)),
                    frames_to_timecode(frame_rate, begin_frame_num + (22.69 * frame_rate)), "narrator")
            add_sub("绝对回收Death Flag决不放弃",
                    frames_to_timecode(frame_rate, begin_frame_num + (24.48 * frame_rate)),
                    frames_to_timecode(frame_rate, begin_frame_num + (28.04 * frame_rate)), "Opening")
            add_sub("干劲满满!",
                    frames_to_timecode(frame_rate, begin_frame_num + (28.32 * frame_rate)),
                    frames_to_timecode(frame_rate, begin_frame_num + (30.32 * frame_rate)), "Opening")
            add_sub("却总是失败的死神啊!",
                    frames_to_timecode(frame_rate, begin_frame_num + (30.32 * frame_rate)),
                    frames_to_timecode(frame_rate, begin_frame_num + (32.90 * frame_rate)), "Opening")
            add_sub("但是下次一定会成功回收!",
                    frames_to_timecode(frame_rate, begin_frame_num + (32.90 * frame_rate)),
                    frames_to_timecode(frame_rate, begin_frame_num + (35.73 * frame_rate)), "Opening")
            add_sub("绝对回收! 绝对回收! 绝对回收!",
                    frames_to_timecode(frame_rate, begin_frame_num + (35.73 * frame_rate)),
                    frames_to_timecode(frame_rate, begin_frame_num + (37.98 * frame_rate)), "Opening")
            add_sub("Flag绝对回收! 绝对回收!",
                    frames_to_timecode(frame_rate, begin_frame_num + (37.98 * frame_rate)),
                    frames_to_timecode(frame_rate, begin_frame_num + (39.94 * frame_rate)), "Opening")
            add_sub("DeDeDe Death Flag",
                    frames_to_timecode(frame_rate, begin_frame_num + (39.94 * frame_rate)),
                    frames_to_timecode(frame_rate, begin_frame_num + (40.98 * frame_rate)), "Opening")
            add_sub("绝对回收! 绝对回收! 绝对回收!",
                    frames_to_timecode(frame_rate, begin_frame_num + (40.98 * frame_rate)),
                    frames_to_timecode(frame_rate, begin_frame_num + (43.03 * frame_rate)), "Opening")
            add_sub("Flag绝对回收! 绝对回收! Death Flag",
                    frames_to_timecode(frame_rate, begin_frame_num + (43.03 * frame_rate)),
                    frames_to_timecode(frame_rate, begin_frame_num + (48.43 * frame_rate)), "Opening")
        case 3:
            # op_3
            add_sub("绝对回收Death Flag决不放弃",
                    frames_to_timecode(frame_rate, begin_frame_num + (1.708 * frame_rate)),
                    frames_to_timecode(frame_rate, begin_frame_num + (5.3 * frame_rate)), "Opening")
            add_sub("干劲满满!", frames_to_timecode(frame_rate, begin_frame_num + (5.583 * frame_rate)),
                    frames_to_timecode(frame_rate, begin_frame_num + (7.583 * frame_rate)), "Opening")
            add_sub("却总是失败的死神啊!", frames_to_timecode(frame_rate, begin_frame_num + (7.583 * frame_rate)),
                    frames_to_timecode(frame_rate, begin_frame_num + (10.542 * frame_rate)), "Opening")
            add_sub("但是下次一定会成功回收!", frames_to_timecode(frame_rate, begin_frame_num + (10.542 * frame_rate)),
                    frames_to_timecode(frame_rate, begin_frame_num + (13.043 * frame_rate)), "Opening")
            add_sub("绝对回收! 绝对回收! 绝对回收!",
                    frames_to_timecode(frame_rate, begin_frame_num + (13.043 * frame_rate)),
                    frames_to_timecode(frame_rate, begin_frame_num + (15.292 * frame_rate)), "Opening")
            add_sub("Flag绝对回收! 绝对回收!", frames_to_timecode(frame_rate, begin_frame_num + (15.292 * frame_rate)),
                    frames_to_timecode(frame_rate, begin_frame_num + (17.25 * frame_rate)), "Opening")
            add_sub("DeDeDe Death Flag", frames_to_timecode(frame_rate, begin_frame_num + (17.25 * frame_rate)),
                    frames_to_timecode(frame_rate, begin_frame_num + (18.292 * frame_rate)), "Opening")
            add_sub("绝对回收! 绝对回收! 绝对回收!",
                    frames_to_timecode(frame_rate, begin_frame_num + (18.292 * frame_rate)),
                    frames_to_timecode(frame_rate, begin_frame_num + (20.333 * frame_rate)), "Opening")
            add_sub("Flag绝对回收! 绝对回收! Death Flag",
                    frames_to_timecode(frame_rate, begin_frame_num + (20.333 * frame_rate)),
                    frames_to_timecode(frame_rate, begin_frame_num + (25.709 * frame_rate)), "Opening")


# 视频帧总数
current_frame_num = begin_frame_num = last_frame_num = 0
last_pic_hash = ''
op = trans = False
op_start_frame = 0
identity_pass = []

sub_num = 1
Err = False


def autosub(videopath, subpath, opType):
    start = time.time()
    # global op_match_times
    global op
    global op_start_frame
    global trans
    global last_pic_hash
    global current_frame_num
    global begin_frame_num
    global last_frame_num
    global subtitle
    global sub_num
    global current_pic
    global pic_current_hash
    global hamdistant
    global people_pic
    global people
    global Err
    global outputFile
    global identity_pass

    opening = openings[opType]
    outputFile = open(subpath, 'w', encoding='utf-8')
    outputFile.write(subtitle_head.replace("$$FILE$$", os.path.abspath(videopath)))
    source_video = cv2.VideoCapture(videopath)

    if source_video.isOpened():
        frame_rate = round(source_video.get(5), 2)
        while True:
            ret, frame = source_video.read()
            # debug
            # print(current_frame_num)
            # print(phash(frame))

            if not ret:
                break

            current_pic = frame[950:1045, 810:910]
            assert 0 not in current_pic.shape, "视频分辨率应为1920*1080"
            pic_current_hash = phash(current_pic)
            hmdistant = hamming_distance(last_pic_hash, pic_current_hash)

            # switch_pic = frame[940:1060, 360:1540]
            switch_pic = frame[800:900, 300:1620]  # op_3
            switch_hash = phash(switch_pic)

            if not op and hamming_distance(phash(frame), opening[0]) < 10:
                if current_frame_num - last_frame_num > (frame_rate / 2) - 5:

                    center_count = len(identity_pass) // 2 - 1
                    people = get_people(identity_pass[center_count])
                    # people = get_people(people_pic)

                    if people == 'undefined' and current_frame_num - last_frame_num < (frame_rate / 2):
                        pass
                    else:
                        print('%3s | %-5d <-> %-5d | hmdst: %-3d | gap: %-3d | %s --> %s | %s'
                              % (sub_num, begin_frame_num, current_frame_num - 1, hmdistant,
                                 current_frame_num - last_frame_num,
                                 frames_to_timecode(frame_rate, begin_frame_num),
                                 frames_to_timecode(frame_rate, current_frame_num), people))

                        add_sub("示范性字幕" if debug else "", frames_to_timecode(frame_rate, begin_frame_num),
                                frames_to_timecode(frame_rate, current_frame_num), people)

                print('%d-%d | %-5d <-> %-5d | hmdst: %-3d | gap: %-3d | %s --> %s | OP'
                      % (sub_num, sub_num + opening[2] - 1, current_frame_num, current_frame_num + opening[1],
                         hamming_distance(phash(frame), opening[0]),
                         opening[1], frames_to_timecode(frame_rate, current_frame_num),
                         frames_to_timecode(frame_rate, current_frame_num + opening[1] + 1)))

                add_op(frame_rate, current_frame_num, opType)
                op = True
                for i in range(opening[1]):
                    source_video.read()
                begin_frame_num = last_frame_num = current_frame_num = current_frame_num + opening[1]
                identity_pass.clear()

            # if hamming_distance(switch_hash, '1010010011000000101010001100000001000100000001011000011010100000') < 10:

            # op_3
            if hamming_distance(switch_hash, '1100000001000000000000001000001010100000100001010100010101000101') < 10:
                if not trans:
                    add_sub("示范性字幕" if debug else "", frames_to_timecode(frame_rate, begin_frame_num),
                            frames_to_timecode(frame_rate, current_frame_num), people)
                    begin_frame_num = current_frame_num
                    last_frame_num = current_frame_num
                    identity_pass.clear()
                trans = True  # 识别转场

            if (hmdistant > 13) and (current_frame_num != 0):
                if current_frame_num - last_frame_num > (frame_rate / 2) - 5:
                    if not trans:
                        center_count = len(identity_pass) // 2 - 1
                        people = get_people(identity_pass[center_count])
                        # people = get_people(people_pic)
                    else:
                        people = "trans"
                        trans = False
                        # begin_frame_num = begin_frame_num + 1
                        begin_frame_num = begin_frame_num + int(frame_rate / 10) - 3

                    if (people == 'undefined' or people == 'narrator') and current_frame_num - last_frame_num < (
                            frame_rate / 2):
                        pass
                    else:
                        # debug
                        # cv2.imwrite(f'output/{videoName}/frame_{current_frame_num}.jpg', frame)

                        print('%3s | %-5d <-> %-5d | hmdst: %-3d | gap: %-3d | %s --> %s | %s'
                              % (sub_num, begin_frame_num, current_frame_num - 1, hmdistant,
                                 current_frame_num - last_frame_num,
                                 frames_to_timecode(frame_rate, begin_frame_num),
                                 frames_to_timecode(frame_rate, current_frame_num), people))

                        add_sub("示范性字幕" if debug else "", frames_to_timecode(frame_rate, begin_frame_num),
                                frames_to_timecode(frame_rate, current_frame_num), people)

                begin_frame_num = current_frame_num
                last_frame_num = current_frame_num
                identity_pass.clear()

            last_pic_hash = pic_current_hash
            people_pic = frame[940:1040, 800:1100]

            # identify by slide window
            if current_frame_num % 2 == 0:
                identity_pass.append(people_pic)

            current_frame_num += 1
    else:
        print("源视频读取出错")
        Err = True
    print("finish!")

    end = time.time()
    print(f'耗时：{str(end - start)}秒')
    return Err
