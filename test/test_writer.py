import datetime

from typedcsv.typedcsv import Header, TypedCsvWriter

def test_save_sample():
    with open('sample.tcsv', 'w', newline='') as fp:
        headers = [Header('name', 'str', 'default|Unknown'),
                   Header('age', 'int', 'default|6'),
                   Header('weight', 'float', 'default|60.25'),
                   Header('join_date', 'datetime', 'strptime|%Y-%m-%d')]
        rowdicts = [{'name':'John',
               'age':24,
               'weight':63.21,
               'join_date': datetime.datetime.strptime('1999-02-15', '%Y-%m-%d')
        },
       {'name': 'Lucy',
        'age': 23,
        'weight': 58,
        'join_date': datetime.datetime.strptime('2000-07-28', '%Y-%m-%d')
        },
       {'name': '',
        'age': '',
        'weight': '',
        'join_date': 'NA'
        }]
        writer = TypedCsvWriter(fp)
        writer.writeheader(headers)
        # writer.writerow(rowdict=rowdicts[0], value_stringify_func_args = {
        #     'join_date': 'strftime|%Y-%m-%d'
        # })
        writer.writerows(rowdicts, value_stringify_func_args = {
            'join_date': 'strftime|%Y-%m-%d'
        })

        writer.write_empty_row()
        headers = [Header('country', '', ''),
                   Header('province', '', 'default|NA'),
                   Header('city', '', ''),
                   Header('population', 'int', 'default|0')]
        writer.writeheader(headers)
        rowdicts = [{
            'country':'China',
            'province':'Guangdong',
            'city':'Guangzhou',
            'population':1000000
        },{
            'country':'China',
            'province':'Guangxi',
            'city':'Guilin',
            'population':200000
        },{
            'country':'America',
            'province':'',
            'city':'NewYork',
            'population':300000
        }]
        writer.writerows(rowdicts)

if __name__ == '__main__':
    test_save_sample()