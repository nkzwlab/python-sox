#!/usr/bin/python
# -*- coding: utf-8 -*-

from pysox.soxdata import SensorMeta, MetaTransducer

def gen_genova_meta_tags():
    genova_meta_tags = []
    gid = 5
    while gid <= 32:
        device = SensorMeta(
            'genova%d' % gid,  # name
            'genova%d' % gid,  # id
            'outdoor weather', # type
            None,              # timestamp
            'genova sensor',   # description
            'genova%d' % gid   # serialNumber
        )

        # latitude, float
        t1 = MetaTransducer(name='latitude', id='latitude')
        device.add_transducer(t1)

        # longitude, float
        t2 = MetaTransducer(name='longitude', id='longitude')
        device.add_transducer(t2)

        # name, string
        t3 = MetaTransducer(name='name', id='name')
        device.add_transducer(t3)

        # id, int
        t4 = MetaTransducer(name='id', id='id')
        device.add_transducer(t4)

        # height, int
        t5 = MetaTransducer(name='height', id='height', units='meter')
        device.add_transducer(t5)

        # temperature, float, celsius
        t6 = MetaTransducer(name='temperature', id='temperature', units='celsius')
        device.add_transducer(t6)

        # wind_chill, float, celsius
        t7 = MetaTransducer(name='wind_chill', id='wind_chill', units='celsius')
        device.add_transducer(t7)

        # humidity, float
        t8 = MetaTransducer(name='humidity', id='humidity', units='percent')
        device.add_transducer(t8)

        # wind_speed, float, kmh
        t9 = MetaTransducer(name='wind_speed', id='wind_speed', units='km/h')
        device.add_transducer(t9)

        # wind_dir, string
        t10 = MetaTransducer(name='wind_dir', id='wind_dir')
        device.add_transducer(t10)

        # wind_dir_deg, float, degree
        t11 = MetaTransducer(name='wind_dir_deg', id='wind_dir_deg', units='degree')
        device.add_transducer(t11)
        
        # atomospheric_pressure, float, hpa
        t12 = MetaTransducer(name='atomospheric_pressure', id='atomospheric_pressure', units='hpa')
        device.add_transducer(t12)
        
        # rain, float, mm/h
        t13 = MetaTransducer(name='rain', id='rain', units='mm/h')
        device.add_transducer(t13)
        
        # dew_point, float, celsius
        t14 = MetaTransducer(name='dew_point', id='dew_point', units='celsius')
        device.add_transducer(t14)

        # last_update, string(date), iso0861
        t15 = MetaTransducer(name='last_update', id='last_update')
        device.add_transducer(t15)

        genova_meta_tags.append(device)

        gid += 1
    return genova_meta_tags


def main():
    genova_meta_tags = gen_genova_meta_tags()
    for device in genova_meta_tags:
        print device.to_string()
        print '\n\n\n'


if __name__ == '__main__':
    main()
