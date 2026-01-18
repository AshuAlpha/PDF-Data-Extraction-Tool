import pandas as pd

xls = pd.ExcelFile('Output/extracted_output.xlsx')
print(f'Total sheets: {len(xls.sheet_names)}')
print(f'Sheet names: {xls.sheet_names}\n')

for sheet in xls.sheet_names:
    df = pd.read_excel('Output/extracted_output.xlsx', sheet_name=sheet)
    print(f'\n{"="*50}')
    print(f'Sheet: {sheet}')
    print(f'{"="*50}')
    print(df)
