"""
mf module.  Contains the ModflowGlobal, ModflowList, and Modflow classes.


"""

import os
import sys
import inspect
import flopy
from ..mbase import BaseModel
from ..pakbase import Package
from ..utils import mfreadnam, SpatialReference
from .mfpar import ModflowPar


class ModflowGlobal(Package):
    """
    ModflowGlobal Package class

    """

    def __init__(self, model, extension='glo'):
        Package.__init__(self, model, extension, 'GLOBAL', 1)
        return

    def __repr__(self):
        return 'Global Package class'

    def write_file(self):
        # Not implemented for global class
        return


class ModflowList(Package):
    """
    ModflowList Package class

    """

    def __init__(self, model, extension='list', unitnumber=2):
        Package.__init__(self, model, extension, 'LIST', unitnumber)
        return

    def __repr__(self):
        return 'List Package class'

    def write_file(self):
        # Not implemented for list class
        return


class Modflow(BaseModel):
    """
    MODFLOW Model Class.

    Parameters
    ----------
    modelname : string, optional
        Name of model.  This string will be used to name the MODFLOW input
        that are created with write_model. (the default is 'modflowtest')
    namefile_ext : string, optional
        Extension for the namefile (the default is 'nam')
    version : string, optional
        Version of MODFLOW to use (the default is 'mf2005').
    exe_name : string, optional
        The name of the executable to use (the default is
        'mf2005').
    listunit : integer, optional
        Unit number for the list file (the default is 2).
    model_ws : string, optional
        model workspace.  Directory name to create model data sets.
        (default is the present working directory).
    external_path : string
        Location for external files (default is None).
    verbose : boolean, optional
        Print additional information to the screen (default is False).
    load : boolean, optional
         (default is True).
    silent : integer
        (default is 0)

    Attributes
    ----------

    Methods
    -------

    See Also
    --------

    Notes
    -----

    Examples
    --------

    >>> import flopy
    >>> m = flopy.modflow.Modflow()

    """

    def __init__(self, modelname='modflowtest', namefile_ext='nam',
                 version='mf2005', exe_name='mf2005.exe',
                 structured=True, listunit=2, model_ws='.', external_path=None,
                 verbose=False, **kwargs):
        BaseModel.__init__(self, modelname, namefile_ext, exe_name, model_ws,
                           structured=structured, **kwargs)
        self.version_types = {'mf2k': 'MODFLOW-2000', 'mf2005': 'MODFLOW-2005',
                              'mfnwt': 'MODFLOW-NWT', 'mfusg': 'MODFLOW-USG'}

        self.set_version(version)

        if self.version == 'mf2k':
            self.glo = ModflowGlobal(self)

        self.lst = ModflowList(self, unitnumber=listunit)
        # -- check if unstructured is specified for something
        # other than mfusg is specified
        if not self.structured:
            assert 'mfusg' in self.version, 'structured=False can only be specified for mfusg models'

        # external option stuff
        self.array_free_format = True
        self.array_format = 'modflow'
        # self.external_fnames = []
        # self.external_units = []
        # self.external_binflag = []

        self.verbose = verbose

        self.load_fail = False
        # the starting external data unit number
        self._next_ext_unit = 1000

        if external_path is not None:
            if os.path.exists(os.path.join(model_ws, external_path)):
                print("Note: external_path " + str(external_path) +
                      " already exists")
            else:
                os.makedirs(os.path.join(model_ws, external_path))
        self.external_path = external_path
        self.verbose = verbose
        self.mfpar = ModflowPar()

        # output file info
        self.hext = 'hds'
        self.dext = 'ddn'
        self.cext = 'cbc'
        self.hpth = None
        self.dpath = None
        self.cpath = None

        # Create a dictionary to map package with package object.
        # This is used for loading models.
        self.mfnam_packages = {
            "zone": flopy.modflow.ModflowZon,
            "mult": flopy.modflow.ModflowMlt,
            "pval": flopy.modflow.ModflowPval,
            "bas6": flopy.modflow.ModflowBas,
            "dis": flopy.modflow.ModflowDis,
            "disu": flopy.modflow.ModflowDisU,
            "bcf6": flopy.modflow.ModflowBcf,
            "lpf": flopy.modflow.ModflowLpf,
            "hfb6": flopy.modflow.ModflowHfb,
            "chd": flopy.modflow.ModflowChd,
            "fhb": flopy.modflow.ModflowFhb,
            "wel": flopy.modflow.ModflowWel,
            "mnw2": flopy.modflow.ModflowMnw2,
            "mnwi": flopy.modflow.ModflowMnwi,
            "drn": flopy.modflow.ModflowDrn,
            "rch": flopy.modflow.ModflowRch,
            "evt": flopy.modflow.ModflowEvt,
            "ghb": flopy.modflow.ModflowGhb,
            "gmg": flopy.modflow.ModflowGmg,
            "lmt6": flopy.modflow.ModflowLmt,
            "lmt7": flopy.modflow.ModflowLmt,
            "riv": flopy.modflow.ModflowRiv,
            "str": flopy.modflow.ModflowStr,
            "swi2": flopy.modflow.ModflowSwi2,
            "pcg": flopy.modflow.ModflowPcg,
            "pcgn": flopy.modflow.ModflowPcgn,
            "nwt": flopy.modflow.ModflowNwt,
            "pks": flopy.modflow.ModflowPks,
            "sms": flopy.modflow.ModflowSms,
            "sfr": flopy.modflow.ModflowSfr2,
            "lak": flopy.modflow.ModflowLak,
            "gage": flopy.modflow.ModflowGage,
            "sip": flopy.modflow.ModflowSip,
            "sor": flopy.modflow.ModflowSor,
            "de4": flopy.modflow.ModflowDe4,
            "oc": flopy.modflow.ModflowOc,
            "uzf": flopy.modflow.ModflowUzf1,
            "upw": flopy.modflow.ModflowUpw,
            "sub": flopy.modflow.ModflowSub,
            "swt": flopy.modflow.ModflowSwt,
            "hyd": flopy.modflow.ModflowHyd,
            "hob": flopy.modflow.ModflowHob,
            "vdf": flopy.seawat.SeawatVdf,
            "vsc": flopy.seawat.SeawatVsc
        }
        return

    def __repr__(self):
        nrow, ncol, nlay, nper = self.get_nrow_ncol_nlay_nper()
        return 'MODFLOW %d layer(s), %d row(s), %d column(s), %d stress period(s)' % (
        nlay, nrow, ncol, nper)

    #
    # def next_ext_unit(self):
    #     """
    #     Function to encapsulate next_ext_unit attribute
    #
    #     """
    #     next_unit = self.__next_ext_unit + 1
    #     self.__next_ext_unit += 1
    #     return next_unit

    @property
    def nlay(self):
        if (self.dis):
            return self.dis.nlay
        else:
            return 0

    @property
    def nrow(self):
        if (self.dis):
            return self.dis.nrow
        else:
            return 0

    @property
    def ncol(self):
        if (self.dis):
            return self.dis.ncol
        else:
            return 0

    @property
    def nper(self):
        if (self.dis):
            return self.dis.nper
        else:
            return 0

    @property
    def nrow_ncol_nlay_nper(self):
        # structured dis
        dis = self.get_package('DIS')
        if (dis):
            return dis.nrow, dis.ncol, dis.nlay, dis.nper
        # unstructured dis
        dis = self.get_package('DISU')
        if (dis):
            return None, dis.nodelay.array[:], dis.nlay, dis.nper
        # no dis
        return 0, 0, 0, 0

    def get_nrow_ncol_nlay_nper(self):
        return self.nrow_ncol_nlay_nper

    def get_ifrefm(self):
        bas = self.get_package('BAS6')
        if (bas):
            return bas.ifrefm
        else:
            return False

    def set_ifrefm(self, value=True):
        if not isinstance(value, bool):
            print('Error: set_ifrefm passed value must be a boolean')
            return False
        self.array_free_format = value
        bas = self.get_package('BAS6')
        if (bas):
            bas.ifrefm = value
        else:
            return False

    def _set_name(self, value):
        # Overrides BaseModel's setter for name property
        BaseModel._set_name(self, value)

        if self.version == 'mf2k':
            for i in range(len(self.glo.extension)):
                self.glo.file_name[i] = self.name + '.' + self.glo.extension[i]

        for i in range(len(self.lst.extension)):
            self.lst.file_name[i] = self.name + '.' + self.lst.extension[i]

    def write_name_file(self):
        """
        Write the model name file.

        """
        fn_path = os.path.join(self.model_ws, self.namefile)
        f_nam = open(fn_path, 'w')
        f_nam.write('{}\n'.format(self.heading))
        f_nam.write('#' + str(self.sr))
        f_nam.write(" ;start_datetime:{0}\n".format(self.start_datetime))
        if self.version == 'mf2k':
            if self.glo.unit_number[0] > 0:
                f_nam.write('{:14s} {:5d}  {}\n'.format(self.glo.name[0],
                                                        self.glo.unit_number[0],
                                                        self.glo.file_name[0]))
        f_nam.write('{:14s} {:5d}  {}\n'.format(self.lst.name[0],
                                                self.lst.unit_number[0],
                                                self.lst.file_name[0]))
        f_nam.write('{}'.format(self.get_name_file_entries()))

        # write the external files
        for u, f, b in zip(self.external_units, self.external_fnames,
                           self.external_binflag):
            if u == 0:
                continue
            # fr = os.path.relpath(f, self.model_ws)
            if b:
                f_nam.write(
                    'DATA(BINARY)   {0:5d}  '.format(u) + f + ' REPLACE\n')
            else:
                f_nam.write('DATA           {0:5d}  '.format(u) + f + '\n')

        # write the output files
        for u, f, b in zip(self.output_units, self.output_fnames,
                           self.output_binflag):
            if u == 0:
                continue
            if b:
                f_nam.write(
                    'DATA(BINARY)   {0:5d}  '.format(u) + f + ' REPLACE\n')
            else:
                f_nam.write('DATA           {0:5d}  '.format(u) + f + '\n')

        # close the name file
        f_nam.close()
        return

    def load_results(self, **kwargs):

        # remove model if passed as a kwarg
        if 'model' in kwargs:
            kwargs.pop('model')

        as_dict = False
        if "as_dict" in kwargs:
            as_dict = bool(kwargs.pop("as_dict"))

        savehead = False
        saveddn = False
        savebud = False

        # check for oc
        try:
            oc = self.get_package('OC')
            self.hext = oc.extension[1]
            self.dext = oc.extension[2]
            self.cext = oc.extension[3]
            if oc.chedfm is None:
                head_const = flopy.utils.HeadFile
            else:
                head_const = flopy.utils.FormattedHeadFile
            if oc.cddnfm is None:
                ddn_const = flopy.utils.HeadFile
            else:
                ddn_const = flopy.utils.FormattedHeadFile

            for k, lst in oc.stress_period_data.items():
                for v in lst:
                    if v.lower() == 'save head':
                        savehead = True
                    if v.lower() == 'save drawdown':
                        saveddn = True
                    if v.lower() == 'save budget':
                        savebud = True
        except Exception as e:
            print("error reading output filenames from OC package:{0}". \
                  format(str(e)))
            pass

        self.hpth = os.path.join(self.model_ws,
                                 '{}.{}'.format(self.name, self.hext))
        self.dpth = os.path.join(self.model_ws,
                                 '{}.{}'.format(self.name, self.dext))
        self.cpth = os.path.join(self.model_ws,
                                 '{}.{}'.format(self.name, self.cext))

        hdObj = None
        ddObj = None
        bdObj = None

        if savehead and os.path.exists(self.hpth):
            hdObj = head_const(self.hpth, model=self, **kwargs)

        if saveddn and os.path.exists(self.dpth):
            ddObj = ddn_const(self.dpth, model=self, **kwargs)
        if savebud and os.path.exists(self.cpth):
            bdObj = flopy.utils.CellBudgetFile(self.cpth, model=self, **kwargs)

        # get subsidence, if written
        subObj = None
        try:

            if self.sub is not None and "subsidence.hds" in self.sub.extension:
                idx = self.sub.extension.index("subsidence.hds")
                subObj = head_const(
                    os.path.join(self.model_ws, self.sub.file_name[idx]),
                    text="subsidence")
        except Exception as e:
            print("error loading subsidence.hds:{0}".format(str(e)))

        if as_dict:
            oudic = {}
            if subObj is not None:
                oudic["subsidence.hds"] = subObj
            if savehead and hdObj:
                oudic[self.hpth] = hdObj
            if saveddn and ddObj:
                oudic[self.dpth] = ddObj
            if savebud and bdObj:
                oudic[self.cpth] = bdObj
            return oudic
        else:
            return hdObj, ddObj, bdObj

    @staticmethod
    def load(f, version='mf2005', exe_name='mf2005.exe', verbose=False,
             model_ws='.', load_only=None, forgive=True, check=True):
        """
        Load an existing model.

        Parameters
        ----------
        f : MODFLOW name file
            File to load.
        
        model_ws : model workspace path

        load_only : (optional) filetype(s) to load (e.g. ["bas6", "lpf"])

        forgive : flag to raise exception(s) on package load failure - good for debugging

        check : boolean
            Check model input for common errors. (default True)
        Returns
        -------
        ml : Modflow object

        Examples
        --------

        >>> import flopy
        >>> ml = flopy.modflow.Modflow.load(f)

        """
        # test if name file is passed with extension (i.e., is a valid file)
        if os.path.isfile(os.path.join(model_ws, f)):
            modelname = f.rpartition('.')[0]
        else:
            modelname = f

        # if model_ws is None:
        #    model_ws = os.path.dirname(f)
        if verbose:
            sys.stdout.write('\nCreating new model with name: {}\n{}\n\n'.
                             format(modelname, 50 * '-'))
        ml = Modflow(modelname, version=version, exe_name=exe_name,
                     verbose=verbose, model_ws=model_ws)

        files_succesfully_loaded = []
        files_not_loaded = []

        namefile_path = os.path.join(ml.model_ws, f)

        # set the reference information
        ref_attributes = SpatialReference.load(namefile_path)

        # read name file
        try:
            ext_unit_dict = mfreadnam.parsenamefile(namefile_path,
                                                    ml.mfnam_packages,
                                                    verbose=verbose)
        except Exception as e:
            raise Exception(
                "error loading name file entries from file:\n" + str(e))

        if ml.verbose:
            print('\n{}\nExternal unit dictionary:\n{}\n{}\n'.
                  format(50 * '-', ext_unit_dict, 50 * '-'))

        # reset unit number for glo file
        if version == 'mf2k':
            unitnumber = None
            for key, value in ext_unit_dict.items():
                if value.filetype == 'GLOBAL':
                    unitnumber = key
                    filepth = os.path.basename(value.filename)
            if unitnumber is not None:
                ml.glo.unit_number = [unitnumber]
                ml.glo.file_name = [filepth]
            else:
                ml.glo.unit_number = [0]
                ml.glo.file_name = ['']

        # reset unit number for list file
        unitnumber = None
        for key, value in ext_unit_dict.items():
            if value.filetype == 'LIST':
                unitnumber = key
                filepth = os.path.basename(value.filename)
        if unitnumber is not None:
            ml.lst.unit_number = [unitnumber]
            ml.lst.file_name = [filepth]

        # reset version based on packages in the name file
        for k, v in ext_unit_dict.items():
            if v.filetype == 'NWT' or v.filetype == 'UPW':
                version = 'mfnwt'
            elif v.filetype == 'GLO':
                version = 'mf2k'
            elif v.filetype == 'SMS':
                version = 'mfusg'
            elif v.filetype == 'DISU':
                version = 'mfusg'
                ml.structured = False

        # update the modflow version
        ml.set_version(version)

        # look for the free format flag in bas6
        bas = None
        bas_key = None
        for key, item in ext_unit_dict.items():
            if item.filetype == "BAS6":
                bas = item
                bas_key = key
                break
        if bas_key is not None:
            start = bas.filehandle.tell()
            line = bas.filehandle.readline()
            while line.startswith("#"):
                line = bas.filehandle.readline()
            if "FREE" in line.upper():
                ml.free_format_input = True
            bas.filehandle.seek(start)
        if verbose:
            print("ModflowBas6 free format:{0}\n".format(
                ml.free_format_input))

        # load dis
        disnamdata = None
        dis_key = None
        for key, item in ext_unit_dict.items():
            if item.filetype == "DIS":
                disnamdata = item
                dis_key = key
                break
            if item.filetype == "DISU":
                disnamdata = item
                dis_key = key
                break
        if forgive:
            try:
                dis = disnamdata.package.load(disnamdata.filename, ml,
                                       ext_unit_dict=ext_unit_dict, check=False)
                files_succesfully_loaded.append(disnamdata.filename)
                if ml.verbose:
                    sys.stdout.write('   {:4s} package load...success\n'
                                     .format(dis.name[0]))
                ext_unit_dict.pop(dis_key)
            except Exception as e:
                s = 'Could not read discretization package: {}. Stopping...' \
                    .format(os.path.basename(disnamdata.filename))
                raise Exception(s + " " + str(e))
        else:
            dis = disnamdata.package.load(disnamdata.filename, ml,
                                       ext_unit_dict=ext_unit_dict, check=False)
            files_succesfully_loaded.append(disnamdata.filename)
            if ml.verbose:
                sys.stdout.write('   {:4s} package load...success\n'
                                 .format(dis.name[0]))
            ext_unit_dict.pop(dis_key)
        start_datetime = ref_attributes.pop("start_datetime", "01-01-1970")
        itmuni = ref_attributes.pop("itmuni", 4)
        if ml.structured:
            sr = SpatialReference(delr=ml.dis.delr.array, delc=ml.dis.delc.array,
                                  **ref_attributes)
            dis.lenuni = sr.lenuni
        else:
            sr = None
        dis.sr = sr
        dis.start_datetime = start_datetime
        dis.itmuni = itmuni

        # load bas after dis if it is available so that the free format option
        # is correctly set for subsequent packages.
        if bas_key is not None:
            try:
                pck = bas.package.load(bas.filename, ml,
                                       ext_unit_dict=ext_unit_dict,
                                       check=False)
                files_succesfully_loaded.append(bas.filename)
                if ml.verbose:
                    sys.stdout.write('   {:4s} package load...success\n'
                                     .format(pck.name[0]))
                ext_unit_dict.pop(bas_key)
            except Exception as e:
                s = 'Could not read basic package: {}. Stopping...' \
                    .format(os.path.basename(bas.filename))
                raise Exception(s + " " + str(e))


        if load_only is None:
            load_only = []
            for key, item in ext_unit_dict.items():
                load_only.append(item.filetype)
        else:
            if not isinstance(load_only, list):
                load_only = [load_only]
            not_found = []
            for i, filetype in enumerate(load_only):
                filetype = filetype.upper()
                if filetype != 'DIS' and filetype != 'BAS6':
                    load_only[i] = filetype
                    found = False
                    for key, item in ext_unit_dict.items():
                        if item.filetype == filetype:
                            found = True
                            break
                    if not found:
                        not_found.append(filetype)
            if len(not_found) > 0:
                raise Exception(
                    "the following load_only entries were not found "
                    "in the ext_unit_dict: " + ','.join(not_found))

        # zone, mult, pval
        ml.mfpar.set_pval(ml, ext_unit_dict)
        ml.mfpar.set_zone(ml, ext_unit_dict)
        ml.mfpar.set_mult(ml, ext_unit_dict)

        # try loading packages in ext_unit_dict
        for key, item in ext_unit_dict.items():
            if item.package is not None:
                if item.filetype in load_only and item.filetype != "DIS":
                    if not forgive:
                        if "check" in inspect.getargspec(item.package.load):
                            pck = item.package.load(item.filename, ml,
                                                    ext_unit_dict=ext_unit_dict,
                                                    check=False)
                        else:
                            pck = item.package.load(item.filename, ml,
                                                    ext_unit_dict=ext_unit_dict)
                        files_succesfully_loaded.append(item.filename)
                        if ml.verbose:
                            sys.stdout.write(
                                '   {:4s} package load...success\n'
                                .format(pck.name[0]))
                    else:
                        try:
                            try:
                                pck = item.package.load(item.filename, ml,
                                                        ext_unit_dict=ext_unit_dict,
                                                        check=False)
                            except TypeError:
                                pck = item.package.load(item.filename, ml,
                                                        ext_unit_dict=ext_unit_dict)
                            files_succesfully_loaded.append(item.filename)
                            if ml.verbose:
                                sys.stdout.write(
                                    '   {:4s} package load...success\n'
                                    .format(pck.name[0]))
                        except BaseException as o:
                            ml.load_fail = True
                            if ml.verbose:
                                sys.stdout.write(
                                    '   {:4s} package load...failed\n   {!s}\n'
                                    .format(item.filetype, o))
                            files_not_loaded.append(item.filename)
                else:
                    if ml.verbose:
                        sys.stdout.write('   {:4s} package load...skipped\n'
                                         .format(item.filetype))
                    files_not_loaded.append(item.filename)
            elif "data" not in item.filetype.lower():
                files_not_loaded.append(item.filename)
                if ml.verbose:
                    sys.stdout.write('   {:4s} package load...skipped\n'
                                     .format(item.filetype))
            elif "data" in item.filetype.lower():
                if ml.verbose:
                    sys.stdout.write('   {} file load...skipped\n      {}\n'
                                     .format(item.filetype,
                                             os.path.basename(item.filename)))
                if key not in ml.pop_key_list:
                    # do not add unit number (key) if it already exists
                    if key not in ml.external_units:
                        ml.external_fnames.append(item.filename)
                        ml.external_units.append(key)
                        ml.external_binflag.append("binary"
                                                   in item.filetype.lower())
                        ml.external_output.append(False)

        # pop binary output keys and any external file units that are now
        # internal
        for key in ml.pop_key_list:
            try:
                ml.remove_external(unit=key)
                ext_unit_dict.pop(key)
            except:
                if ml.verbose:
                    sys.stdout.write('Warning: external file unit " +\
                        "{} does not exist in ext_unit_dict.\n'.format(key))

        # write message indicating packages that were successfully loaded
        if ml.verbose:
            print(1 * '\n')
            s = '   The following {0} packages were successfully loaded.' \
                .format(len(files_succesfully_loaded))
            print(s)
            for fname in files_succesfully_loaded:
                print('      ' + os.path.basename(fname))
            if len(files_not_loaded) > 0:
                s = '   The following {0} packages were not loaded.'.format(
                    len(files_not_loaded))
                print(s)
                for fname in files_not_loaded:
                    print('      ' + os.path.basename(fname))
                print('\n')

        if check:
            ml.check(f='{}.chk'.format(ml.name), verbose=ml.verbose, level=0)

        # return model object
        return ml
