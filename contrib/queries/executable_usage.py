#------------------------------------------------------------------------    #
# This python script gets executable usage on SYSHOST grouped by exec name.  #
# Total CPU time used, number of jobs, and number of users of the exec are   #
# shown. Executable with "known" names are shown as all CAPS and grouped     #
# together even if they have different actual exec name / version, other     #
# executables are only grouped by their name.                                #            #
#                                                                            #
# Examples:                                                                  #
#                                                                            #
# 1. Show the help output:                                                   #
#   python executable_usage.py -h                                            #
#                                                                            #
# 2. Get executable usage on Darter for the last 90 days                     #
#   python executable_usage.py darter                                        #
#                                                                            #
# 3. Get executable usage on Darter for specific period                      #
#   python executable_usage.py darter --startdate 2015-03-01 \               #
#          --endate 2015-06-31                                               #
#                                                                            #
# 4. Get executable usage on Darter for the last 90 days, excluding all      #
#    module name with 'ari', 'gcc', and 'craype' in its name                 #
#   python executable_usage.py darter --exclude ari,gcc,craype               #
#                                                                            #
#----------------------------------------------------------------------------#

from __future__ import print_function
import os, sys, re, base64, operator
import MySQLdb, argparse
import time
from datetime import datetime, timedelta
try:
  import configparser
except:
  import ConfigParser as configparser

XALT_ETC_DIR = os.environ.get("XALT_ETC_DIR","./")
ConfigFn = os.path.join(XALT_ETC_DIR,"xalt_db.conf")

parser = argparse.ArgumentParser \
          (description='Get library usage on SYSHOST grouped by module name.\
           The number of linking instances and unique user for each library \
           is displayed. A second table where library version (module name \
           versions) has been agregated is also displayed (assuming module \
           name version is in the form <module_name/version>).')
parser.add_argument \
          ("syshost", metavar="SYSHOST", action="store", \
           help="The syshost for this query.")
parser.add_argument \
          ("--startdate", dest='startdate', action="store", \
           help="exclude everything before STARTDATE (in YYYY-MM-DD). \
                 If not specified, defaults to ENDDATE - 90 days.")
parser.add_argument \
          ("--enddate", dest='enddate', action="store", \
           help="exclude everything after ENDDATE (in YYYY-MM-DD). \
                 If not specified, defaults to today.")
parser.add_argument \
          ("--exclude", dest='patterns', action="store", \
           help="comma separated PATTERN to ignore module name whose \
                 substring matches any of the PATTERNS.")

args = parser.parse_args()

enddate = time.strftime('%Y-%m-%d')
if args.enddate is not None:
  enddate = args.enddate

startdate = (datetime.strptime(enddate, "%Y-%m-%d") - timedelta(90)) \
             .strftime('%Y-%m-%d');
if args.startdate is not None:
  startdate = args.startdate
  
excludePatterns = None
if args.patterns is not None:
  excludePatterns = [x.strip() for x in args.patterns.split(',')]
  
config = configparser.ConfigParser()     
config.read(ConfigFn)

conn = MySQLdb.connect \
         (config.get("MYSQL","HOST"), \
          config.get("MYSQL","USER"), \
          base64.b64decode(config.get("MYSQL","PASSWD")), \
          config.get("MYSQL","DB"))
cursor = conn.cursor()

