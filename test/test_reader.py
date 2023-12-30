import datetime

from typedcsv.typedcsv import TypedCsvReader

def test_load_sample():
    with open('../sample.tc', 'r') as fp:
        reader = TypedCsvReader(fp, ignore_value_error=False)
        for row in reader:
            print(row)
            assert isinstance(row['age'], int)
            assert isinstance(row['join_date'], datetime.datetime)
            assert isinstance(row['weight'], float)

if __name__ == '__main__':
    test_load_sample()