import os
os.environ["R_Home"] = "C:/Program Files/R/R-4.4.2"

import pandas as pd
import rpy2.robjects as ro
from rpy2.robjects import pandas2ri
from rpy2.robjects.packages import importr

def bcra_analysis(patients):
    try:
        col_names = ["ID", "T1", "N_Biop", "HypPlas", "AgeMen", "Age1st", "N_Rels", "Race", "RaceName"]
        Pts_bcra = pd.DataFrame(patients)
        Pts_bcra.columns = col_names

        Pts_bcra = Pts_bcra[(Pts_bcra['T1'] >=20) & (Pts_bcra['T1'] <= 85)]

        Pts_bcra.insert(2, 'T2', Pts_bcra['T1'] + 5)
        Pts_bcra.insert(3, 'T3', 90)
        Pts_bcra["N_Biop"]=Pts_bcra["N_Biop"].apply(lambda x:0 if x == 99
                                                    # else 1 if x == 1
                                                    # else 2 if 2 <= x < 99
                                                    else x
                                                    )
        # Age at Mernarche is already recoded from the database to match BCRA library except for unknown
        Pts_bcra['AgeMen']=Pts_bcra['AgeMen'].apply(lambda x: 0 if x == 999 #unknown
                                                    # else 1 if 12 <= x < 14
                                                    # else 2 if 7 <= x <= 11
                                                    else x
                                                    )
        # Age at First live Birth is already recoded from the database to match BCRA library except for unknown
        Pts_bcra['Age1st']=Pts_bcra['Age1st'].apply(lambda x:0 if x == 99 #unknown
                                                    else 2 if x == 98 #nulliparous
                                                    else x
                                                    )
        Pts_bcra['N_Rels']=Pts_bcra['N_Rels'].apply(lambda x:0 if x==99 #unknown
                                                    # else 1 if x == 1
                                                    # else 2 if 2 <= x < 99
                                                    else x
                                                    )

        Pts_bcra['Race']=Pts_bcra['Race'].apply(lambda x:1 if x==6 #white
                                                else 2 if x == 2 #black
                                                else 3 if x == 9 # or 5 since both are Hispanic
                                                else 4 if x == 12 or x == 9821 #Others
                                                else 6 if x == 989 #Chinese
                                                else 7 if x == 9811 #Japanese
                                                else 8 if x == 9810 #Filipino
                                                else 9 if x == 7 #Native Hawaiian
                                                else 10 if x == 8 or x == 9818 #Other Pacific Islander
                                                else 11 if x == 1 or x == 984 or x == 9814 or x == 9819 #Asian
                                                else 4 #Others
                                                )
        print("Connecting to R")
        pandas2ri.activate()
        bcra=importr('BCRA')
        utils=importr('utils')
        dplyr=importr('dplyr')
        ro.globalenv['Pts_bcra']=Pts_bcra
        ro.r('''
        library(BCRA)
        Pts_bcra[c("T1", "T2", "T3")] <- lapply(Pts_bcra[c("T1", "T2", "T3")], as.integer)
        Pts_bcra1 <- data.frame(subset(Pts_bcra, select = c("ID", "T1", "T2", "N_Biop", "HypPlas", "AgeMen", "Age1st", "N_Rels", "Race")))
        Pts_bcra2 <- data.frame(subset(Pts_bcra, select = c("ID", "T1", "T3", "N_Biop", "HypPlas", "AgeMen", "Age1st", "N_Rels", "Race")))
        colnames(Pts_bcra2)[3] <- "T2"
        Pts_bcra['Five_Year_Risk'] <- data.frame(round(absolute.risk(Pts_bcra1, Raw_Ind = 0, Avg_White = 0),2))
        Pts_bcra['Lifetime_Risk'] <- data.frame(round(absolute.risk(Pts_bcra2, Raw_Ind = 0, Avg_White = 0),2))
        ''')           

        Pts_bcra = pandas2ri.rpy2py(ro.r['Pts_bcra'])
        return Pts_bcra
    except Exception as e:
        print("Error connecting to R: ", e)


if __name__ == "__main__":
    patients = bcra_analysis()
