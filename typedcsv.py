import datetime
from csv import reader
import re
from collections import namedtuple
import decimal


class TypedCsvReader:
    '''
    Header structure is to store the parsed header cell definition.
    It includes:
     name: textual name of the column,
     type_func: type casting function object and
     convert_func_args: pre-processing function and arguments definition in string.
    '''
    Header = namedtuple('Header', ['name', 'type_func', 'convert_func_args'])

    def __init__(self, f, dialect='excel', ignore_value_error=False, *args, **kwargs):
        '''

        :param f: file descriptor
        :param dialect: csv parsing dialet
        :param ignore_value_error: when catch value error, whether to raise the error or ignore it, i.e. return the original value instead
        :param args: other positional arguments for csv reader
        :param kwargs: other key-value arguments for csv reader
        '''
        self.reader = reader(f, dialect, *args, **kwargs)
        self._headers = None
        self._headernames = None
        self._ignore_value_error = ignore_value_error
        self._last_row_was_empty = True
        self._table_index = -1


    def __iter__(self):
        return self

    def parse_header(self, header_def:str):
        '''
        parse the textual definition of one header cell/column
        :param header_def: textual definition of one header cell
        :return: a tuple including parsed name, type_func, convert_func_args
        '''
        matcher = re.match(r'([^:=]+)(:[^:=]+)?(=[^:=]+)?',header_def)
        if not matcher:
            raise  ValueError("header definition %r can not be parsed" % (header_def,))
        name, type_func, convert_func_args = matcher.groups()
        if type_func is None:
            type_func =':str'
        type_func = type_func[1:].strip()

        if convert_func_args is not None:
            convert_func_args = convert_func_args[1:].strip()

        if hasattr(self, type_func):
            type_func = getattr(self, type_func)
        else:
            raise AttributeError("does not support data type %r" % (type_func, ))

        return name, type_func, convert_func_args


    def update_headers(self, header_row):
        '''
        it is an header row, parse it into Header named tuple
        and update header name list, as well as table index
        :param header_row: an raw row list
        :return:
        '''
        self._headers = []
        for header_def in header_row:
            name, type_func, convert_func_args = self.parse_header(header_def)
            self._headers.append(TypedCsvReader.Header(name, type_func, convert_func_args))
        self._headernames = [header.name for header in self._headers] # update
        self._table_index += 1 # update


    @property
    def header_names(self):
        return self._headernames

    @property
    def table_index(self):
        return self._table_index

    def convert(self, value, convert_func_args_str_definition:str):
        '''
        pre-process the cell value using convert func and other arguments (of str type)
        :param value: value to be processed
        :param convert_func_args_str_definition: separated by "|", first section is the function name to be call
        and such function must accept value as its first parameter
        :return: processed value
        '''
        convert_func, *args = convert_func_args_str_definition.split('|')
        if hasattr(self, convert_func):
            func = getattr(self, convert_func)
            return func(value,*args)
        else:
            raise AttributeError("convert function %r is not defined" % (convert_func,))

    def process_value(self, value, convert_func_args, type_func):
        # 1) pre-process value, most of the time, from str to str
        if convert_func_args:
            value = self.convert(value, convert_func_args)
        # 2) type cast on value, from pre-processed type to the target data type
        if type_func:
            value = type_func(value)
        # 3) return final value
        return value

    def __next_not_empty(self):
        '''
        iterate a csv reader, skip empty row
        since it support storing multiple tables in one file, when a new non-empty row read, it's consider as the
        header of a new table, will update header, as well as table index
        :return: raw content row, or throw StopIteration exception when file reaches to the end
        '''
        for row in self.reader:
            if not row:
                # skip empty row
                self._last_row_was_empty = True
                continue
            else:
                if self._last_row_was_empty:
                    self._last_row_was_empty = False
                    self.update_headers(row) # this is the first row of a new table
                    continue # do not return header row
                else:
                    return row # it is content row
        raise StopIteration

    def __next__(self):
        '''
        read next content row, with proper header info updated
        :return: row as dict
        '''
        row = self.__next_not_empty()

        row = [self.process_value(value, self._headers[i].convert_func_args, self._headers[i].type_func) \
               for i, value in enumerate(row)]
        d = dict(zip(self.header_names, row))
        return d

    def add_func(self,func_name, func_obj):
        '''
        support adding of customized function, for the use of type conversion or value pre-processing
        the function must accept value as its first parameter
        :param func_name: string
        :param func_obj: function object
        :return: None
        '''
        setattr(self, func_name, func_obj)

    #### type/convert functions ####
    def default(self, original_value, default_value):
        if original_value == '':
            # when it's empty value according to csv format, replace it using default_value
            return default_value
        else:
            # otherwise, no change to the original value
            return original_value

    def error_wrapper(func):
        def wrapped(self, value, *args, **kwargs):
            try:
                return func(self, value, *args, **kwargs)
            except ValueError as err:
                if self._ignore_value_error:
                    return value
                else:
                    raise

        return wrapped

    @error_wrapper
    def int(self, value, base='10'):
        return int(value, int(base))

    @error_wrapper
    def float(self, value):
        return float(value)

    @error_wrapper
    def decimal(self, value):
        return decimal.Decimal(value)

    @error_wrapper
    def str(self, value):
        return str(value)

    @error_wrapper
    def datetime(self, value):
        if isinstance(value, datetime.datetime):
            return value
        else:
            # by default, assume datetime string is in iso format, i.e.
            return datetime.datetime.fromisoformat(value)

    @error_wrapper
    def strptime(self, value, format):
        return datetime.datetime.strptime(value, format)

    #### end of type/convert functions ####



# if __name__ == '__main__':
#    with open('sample.tc', 'r') as fp:
#        reader = TypedCsvReader(fp, ignore_value_error=True)
#        for row in reader:
#            print(reader.table_index, row)