equiv_patternA = [
    [ r'^1690'                          , '1690*.x*'                       ],
    [ r'^2D_needle'                     , '2D_needle*'                     ],
    [ r'^3D_needle'                     , '3D_needle*'                     ],
    [ r'^A01'                           , 'A0*'                            ],
    [ r'^adcirc'                        , 'ADCIRC*'                        ],
    [ r'^padcirc'                       , 'ADCIRC*'                        ],
    [ r'^AHF-v1\.0'                     , 'AHF-v1.0*'                      ],
    [ r'^arps'                          , 'ARPS*'                          ],
    [ r'^arps_mpi'                      , 'ARPS*'                          ],
    [ r'^pmemd'                         , 'Amber*'                         ],
    [ r'^sander'                        , 'Amber*'                         ],
    [ r'^Analysis016'                   , 'Analysis016*'                   ],
    [ r'^BADDI3'                        , 'BADDI3*'                        ],
    [ r'^CAMx'                          , 'CAMx*'                          ],
    [ r'^c37b1'                         , 'CHARMM*'                        ],
    [ r'^charmm'                        , 'CHARMM*'                        ],
    [ r'^CHNS'                          , 'CHNS*'                          ],
    [ r'^run\.cctm'                     , 'CMAQ_CCTM*'                     ],
    [ r'^cactus_'                       , 'Cactus*'                        ],
    [ r'^chim'                          , 'CHIMERA*'                       ],
    [ r'^chroma'                        , 'Chroma*'                        ],
    [ r'^harom\.parscalar'              , 'Chroma*'                        ],
    [ r'^sm_chroma'                     , 'Chroma*'                        ],
    [ r'^CitcomS'                       , 'CitcomS*'                       ],
    [ r'^CoMD-'                         , 'CoMD*'                          ],
    [ r'^Compute_'                      , 'Compute_Weather_Code*'          ],
    [ r'^cp2k'                          , 'CP2K*'                          ],
    [ r'^DADDI_'                        , 'DADDI*'                         ],
    [ r'^mpi_dbscan'                    , 'DBScan*'                        ],
    [ r'^DCMIP'                         , 'DCMIP*'                         ],
    [ r'^dlpoly'                        , 'DL_POLY*'                       ],
    [ r'^DNS2d'                         , 'DNS2d*'                         ],
    [ r'^enzo'                          , 'ENZO*'                          ],
    [ r'^FIN'                           , 'FIN*'                           ],
    [ r'^FPHC'                          , 'FPHC*'                          ],
    [ r'^flash4'                        , 'Flash4*'                        ],
    [ r'^Floating_Jinhui'               , 'Floating_Jinhui*'               ],
    [ r'^FractionalVaporSaturationTime' , 'FractionalVaporSaturationTime*' ],
    [ r'^FrankWolfe'                    , 'FrankWolfe*'                    ],     
    [ r'^GIZMO'                         , 'GIZMO*'                         ],
    [ r'^GSreturn'                      , 'GSreturn*'                      ],
    [ r'^.*Gadget.*'                    , 'Gadget*'                        ],
    [ r'^GigaPOWERS'                    , 'GigaPOWERS*'                    ],
    [ r'^graph500'                      , 'Graph500*'                      ],
    [ r'^mdrun'                         , 'Gromacs*'                       ],
    [ r'^HF'                            , 'HF*'                            ],
    [ r'^HOPSPACK_-'                    , 'HOPSPACK*'                      ],
    [ r'^xhpcg'                         , 'HPCG*'                          ],
    [ r'^xhpl'                          , 'HPL*'                           ],
    [ r'^IMB-'                          , 'IMB*'                           ],
    [ r'^IceNine'                       , 'IceNine*'                       ],
    [ r'^lmp_'                          , 'LAMMPS*'                        ],
    [ r'^LESPDFISAT'                    , 'LESPDFISAT*'                    ],
    [ r'^lulesh'                        , 'LULESH*'                        ],
    [ r'^Longitudinal-'                 , 'Longitudinal*'                  ],
    [ r'^MHDAM3d_'                      , 'MHDAM3d*'                       ],
    [ r'^su3_'                          , 'MILC*'                          ],
    [ r'^mitgcmuv'                      , 'MITGCM*'                        ],
    [ r'^charmrun'                      , 'NAMD*'                          ],
    [ r'^namd2'                         , 'NAMD*'                          ],
    [ r'^nektar'                        , 'NEKTAR*'                        ],
    [ r'^nrlmol'                        , 'NRLMol*'                        ],
    [ r'^NVT_'                          , 'NVT*'                           ],
    [ r'^[Nn][Ww][Cc]hem'               , 'NWChem*'                        ],
    [ r'^NavStk_'                       , 'NavStk*'                        ],
    [ r'^NewAlgorithm'                  , 'NewAlgorithm*'                  ],
    [ r'^O2case'                        , 'O2case*'                        ],
    [ r'^.*foam.*'                      , 'OpenFOAM*'                      ],
    [ r'^OpenSees'                      , 'OpenSees*'                      ],
    [ r'^OpenSeesSP'                    , 'OpenSees*'                      ],
    [ r'^P-SPH'                         , 'P-SPH*'                         ],
    [ r'^parsec.mpi'                    , 'PARSEC*'                        ],
    [ r'^P_merge_LD'                    , 'P_merge_LD*'                    ],
    [ r'^python'                        , 'Python*'                        ],
    [ r'^qcprog'                        , 'QCHEM*'                         ],
    [ r'^ph.x'                          , 'QE*'                            ],
    [ r'^pw.x'                          , 'QE*'                            ],
    [ r'^READ_WRFNETCDF'                , 'READ_WRFNETCDF*'                ],
    [ r'^[Rr]osetta'                    , 'Rosetta*'                       ],
    [ r'^SAM_ADV_'                      , 'SAM_ADV*'                       ],
    [ r'^SSEPBMPI_3d_'                  , 'SSEPBMPI_3d*'                   ],
    [ r'^Sandia_100_'                   , 'Sandia_100*'                    ],
    [ r'^Sbm_LFP_'                      , 'Sbm_LFP*'                       ],
    [ r'^SesiSol'                       , 'SeisSol*'                       ],
    [ r'^Select_Particles'              , 'Select_Particles*'              ],
    [ r'^Sept1'                         , 'Sept1*'                         ],
    [ r'^siesta'                        , 'Siesta*'                        ],
    [ r'^Spacing'                       , 'Spacing*'                       ],
    [ r'^xspecfem3D'                    , 'SpecFEM3D*'                     ],
    [ r'^Splotch'                       , 'Splotch*'                       ],
    [ r'^Stratified_'                   , 'Stratified*'                    ],
    [ r'^ttmmd'                         , 'TTMMD*'                         ],
    [ r'^TADDI'                         , 'TADDI*'                         ],
    [ r'^T_Matrix'                      , 'T_Matrix*'                      ],
    [ r'^Trispectrum'                   , 'Trispectrum*'                   ],
    [ r'^UT-GMRES'                      , 'UT-GMRES*'                      ],
    [ r'^UT-MOM'                        , 'UT-MOM*'                        ],
    [ r'^UT.*AIM'                       , 'UTAIM*'                         ],
    [ r'[0-9]+_[0-9]+.sh'               , 'Unknown_number_pair.sh*'        ],
    [ r'^vasp'                          , 'VASP*'                          ],          
    [ r'^wps_'                          , 'WPS*'                           ],
    [ r'^global_enkf_wrf'               , 'WRF*'                           ],
    [ r'^wrf'                           , 'WRF*'                           ],
    [ r'^Xvicar'                        , 'Xvicar*'                        ],
    [ r'^a\.out'                        , 'a.out'                          ],
    [ r'ablDyM'                         , 'ablDyM*'                        ],
    [ r'^ah1w'                          , 'ah1w*'                          ],
    [ r'^astrobear'                     , 'astrobear*'                     ],
    [ r'^athena'                        , 'athena*'                        ],
    [ r'^bsr'                           , 'bsr*'                           ],
    [ r'^buoyantBoussinesq'             , 'buoyantBoussines*'              ],
    [ r'^.*cdmft'                       , 'cdmft*'                         ],
    [ r'^citcom'                        , 'citcom*'                        ],
    [ r'^cntor'                         , 'cntor*'                         ],
    [ r'^coawst'                        , 'coawst*'                        ],
    [ r'^com_estimator'                 , 'com_estimator*'                 ],
    [ r'^cp2k\.'                        , 'cp2k*'                          ],
    [ r'^dam_'                          , 'dam*'                           ],
    [ r'^deform_lung'                   , 'deform_lung*'                   ],
    [ r'^dgbte_'                        , 'dgbte*'                         ],
    [ r'^dgsg'                          , 'dgsg*'                          ],
    [ r'^equm-'                         , 'equm*'                          ],
    [ r'^etbm_hartree'                  , 'etbm_hartree*'                  ],
    [ r'^fdtd-engine'                   , 'fdtd-engine*'                   ],
    [ r'^fkqcwl'                        , 'fkqcwl*'                        ],
    [ r'^flw-avni'                      , 'fl2-avni*'                      ],
    [ r'^flamelet[A-Z]'                 , 'flamelet*'                      ],
    [ r'^fmm_'                          , 'fmm*'                           ],
    [ r'^grmhd'                         , 'grmhd*'                         ],
    [ r'^harris2d'                      , 'harris2d*'                      ],
    [ r'^himeno'                        , 'himeno*'                        ],
    [ r'^iblank'                        , 'iblank*'                        ],
    [ r'^ioChann'                       , 'ioChann*'                       ],
    [ r'^ks_spectrum'                   , 'ks_spectrum*'                   ],
    [ r'^laminarSMOKE'                  , 'laminarSMOKE*'                  ],
    [ r'^lassopg'                       , 'lassopg*'                       ],
    [ r'^lbs3d'                         , 'lbs3d*'                         ],
    [ r'^lchgall_'                      , 'lchgall*'                       ],
    [ r'^lesmpi_rankine'                , 'lesmpi_rankine*'                ],
    [ r'^lz_'                           , 'lz*'                            ],
    [ r'^mandel_'                       , 'mandel*'                        ],
    [ r'^mcmc_test'                     , 'mcmc*'                          ],
    [ r'^md3d_'                         , 'md3d*'                          ],
    [ r'^melSplit'                      , 'melSplit*'                      ],
    [ r'^mh1w'                          , 'mh1w*'                          ],
    [ r'^mhray_'                        , 'mhray*'                         ],
    [ r'^molpairs'                      , 'molpairs*'                      ],
    [ r'^ocean[MG]'                     , 'ocean*'                         ],
    [ r'^pelfe_'                        , 'pelfe*'                         ],
    [ r'^perf_cfft'                     , 'perf_cfft*'                     ],
    [ r'^piso'                          , 'piso*'                          ],
    [ r'^polaris_'                      , 'polaris*'                       ],
    [ r'^ramses'                        , 'ramses*'                        ],
    [ r'^ranksort_'                     , 'ranksort*'                      ],
    [ r'^rfcst_'                        , 'rfcst*'                         ],
    [ r'^rocflocm'                      , 'rocflocm*'                      ],
    [ r'^run\.cctm'                     , 'run.cctm*'                      ],
    [ r'^run\.ddm'                      , 'run.ddm*'                       ],
    [ r'^run_3ln'                       , 'run_3ln*'                       ],
    [ r'^run_aedtproc'                  , 'run_aedtproc*'                  ],
    [ r'^sem_model_slice'               , 'sem_model_slice*'               ],
    [ r'^sfmpi'                         , 'sfmpi*'                         ],
    [ r'^smk_'                          , 'smk*'                           ],
    [ r'^sp-mz'                         , 'sp-mz*'                         ],
    [ r'^spmv-'                         , 'spmv*'                          ],
    [ r'^sssp_eval-'                    , 'sssp_eval*'                     ],
    [ r'^toascii.*ksh'                  , 'toascii*'                       ],
    [ r'^v14'                           , 'v14*'                           ],
    [ r'^validation[A-Z0-9]'            , 'validation*'                    ],
    [ r'^varOmega'                      , 'varOmega*'                      ],
    [ r'^vat_2d'                        , 'vat_2d*'                        ],
    [ r'^vat_3d'                        , 'vat_3d*'                        ],
    [ r'^vfmfe'                         , 'vfmfe*'                         ],
    [ r'^virial3'                       , 'virial3*'                       ],
    [ r'^vlpl'                          , 'vlpl*'                          ],
    [ r'^xkhi03'                        , 'xkhi03*'                        ],
    [ r'^xlmg1'                         , 'xlmg1*'                         ],
    [ r'^xpacc'                         , 'xpacc*'                         ],
    [ r'^xsbig'                         , 'xsbig*'                         ],
    [ r'^ymir_'                         , 'ymir*'                          ],
    ]

  sA = []
  sA.append("SELECT CASE \\")
  for entry in equiv_patternA:
    left  = entry[0].lower()
    right = entry[1]
    s     = "WHEN LOWER(SUBSTRING_INDEX(xalt_run.exec_path,'/',-1)) REGEXP '%s' then '%s' \\" % (left, right)
    sA.append(s)

  sA.append(" ELSE SUBSTRING_INDEX(xalt_run.exec_path,'/',-1) END \\")
  sA.append(" AS execname, ROUND(SUM(run_time*num_cores/3600)) as totalcput, \\")
  sA.append(" COUNT(date) as n_jobs, COUNT(DISTINCT(user)) as n_users \\")
  sA.append("   FROM xalt_run \\")
  sA.append("  WHERE syshost = '%s' \\")
  sA.append("    AND date >= '%s 00:00:00' AND date <= '%s 23:59:59' \\")
  sA.append("  GROUP BY execname ORDER BY totalcput DESC")

  query = "\n".join(sA) % (args.syshost, startdate, enddate)

