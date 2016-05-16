#! /usr/bin/env python# Generates all of the possible parameter file combinations for duchamp.# These are stored in the folder specified by "DIR_PARAM".# This file should only need to be run once.import argparseimport osimport sysbase_path = os.path.dirname(__file__)sys.path.append(os.path.abspath(os.path.join(base_path, '..')))from utils.logging_helper import config_loggerfrom database.database_support import PARAMETER_FILEfrom sqlalchemy import create_enginefrom config import DIR_PARAM, DB_LOGINLOGGER = config_logger(__name__)LOGGER.info('Starting generate_parameter_files.py')LOGGER.info('PYTHONPATH = {0}'.format(sys.path))# create a directory of the files with the run_idif not os.path.exists(DIR_PARAM):    os.makedirs(DIR_PARAM)    os.chdir(DIR_PARAM)# fixed parametersImageFile = 'input.fits'flagRejectbeforeMerge = 'true'flagATrous = 'true'flagAdjacent = 'true'# variable parametersoutname = 'duchamp-output'  # !!!!! This needs to be the same name all the time and not altered belowthreshold = [2, 3, 4, 5]  # this is the threshold in sigmasigma = 86e-6for i in range(0, len(threshold), 1):    # noinspection PyAugmentAssignment    threshold[i] = threshold[i] * sigmareconDim = [1, 3]snrRecon = [1, 2]scaleMin = [2, 3]minPix = [10]minChan = [3, 5]flagGrowth = [1, 0]  # grow the sourcesgrowthThreshold = [1, 2]  # this is the grow-threshold in sigmafor i in range(0, len(growthThreshold), 1):    # noinspection PyAugmentAssignment    growthThreshold[i] = growthThreshold[i] * sigmacounter = 0parameters = {}for i in range(0, len(threshold), 1):    for j in range(0, len(reconDim), 1):        for k in range(0, len(snrRecon), 1):            for l in range(0, len(scaleMin), 1):                for m in range(0, len(minPix), 1):                    for n in range(0, len(minChan), 1):                        for o in range(0, len(flagGrowth), 1):                            if flagGrowth[o] == 1:                                for p in range(0, len(growthThreshold), 1):                                    if growthThreshold[p] < threshold[i]:                                        counter += 1                                        parfile = 'supercube_run' + '_' + str(counter) + '.par'                                        if counter < 10000:                                            parfile = 'supercube_run' + '_0' + str(counter) + '.par'                                        if counter < 1000:                                            parfile = 'supercube_run' + '_00' + str(counter) + '.par'                                        if counter < 100:                                            parfile = 'supercube_run' + '_000' + str(counter) + '.par'                                        if counter < 10:                                            parfile = 'supercube_run' + '_0000' + str(counter) + '.par'                                        fileText = 'ImageFile              ' + ImageFile + '\n' + \                                                   'outFile                ' + outname + '_' + parfile + '\n' + \                                                   'flagSeparateHeader      true \n' + \                                                   'flagRejectBeforeMerge  ' + flagRejectbeforeMerge + '\n' + \                                                   'flagATrous             ' + flagATrous + '\n' + \                                                   'flagAdjacent           ' + flagAdjacent + '\n' + \                                                   'threshold              ' + str(threshold[i]) + '\n' + \                                                   'reconDim               ' + str(reconDim[j]) + '\n' + \                                                   'snrRecon               ' + str(snrRecon[k]) + '\n' + \                                                   'scaleMin               ' + str(scaleMin[l]) + '\n' + \                                                   'minPix                 ' + str(minPix[m]) + '\n' + \                                                   'minChannels            ' + str(minChan[n]) + '\n' + \                                                   'flagGrowth              true \n' + \                                                   'growthThreshold        ' + str(growthThreshold[p]) + '\n'                                        parameters[parfile] = fileText                            if flagGrowth[o] == 0:                                counter += 1                                parfile = 'supercube_run' + '_' + str(counter) + '.par'                                if counter < 10000:                                    parfile = 'supercube_run' + '_0' + str(counter) + '.par'                                if counter < 1000:                                    parfile = 'supercube_run' + '_00' + str(counter) + '.par'                                if counter < 100:                                    parfile = 'supercube_run' + '_000' + str(counter) + '.par'                                if counter < 10:                                    parfile = 'supercube_run' + '_0000' + str(counter) + '.par'                                fileText = 'ImageFile              ' + ImageFile + '\n' + \                                           'outFile                ' + outname + '_' + parfile + '\n' + \                                           'flagSeparateHeader      true \n' + \                                           'flagRejectBeforeMerge  ' + flagRejectbeforeMerge + '\n' + \                                           'flagATrous             ' + flagATrous + '\n' + \                                           'flagAdjacent           ' + flagAdjacent + '\n' + \                                           'threshold              ' + str(threshold[i]) + '\n' + \                                           'reconDim               ' + str(reconDim[j]) + '\n' + \                                           'snrRecon               ' + str(snrRecon[k]) + '\n' + \                                           'scaleMin               ' + str(scaleMin[l]) + '\n' + \                                           'minPix                 ' + str(minPix[m]) + '\n' + \                                           'minChannels            ' + str(minChan[n]) + '\n' + \                                           'flagGrowth              false \n'                                parameters[parfile] = fileText# create all output filesengine = create_engine(DB_LOGIN)connection = engine.connect()for k, v in parameters.iteritems():    # k is parameter file name, v is file contents.    try:        LOGGER.info('Creating file {0}'.format(k))        with open(k, 'w') as newfile:            newfile.write(v)        LOGGER.info('Registering file in the DB')        connection.execute(PARAMETER_FILE.insert(parameter_file=k))    except Exception as e:        LOGGER.info('Could not insert in to database: {0}'.format(e.message))