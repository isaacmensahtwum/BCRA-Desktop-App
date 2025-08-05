import os
os.environ["R_HOME"] = "C:/Program Files/R/R-4.4.2"

import pandas as pd
import rpy2.robjects as ro
from rpy2.robjects import pandas2ri
from rpy2.robjects.packages import importr

def bcra_analysis(patients):
    try:
        col_names = ["ID", "T1", "N_Biop", "HypPlas", "AgeMen", "Age1st", "N_Rels", "Race", "RaceName"]
        Pts_bcra = pd.DataFrame(patients, columns=col_names)

        # Filter age range
        Pts_bcra = Pts_bcra[(Pts_bcra['T1'] >= 20) & (Pts_bcra['T1'] <= 85)]

        # Add required columns
        Pts_bcra.insert(2, 'T2', Pts_bcra['T1'] + 5)
        Pts_bcra.insert(3, 'T3', 90)

        # Transform values
        Pts_bcra["N_Biop"] = Pts_bcra["N_Biop"].replace(99, 0)
        Pts_bcra["AgeMen"] = Pts_bcra["AgeMen"].replace(999, 0)
        Pts_bcra["Age1st"] = Pts_bcra["Age1st"].replace({99: 0, 98: 2})
        Pts_bcra["N_Rels"] = Pts_bcra["N_Rels"].replace(99, 0)

        # Race mapping logic remains the same
        Pts_bcra['Race'] = Pts_bcra['Race'].apply(lambda x: 1 if x == 6 else
                                                  2 if x == 2 else
                                                  3 if x == 9 else
                                                  4 if x in [12, 9821] else
                                                  6 if x == 989 else
                                                  7 if x == 9811 else
                                                  8 if x == 9810 else
                                                  9 if x == 7 else
                                                  10 if x in [8, 9818] else
                                                  11 if x in [1, 984, 9814, 9819] else
                                                  4)

        # R setup
        pandas2ri.activate()
        bcra = importr('BCRA')

        ro.globalenv['Pts_bcra'] = Pts_bcra
        ro.r('''
        library(BCRA)
        Pts_bcra[c("T1", "T2", "T3")] <- lapply(Pts_bcra[c("T1", "T2", "T3")], as.integer)
        Pts_bcra1 <- subset(Pts_bcra, select = c(ID, T1, T2, N_Biop, HypPlas, AgeMen, Age1st, N_Rels, Race))
        Pts_bcra2 <- subset(Pts_bcra, select = c(ID, T1, T3, N_Biop, HypPlas, AgeMen, Age1st, N_Rels, Race))
        colnames(Pts_bcra2)[3] <- "T2"
        Pts_bcra['Five_Year_Risk'] <- round(absolute.risk(Pts_bcra1, Raw_Ind = 0, Avg_White = 0), 2)
        Pts_bcra['Lifetime_Risk'] <- round(absolute.risk(Pts_bcra2, Raw_Ind = 0, Avg_White = 0), 2)
        ''')
        return pandas2ri.rpy2py(ro.r['Pts_bcra'])

    except Exception as e:
        print("Error in bcra_analysis:", e)
        return None
