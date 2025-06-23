import pandas as pd

df = pd.DataFrame([['Lee', 'A'],
                   ['Lee', 'A+'],
                   ['Lee', 'A+'],
                   ['Col', 'B+'],
                   ['Col', 'A'],
                   ['Col', 'B+']],
                  columns=['name', 'grade']
                 )
                
df.pivot(index='name', columns='grade')

df.insert(0, 'grade_nbr', df.groupby('name').cumcount())

df['grade_nbr'] = 'grade_' + df['grade_nbr'].astype(str)

df.pivot(index='name', columns='grade_nbr', values='grade')
