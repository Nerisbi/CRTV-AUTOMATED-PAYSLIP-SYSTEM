import pandas as pd

print("=== EXCEL FILE CHECK ===")

try:
    df = pd.read_excel("input/employees.xlsx")
    print(f"Columns: {list(df.columns)}")
    print(f"Rows: {len(df)}")
    print()
    print("Data:")
    for idx, row in df.iterrows():
        print(f"Row {idx+1}:")
        for col in df.columns:
            val = row[col]
            if pd.isna(val):
                val = "[EMPTY]"
            print(f"  {col}: {val}")
        print()
except Exception as e:
    print(f"Error: {e}")
