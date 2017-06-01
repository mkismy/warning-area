# -*- coding: utf-8 -*-
import json
import codecs

import geojson
import shapely.geometry
import shapely.ops

import citycode
import estat

citylist = citycode.getlist()

def split01484(name, code):
    if name[2:4] == u'焼尻' or name[2:4] == u'天売':
        return '0148402' # 天売焼尻
    else:
        return '0148401' # 羽幌町

def split01206(name, code):
    if name[:3] == u'阿寒町':
        return '0120602'
    elif name[:3] == u'音別町':
        return '0120603'
    else:
        return '0120601' # 釧路市釧路

def split01208(name, code):
    if int(code) > 1200: # 北見市常呂
        return '0120802'
    else:
        return '0120801' # 北見市北見

def split01233(name, code):
    if int(code) > 400: # 伊達市大滝
        return '0123302'
    else:
        return '0123301' # 伊達市伊達

def split01601(name, code):
    if int(code) <= 40 :
        return '0160101' # 日高町日高
    else:
        return '0160102' # 日高町門別

def split01346(name, code):
    if name[:2] == u'熊石':
        return '0134602' # 八雲町熊石
    else:
        return '0134601' # 八雲町八雲

def split04421(name, code):
    seibu = [u'宮床', u'吉岡', u'吉田']
    if name[:2] in seibu or code == '0090' or code == '0060':
        return '0442102' # 大和町西部
    else:
        return '0442101' # 大和町東部

def split04215(name, code):
    if name[:3] == u'岩出山' or name[:2] == u'鳴子':
        return '0421502' # 大崎市西部
    else:
        return '0421501' # 大崎市東部

def split04213(name, code):
    west = [u'一迫', u'鶯沢', u'栗駒', u'花山']
    if name[:2] in west:
        return '0421302' # 栗原市西部
    else:
        return '0421301' # 栗原市東部


split_areas = [
    #['01484', split01484],
    #['01206', split01206],
    #['01208', split01208],
    #['01233', split01233],
    #['01601', split01601],
    #['01346', split01346],
    #['04421', split04421],
    #['04215', split04215],
    ['04213', split04213],
]

def main():
    for area in split_areas:
        areas = {}
        geojson = estat.get_geojson(area[0])
        load_geojson(geojson, area[1], areas)
        output_geojson(areas)


def split_sendai():
    areas = {}

    geojson1 = estat.get_geojson('04101')
    load_geojson(geojson1, split04101, areas)

    geojson2 = estat.get_geojson('04102')
    load_geojson(geojson2, split0410001, areas)

    geojson3 = estat.get_geojson('04103')
    load_geojson(geojson3, split0410001, areas)

    geojson4 = estat.get_geojson('04104')
    load_geojson(geojson4, split04104, areas)

    geojson5 = estat.get_geojson('04105')
    load_geojson(geojson5, split0410002, areas)

    output_geojson(areas)


def split04101(name, code): # 青葉区
    # 宮城総合支所
    # source http://www.city.sendai.jp/aoba-kusesuishin/aobaku/shokai/profile/shokankuiki.html
    miyagi = [u'赤坂', u'愛子中央', u'愛子東', u'芋沢', u'大倉', u'落合', u'上愛子', u'国見ケ丘', u'熊ケ根', u'栗生', u'郷六', u'作並', u'下愛子', u'高野原', u'中山台', u'中山台西', u'中山吉成', u'錦ケ丘', u'ニツカ', u'新川', u'南吉成', u'みやぎ台', u'向田', u'吉成', u'吉成台', u'臨済院']

    if name in miyagi:
        return '0410002' # 仙台市西部

    elif name[-2:] == u'丁目' and name[:-3] in miyagi:
        return '0410002' # 仙台市西部

    else:
        return '0410001' # 仙台市東部

def split04104(name, code): # 太白区
    # 秋保総合支所
    if name[:3] in u'秋保町':
        return '0410002' # 仙台市西部

    else:
        return '0410001' # 仙台市東部

def split0410001(name, code): # 宮城野区, 若林区
    return '0410001' # 仙台市東部

def split0410002(name, code): # 泉区
    return '0410002' # 仙台市西部



def load_geojson(filename, split_func, areas):
    with open(filename) as f:
        data = json.loads(f.read(), 'utf-8')

        # append splited polygons
        for feature in data['features']:

            if feature['properties']['HCODE'] == 8154: # 水面
                continue
            
            city_name = feature['properties']['CSS_NAME']
            area_name = feature['properties']['MOJI']
            area_code = feature['properties']['KIHON1']

            if area_name[-4:] == u'（湖面）':
                continue

            print area_name, area_code
            code = split_func(area_name, area_code)
            append_geometry(areas, code, feature)


def append_geometry(areas, code, feature):
    if not code in areas:
        areas[code] = []

    poly = shapely.geometry.asShape(feature['geometry'])
    areas[code].append(poly)


def output_geojson(areas):
    for code in areas.keys():
        feature = create_city_geojson(code, areas[code], citylist[code])


def create_city_geojson(code, polygons, meta):
    geometry = shapely.ops.cascaded_union(polygons)
    feature = geojson.Feature(geometry=geometry, properties=meta)

    with open('geojson-split/' + code + '.json', 'w') as f:
        json_str = geojson.dumps(feature, ensure_ascii=False)
        f.write(json_str.encode('utf-8'))

    return feature

if __name__ == '__main__':
    main()
    #split_sendai()


