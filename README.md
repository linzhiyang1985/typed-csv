# typed-csv
## Typed CSV
### Propose a csv based file format with type information in header
1. File extension is **.tc** or **.tcsv**.
2. It stores one or more **table(s)**. Tables are separated by at least one empty line.
3. Table must contain **header**.
4. Header contains **cell(s)** that are separated by **,(comma)** symbol. Since comma is a preserved symbol, when content in table contains comma should follow csv dialect.
5. In cell, it contains **header name**, and **data type** information. Optionally, **data conversion function** follows, separating them using a **=**. For example:
> name:str=default|Unknown,age:int=default|6,join_date:datetime=format|%Y-%m-%d,weight:float=default|60.25
6. When parsing content row, iterate each cell. Firstly, use **data convert function** and its **arguments** to pre-process the raw value, output will be still in string format; next, use **type function** to cast pre-processed string, the output is the final cell value
