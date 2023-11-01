import pandas as pd
import os

D = []
for file in os.listdir('OUTPUT_CSV'):
    print(file)
    p = 'OUTPUT_CSV/' + file
    d = pd.read_csv(p, sep=';')
    o = d[d['fdr'] <= 0.05]
    se = file[:-4].split('-')
    for i, r in o.iterrows():
        D.append({'id1': r['id1'],
                  'start': se[0],
                  'end': se[1],
                  'Name': r['geneName'],
                  'Function': r['annotation'] if not pd.isna(r['annotation']) else 'hypothetical protein'})
pd.DataFrame(D).to_csv('FDRfilterTargetPred.csv', index=False)

# s= open('OUTPUT_CSV/776246-776381.csv')
# f= s.readlines()
# print(f[91])
# print(f[92])
# print(f[0])