#query = "SELECT CASE \
#       WHEN LOWER(SUBSTRING_INDEX(xalt_run.exec_path,'/',-1)) REGEXP '^1690'             then '1690*.x*'              \
#       WHEN LOWER(SUBSTRING_INDEX(xalt_run.exec_path,'/',-1)) REGEXP '^2d_needle'        then '2D_needle*'            \
#       WHEN LOWER(SUBSTRING_INDEX(xalt_run.exec_path,'/',-1)) REGEXP '^3d_needle'        then '3D_needle*'            \
#       WHEN LOWER(SUBSTRING_INDEX(xalt_run.exec_path,'/',-1)) REGEXP '^a01'              then 'A0*'                   \
#       WHEN LOWER(SUBSTRING_INDEX(xalt_run.exec_path,'/',-1)) REGEXP '^adcirc'           then 'ADCIRC*'               \
#       WHEN LOWER(SUBSTRING_INDEX(xalt_run.exec_path,'/',-1)) REGEXP '^padcirc'          then 'ADCIRC*'               \
#       WHEN LOWER(SUBSTRING_INDEX(xalt_run.exec_path,'/',-1)) REGEXP '^ahf-v1\.0'        then 'AHF-v1.0*'             \
#       WHEN LOWER(SUBSTRING_INDEX(xalt_run.exec_path,'/',-1)) REGEXP '^arps'             then 'ARPS*'                 \
#       WHEN LOWER(SUBSTRING_INDEX(xalt_run.exec_path,'/',-1)) REGEXP '^pmemd'            then 'AMBER*'                \
#       WHEN LOWER(SUBSTRING_INDEX(xalt_run.exec_path,'/',-1)) REGEXP '^sander'           then 'AMBER*'                \
#       WHEN LOWER(SUBSTRING_INDEX(xalt_run.exec_path,'/',-1)) REGEXP '^amber'            then 'AMBER*'                \
#       WHEN LOWER(SUBSTRING_INDEX(xalt_run.exec_path,'/',-1)) REGEXP '^analysis016'      then 'Analysis016*'          \
#       WHEN LOWER(SUBSTRING_INDEX(xalt_run.exec_path,'/',-1)) REGEXP '^baddi3'           then 'BADDI3*'               \
#       WHEN LOWER(SUBSTRING_INDEX(xalt_run.exec_path,'/',-1)) REGEXP '^camx'             then 'CAMx*'                 \
#       WHEN LOWER(SUBSTRING_INDEX(xalt_run.exec_path,'/',-1)) REGEXP '^c37b1'            then 'CHARMM*'               \
#       WHEN LOWER(SUBSTRING_INDEX(xalt_run.exec_path,'/',-1)) REGEXP '^charm'            then 'CHARMM*'               \
#       WHEN LOWER(SUBSTRING_INDEX(xalt_run.exec_path,'/',-1)) REGEXP '^chns'             then 'CHNS*'                 \
#       WHEN LOWER(SUBSTRING_INDEX(xalt_run.exec_path,'/',-1)) REGEXP '^run\.cctm'        then 'CMAQ_CCTM*'            \
#       WHEN LOWER(SUBSTRING_INDEX(xalt_run.exec_path,'/',-1)) REGEXP '^cactus_'          then 'Cactus*'               \
#       WHEN LOWER(SUBSTRING_INDEX(xalt_run.exec_path,'/',-1)) REGEXP '^chroma'           then 'Chroma*'               \
#       WHEN LOWER(SUBSTRING_INDEX(xalt_run.exec_path,'/',-1)) REGEXP '^harom\.parscalar' then 'Chroma*'               \
#       WHEN LOWER(SUBSTRING_INDEX(xalt_run.exec_path,'/',-1)) REGEXP '^sm_chroma'        then 'Chroma*'               \
#       WHEN LOWER(SUBSTRING_INDEX(xalt_run.exec_path,'/',-1)) REGEXP '^citcoms'          then 'CitcomS*'              \
#       WHEN LOWER(SUBSTRING_INDEX(xalt_run.exec_path,'/',-1)) REGEXP '^comd-'            then 'CoMD*'                 \
#       WHEN LOWER(SUBSTRING_INDEX(xalt_run.exec_path,'/',-1)) REGEXP '^compute_'         then 'Compute_Weather_Code*' \
#       WHEN LOWER(SUBSTRING_INDEX(xalt_run.exec_path,'/',-1)) REGEXP '^daddi_'           then 'DADDI*'                \
#       WHEN LOWER(SUBSTRING_INDEX(xalt_run.exec_path,'/',-1)) REGEXP '^mpi_dbscan'       then 'DDScan*'               \
#       WHEN LOWER(SUBSTRING_INDEX(xalt_run.exec_path,'/',-1)) REGEXP '^dcmip'            then 'DCMIP*'                \
#       WHEN LOWER(SUBSTRING_INDEX(xalt_run.exec_path,'/',-1)) REGEXP '^dlpoly'           then 'DL_POLY*'              \
#       WHEN LOWER(SUBSTRING_INDEX(xalt_run.exec_path,'/',-1)) REGEXP '^dns2d'            then 'DNS2d*'                \
#       WHEN LOWER(SUBSTRING_INDEX(xalt_run.exec_path,'/',-1)) REGEXP '^enzo'             then 'ENZO*'                 \
#       WHEN LOWER(SUBSTRING_INDEX(xalt_run.exec_path,'/',-1)) REGEXP '^fin'              then 'FIN*'                  \
#       WHEN LOWER(SUBSTRING_INDEX(xalt_run.exec_path,'/',-1)) REGEXP '^fphc'             then 'FPHC*'                 \
#       WHEN LOWER(SUBSTRING_INDEX(xalt_run.exec_path,'/',-1)) REGEXP '^flash'            then 'Flash4*'               \
#       WHEN LOWER(SUBSTRING_INDEX(xalt_run.exec_path,'/',-1)) REGEXP '^floating_jinhui'  then 'Floating_Jinhui*'      \
#       WHEN LOWER(SUBSTRING_INDEX(xalt_run.exec_path,'/',-1)) REGEXP '^FractionalVaporSaturationTime' then 'FractionalVaporSaturationTime*' \
#       WHEN LOWER(SUBSTRING_INDEX(xalt_run.exec_path,'/',-1)) REGEXP '^frankwolfe'       then 'FrankWolfe*'           \
#       WHEN LOWER(SUBSTRING_INDEX(xalt_run.exec_path,'/',-1)) REGEXP '^gizmo'            then 'GIZMO*'                \
#
#       WHEN LOWER(SUBSTRING_INDEX(xalt_run.exec_path,'/',-1)) REGEXP 'wrf' then 'WRF*' \
#       WHEN LOWER(SUBSTRING_INDEX(xalt_run.exec_path,'/',-1)) REGEXP 'chim' then 'CHIMERA*' \
#       WHEN LOWER(SUBSTRING_INDEX(xalt_run.exec_path,'/',-1)) REGEXP 'vasp' then 'VASP*' \
#       WHEN LOWER(SUBSTRING_INDEX(xalt_run.exec_path,'/',-1)) REGEXP 'namd' then 'NAMD*' \
#       WHEN LOWER(SUBSTRING_INDEX(xalt_run.exec_path,'/',-1)) REGEXP 'lmp' then 'LAMMPS*' \
#       WHEN LOWER(SUBSTRING_INDEX(xalt_run.exec_path,'/',-1)) REGEXP 'gromacs' then 'GROMACS*' \
#       WHEN LOWER(SUBSTRING_INDEX(xalt_run.exec_path,'/',-1)) REGEXP 'cp2k' then 'CP2K*' \
#       WHEN LOWER(SUBSTRING_INDEX(xalt_run.exec_path,'/',-1)) REGEXP 'nwchem' then 'NWCHEM*' \
#       WHEN LOWER(SUBSTRING_INDEX(xalt_run.exec_path,'/',-1)) REGEXP 'ttmmd' then 'TTMMD*' \
#       WHEN LOWER(xalt_run.exec_path)  REGEXP 'genasis' then 'GENASIS*' \
#       WHEN LOWER(SUBSTRING_INDEX(xalt_run.exec_path,'/',-1)) REGEXP 'engine_par' then 'VISIT*' \
#       WHEN LOWER(SUBSTRING_INDEX(xalt_run.exec_path,'/',-1)) REGEXP 'foam' then 'OPENFOAM*' \
#       WHEN LOWER(SUBSTRING_INDEX(xalt_run.exec_path,'/',-1)) REGEXP 'ph.x' then 'Q-ESPRESSO*' \
#       WHEN LOWER(SUBSTRING_INDEX(xalt_run.exec_path,'/',-1)) REGEXP 'pw.x' then 'Q-ESPRESSO*' \
#       ELSE SUBSTRING_INDEX(xalt_run.exec_path,'/',-1) END \
#     AS execname, ROUND(SUM(run_time*num_cores/3600)) as totalcput, \
#     COUNT(date) as n_jobs, COUNT(DISTINCT(user)) as n_users \
#     FROM xalt_run \
#    WHERE syshost = '%s' \
#      AND date >= '%s 00:00:00' AND date <= '%s 23:59:59' \
#    GROUP BY execname ORDER BY totalcput DESC" \
#    % (args.syshost, startdate, enddate)
cursor.execute(query)
results = cursor.fetchall()

print ("")
print ("====================================================================")
print ("%10s %10s %10s %35s" % ("CPU Time.", "# Jobs", "# Users","Exec"))
print ("====================================================================")

sum = 0.0
for execname, totalcput, n_jobs, n_users in results:
  sum += totalcput
  print ("%35s %10s %10s %10s" % (totalcput, n_jobs, n_users,execname))

print("(M) SUs", sum/1.0e6, file=sys.stderr)

