"""-------------------------------------------------------------------

MODULE
    FDLSetupValidation - Testme script

DESCRIPTION
    Test setup script to check setup for DataLoader

--------------------------------------------------------------------"""

import acm
import ael
import amb
import os
import string

import FDLFTPClient
from FDLWebClient import FDLWebClient
from FSFTPOperations import SFTPOperations
from FDLOpenFIGI import OpenFigiData
import FIntegrationUtils

utils_obj = FIntegrationUtils.FIntegrationUtils()


def event_cb_amb(channel, event, arg):
    """ Callback function that is called to process each message"""
    (channel,amb.mb_event_type_to_string(event.event_type))
    eventstring= amb.mb_event_type_to_string(event.event_type)
    if eventstring == 'Message':
        amb.mb_queue_accept(channel, event.message,'ok')
    elif eventstring == 'Status':
        pass
    elif eventstring == 'Disconnect':
        ael.log("AMB disconnected")
    else:
        ael.log('AMB unknown event')


class DataloaderSetupValidation():

    def  __init__(self, logger, provider, config_variables_obj):
        self.logger = logger
        self.config_variables_obj = config_variables_obj
        self.config = config_variables_obj.config_data()
        self.provider = provider

    def check_amb_connection(self):
        error_msg = ''
        self.logger.debug("Checking amb connection")
        is_connected = False
        amb_address = self.config.get("MESSAGE_BROKER_ex")
        try:
            amb.mb_init(amb_address)
            self.logger.info("Successfully Connected to AMB {}".format(amb_address))
            is_connected = True
        except Exception as ex:
            error_msg = "Unable to connect to AMB with {0}, set in FParameter {1}".format(amb_address, "MESSAGE_BROKER_ex")
            self.logger.error(error_msg)

        if is_connected:
            return is_connected
        else:
            return error_msg

    def check_ats_and_amba_version(self):
        ats_version_compatible = False
        amba_version_compatible = False
        error_log = ''
        app_versions = self.get_connected_application()
        prime_ver = app_versions.get('PRIME')
        ats_ver = app_versions.get('ATS')
        amba_ver = app_versions.get('AMBA')
        self.logger.debug("PRIME version: {}".format(prime_ver))
        self.logger.debug("ATS version: {}".format(ats_ver))
        self.logger.debug("AMBA version: {}".format(amba_ver))

        if ats_ver:
            if prime_ver >= 2019.4 and ats_ver >= 2019.4:
                ats_version_compatible = True
            elif prime_ver <= 2019.3 and ats_ver <= 2019.3:
                ats_version_compatible = True
            else:
                error_log += "ATS: {} not compatible, ".format(ats_ver)
        else:
            error_log += "ATS for Dataloader is not running, "

        if amba_ver:
            if prime_ver >= 2019.4 and amba_ver >= 2019.4:
                amba_version_compatible = True
            elif prime_ver <= 2019.3 and amba_ver <= 2019.3:
                amba_version_compatible = True
            else:
                error_log += "AMBA: {} not compatible".format(amba_ver)
        else:

            error_log += "AMBA for Dataloader is not running, "

        if error_log:
            error_log += "with Prime {}".format(prime_ver)

        if amba_version_compatible == True and ats_version_compatible == True:
            self.logger.info(
                "ATS:{} and AMBA:{} versions are compatible with Prime:{} version".format(ats_ver, amba_ver, prime_ver))
            return True
        else:
            self.logger.error(error_log)
            return error_log

    def openfigi_api_connection(self):
        res = False
        sec_id_type = 'ISIN'
        sec_id = 'US5949181045'
        fd = OpenFigiData(sec_id_type, sec_id)
        if fd.resp_error_code == 401:
            res = 'Apikey is invalid.'
        else:
            res = True
        return res
    
    def get_connected_application(self):
        app_version = {}
        for con_user in acm.ConnectedUsers():
            acm_user = con_user['Application']
            app_ver = ".".join(acm_user.rstrip(string.ascii_letters).split(".")[0:2])
            app_ver_float = float(app_ver.split('_')[-1])
            if app_ver.upper().startswith('ATS'):
                app_version['ATS'] = app_ver_float
            elif app_ver.upper().startswith('AMBA'):
                app_version['AMBA']  = app_ver_float
            elif app_ver.upper().startswith('PRIME'):
                app_version['PRIME']  = app_ver_float
        return app_version

    def check_user_context_parameters(self):
        fparam_user_context = ['PROVIDER_DATA_FILE_PATH']
        test_file_name = "Provider_Data_{}.txt".format(self.provider)
        error_msg = ''
        for fparam in fparam_user_context:
            provider_file_path = self.config.get(fparam)
            self.logger.info("Checking provider data file path set in FParameter {}".format(fparam))
            if os.path.exists(provider_file_path):
                try:
                    file_path = os.path.join(provider_file_path, test_file_name)
                    f = open(file_path, 'w')
                    f.close()
                    os.remove(file_path)
                    self.logger.info(
                        "User has write permission of path:{} set in FParameter: {}".format(provider_file_path, fparam))
                except IOError as ex:
                    error_msg = "User does not has write permission to path:{} set in FParameter: {}".format(
                        provider_file_path, fparam)
                    self.logger.error(error_msg)
                    self.logger.error(str(ex))
            else:
                error_msg = "Provider data file path: {} set in FParameter: {} does not exist".format(
                    provider_file_path, fparam)
                self.logger.error(error_msg)

        if error_msg:
            return error_msg
        else:
            return True

    def check_sftp_connection(self):
        status =0
        self.logger.debug("Checking SFTP connection")
        data_file_path = os.path.join(self.config['DATA_FILE_PATH_ex'], self.provider)
        host = self.config['SFTP_HOST']
        port = self.config['SFTP_PORT']
        user = self.config['FTP_USER']
        pwd = self.config['FTP_PASSWORD']
        app_name = self.config['APPLICATION_NAME']
        proxy_hostname = self.config['SFTP_PROXY_HOSTNAME'] 
        proxy_portnumber = self.config['SFTP_PROXY_PORTNAME']
        connection_fparams = ['BBG_SFTP_HOST', 'BBG_SFTP_PORT', 'BBG_FTP_USER', 'BBG_FTP_PASSWORD']
        try:        
            from chilkat import chilkat  
            
            obj = SFTPOperations(app_name, host, port, user, pwd, proxy_hostname=proxy_hostname, proxy_portnumber=proxy_portnumber)   
                      
        except ImportError as ex: 
            t,v,tb = sys.exc_info()
            msg = traceback.format_exception(t,v,tb)
            self.logger.info("Could not import chilkat, Please copy chilkat from Dependencies folder and place it in PythonExtension37 folder of FrontArena")
            
        
        if str(obj.sftp.lastErrorText()).__contains__('Received SUCCESS response to subsystem request'):
            self.logger.info("Succesfully connected to {} via SFTP".format(self.provider))
            status =1
        return status

    def check_webservice_connection(self):
        self.logger.debug("Checking Web Services connection")
        is_connected = False
        try:
            web_client_obj = FDLWebClient(self.config_variables_obj)

            if web_client_obj.web_client:
                self.logger.info("Succesfully connected to web services")
                is_connected = True
            else:
                self.logger.error("Can not connect to web services")
        except Exception as ex:
            self.logger.error("Can not connect to web services : {}".format(str(ex)) )
            try:
                import zeep
            except Exception as ex:
                self.logger.error("Can not connect to web services : {}".format(str(ex)))

        return is_connected

    def check_marketmap_connection(self):
        is_connected = False
        self.logger.debug("Checking connection to MarketMap")
        #['MM_CATAPULT_GROUP', 'MM_CATAPULT_PASSWORD', 'MM_CATAPULT_HOST', 'MM_CATAPULT_USER',
        connection_fparams = ['MM_CATAPULT_HOST', 'MM_LOCAL_PROXY_USER', 'MM_LOCAL_PROXY_PASSWORD', 'MM_LOCAL_PROXY_HOST', 'MM_LOCAL_PROXY_PORT']
        self.logger.info("Checking connection to MarketMap")
        host = self.config['MM_CATAPULT_HOST']
        #self.catapult_host = self.catapult_host.strip("https://")
        try:
            obj = FDLFTPClient.FDLMarketMapClient(config_variables_obj)
            if obj.valid_proxy and obj.valid_credentials:
                is_connected = True
        except Exception as ex:
            self.logger.info("Can not connect to MarketMap, {}".format(str(ex)))
            self.logger("Please check FParameters {}".format(connection_fparams))
        if is_connected:
            self.logger.info("Successfully connected to MarketMap {}".format(host))
        return is_connected

    def check_data_provider_connection(self):
        self.logger.debug("Checking Data Provider connection")
        is_connected = False
        error_message = ''
        if self.provider == 'Bloomberg':
            if self.config.get('BBG_USE_WEB_SERVICE'):
                is_connected = self.check_webservice_connection()

            elif not self.config.get('BBG_USE_FTP'):                
                is_connected = self.check_sftp_connection()                
        elif self.provider == 'Refinitiv':
            if not self.config.get('RDS_USE_FTP'):                
                is_connected = self.check_sftp_connection()                
        elif self.provider == 'MarketMap':
            is_connected = self.check_marketmap_connection()

        if is_connected:
            return is_connected
        else:
            return "Can not connect to {}".format(self.provider)

    def check_addinfos(self, addinfo_list):
        self.logger.debug("Checking Additional Info")
        missing_addinfos = []
        #addinfo_list = addinfo_dict.get(entity, [])
        if not addinfo_list:
            self.logger.error("Additional Info(s) invalid for DataLoader")
            return False

        for each_addinfo in addinfo_list:
            addinfo = each_addinfo.get('FieldName')
            entity = each_addinfo.get('Table')
            self.logger.debug("Checking additional info for {}".format(entity))
            try:
                addinfo_res = acm.FAdditionalInfoSpec[addinfo]
                #addinfo_res = acm.FAdditionalInfo.Select("addInf={}".format(addinfo))
                if addinfo_res:
                    self.logger.info("Additional info {} is present".format(addinfo))
                else:
                    missing_addinfos.append(addinfo)
            except Exception as ex:
                self.logger.error("Additional info {} is not present : {}".format(addinfo, str(ex)))
                missing_addinfos.append(addinfo)
        if missing_addinfos:
            error_mesage = "Additional info: {} are not present".format(missing_addinfos)
            self.logger.error(error_mesage)
            return error_mesage
        else:
            return True


    def check_aliases(self, alias_types):
        self.logger.info("Checking Aliases required for - {}".format(self.provider))
        missing_aliases = []
        for each_alias_type in alias_types:
            try:
                alias_type = each_alias_type.get('FieldName')
                entity = each_alias_type.get('Table')
                self.logger.debug("Checking Aliases for {}".format(entity))
                self.logger.debug("Checking for Alias type {}".format(alias_type))
                if entity == 'Instrument':
                    acmAlias = acm.FInstrAliasType.Select("name='%s'" % alias_type)
                    if acmAlias:
                        self.logger.info("Alias type {} is present".format(alias_type))
                    else:
                        missing_aliases.append(alias_type)
                elif entity == 'Party':
                    acmAlias = acm.FPartyAliasType.Select("name='%s'" % alias_type)
                    if acmAlias:
                        self.logger.info("Alias type {} is present".format(alias_type))
                    else:
                        missing_aliases.append(alias_type)
            except Exception as ex:
                self.logger.error("Alias type {0} is not present : {1}".format(alias_type, str(ex)))
                missing_aliases.append(alias_type)
        if missing_aliases:
            error_message = "Alias types {} are not present".format(missing_aliases)
            self.logger.error(error_message)
            return error_message
        else:
            return True


    def check_choice_list(self):
        self.logger.debug("Checking Ratings choicelist")
        ratings_choicelist = ['Moodys', 'S&P', 'OurRate']
        missing_ratings = []
        error_msg = ''
        for each_rating in ratings_choicelist:
            try:
                query = "list = '%s' and name ='%s'" %('MASTER', each_rating)
                choicelist = acm.FChoiceList.Select01(query, None)
                #choicelist = acm.FChoiceList.Select("list={}".format(each_rating))
                if choicelist:
                    self.logger.info("Rating choicelist {} is present".format(each_rating))
                else:
                    missing_ratings.append(each_rating)
            except Exception as ex:
                self.logger.error("Rating choicelist {0} is not present in db : {1}".format(each_rating, str(ex)))
                missing_ratings.append(each_rating)
        if missing_ratings:
            error_msg = "Rating choicelist(s) {} are not present in db".format(missing_ratings)
            self.logger.error(error_msg)
        if not missing_ratings:
            return True
        else:
            return error_msg

    def check_amb_channels(self, component):
        dl_writer_channels = ['{}_SENDER'.format(self.config['MESSAGE_GROUP'].strip()),
                   '{}_REQUEST_SND'.format(self.config['MESSAGE_GROUP'].strip()),
                   'NOTIFY_SENDER',
                   ]
        dl_reader_channels = ['{}_REQUEST_RCV'.format(self.config['MESSAGE_GROUP'].strip()),
                    'NOTIFY_{}'.format(acm.UserName())]

        missing_channel = []
        res = True
        is_connected = self.check_amb_connection()
        if is_connected and component == 'DataLoader':
            for channel_name in dl_writer_channels:
                try:
                    handle = amb.mb_queue_init_writer(channel_name, event_cb_amb, None)
                    if handle:
                        self.logger.info("channel {} is present for sending messages to AMB".format(channel_name))
                    else:
                        self.logger.error("Cannot open channels {0} for sending messages to AMB : {1}".format(channel_name, str(e)))
                        missing_channel.append(channel_name)
                except Exception as e:
                    missing_channel.append(channel_name)

            for channel_name in dl_reader_channels:
                try:
                    handle = amb.mb_queue_init_reader(channel_name, event_cb_amb, None)
                    if handle:
                        self.logger.info("channel {} is present for sending messages to AMB".format(channel_name))
                    else:
                        missing_channel.append(channel_name)

                except Exception as e:
                    self.logger.error("Cannot open channels {0} for reading messages from AMB : {1}".format(channel_name, str(e)))
                    missing_channel.append(channel_name)

        elif is_connected and component == 'Autolink':
            channel_name = 'Autolink_Reader'
            try:
                handle = amb.mb_queue_init_reader(channel_name, event_cb_amb, None)
                if handle:
                    self.logger.info("channel {} is present for sending messages to AMB".format(channel_name))
                else:
                    missing_channel.append(channel_name)

            except Exception as e:
                self.logger.error("Cannot open channels {0} for reading messages from AMB : {1}".format(channel_name, str(e)))
                missing_channel.append(channel_name)
        else:
            res = False

        if missing_channel:
            error_msg = "Channel: {} are not found in system table in amb db".format(missing_channel)
            self.logger.error(error_msg)
            res = error_msg
        return res

    def check_default_instrument(self, default_instrument_types):
        missing_default = []
        missing_def_entiites = ""
        for ins_type in default_instrument_types:
            def_ins_name = ins_type
            if ins_type != 'DUMMY_UNDERLYING':
                def_ins_name = ins_type + 'Default'

            ins = acm.FInstrument.Select('name={}'.format(def_ins_name))
            if ins:
                self.logger.info("Default instrument:{} is present in db".format(def_ins_name))
            else:
                missing_default.append(def_ins_name)
        if missing_default:
            missing_def_entiites += "Missing default instrument {}\n".format(missing_default)
            self.logger.warn("Default instrument(s): {} are not present in db".format(missing_default))
            missing_default = []

        if self.provider in ['Bloomberg', 'Refinitiv']:
            default_vola_dict = {'Bloomberg' : ['Equity', 'Commodity', 'FX'], 'Refinitiv' : ['FX']}
            default_vola_types = default_vola_dict.get(self.provider)
            for ins_type in default_vola_types:
                def_vola_name = ins_type + 'Default'
                vol = acm.FVolatilityStructure.Select('name={}'.format(def_vola_name))
                if vol:
                    self.logger.info("Default Volatility Surface :{} is present in db".format(def_vola_name))
                else:
                    missing_default.append(def_vola_name)
            if missing_default:
                missing_def_entiites += "Missing default volatility surface {}\n".format(missing_default)
                self.logger.warn("Default volatility surface(s): {} are not present in db".format(missing_default))
                missing_default = []

        if self.provider == 'Bloomberg':
            yc = acm.FYieldCurve.Select('name={}'.format('DEFAULT'))
            if yc:
                self.logger.info("Default yield curve :{} is present in db".format('DEFAULT'))
            else:
                missing_default.append('DEFAULT')
            if missing_default:
                missing_def_entiites += "Missing default yield curve {}\n".format(missing_default)
                self.logger.warn("Default yield curve: {} is not present in db".format(missing_default))

        if missing_def_entiites:
            return missing_def_entiites
        else:
            return True

    def check_Price_config(self):
        self.logger.debug("Checking the price settings")
        error_msg = ''
        price_semantic = None
        price_dist = None
        price_market = None
        fparam_semantic = self.config.get('PRICE_SEMANTIC_ex', '')
        if fparam_semantic:
            self.logger.info("Checking price semantic in db")
            try:
                price_semantic = acm.FPriceSemantic[fparam_semantic]
                if price_semantic:
                    self.logger.info("Price semantic: {} is present in db".format(fparam_semantic))
                else:
                    self.logger.error("Price semantic: {} is not present in db".format(fparam_semantic))
                    error_msg = "Price semantic: {} is not present in db\n".format(fparam_semantic)
            except Exception as ex:

                self.logger.error("Price semantic: {0} is not present in db : {1}".format(fparam_semantic, str(ex)))
        else:
            error_msg = "FParameter {} value is not set\n".format('PRICE_SEMANTIC_ex')
            self.logger.error(error_msg)


        fparam_distributor = self.config.get('PRICE_DISTRIBUTOR_ex', '')
        if fparam_distributor:
            self.logger.info("Checking price distributor in db")
            try:
                price_dist = acm.FPriceDistributor[fparam_distributor]
                if price_dist:
                    self.logger.info("Price distributor: {} is present in db".format(fparam_distributor))
                    price_dist = True
                else:
                    self.logger.error("Price distributor: {} is not present in db\n".format(fparam_distributor))
                    error_msg += " Price distributor: {} is not present in db\n".format(fparam_distributor)
            except Exception as ex:
                self.logger.error("Price distributor: {0} is not present in db : {1}".format(fparam_distributor, str(ex)))
        else:
            error_msg += "FParameter {} value is not set\n".format('PRICE_DISTRIBUTOR_ex')
            self.logger.error("FParameter {} value is not set".format('PRICE_DISTRIBUTOR_ex'))

        fparam_market = self.config.get('MARKET_UPLOAD_ex')
        self.logger.info("Checking Market place")
        if fparam_market:
            try:
                price_market = acm.FMarketPlace[fparam_market]
                if price_market:
                    self.logger.info("Market Place : {} is present in db".format(fparam_market))
                    price_market = True
                else:
                    self.logger.error("Market Place : {} is not present in db".format(fparam_market))
                    error_msg += "Market Place : {} is not present in db\n".format(fparam_market)
            except Exception as ex:
                self.logger.error("Market Place : {0} is not present in db : {1}".format(fparam_market, str(ex)))
        else:
            error_msg += "FParameter {} value is not set\n".format('MARKET_UPLOAD_ex')
            self.logger.error("FParameter {} value is not set".format('MARKET_UPLOAD_ex'))

        if error_msg:
            return error_msg
        else:
            return True


    def check_mandatory_fparameters(self, mandatory_fparameter_dict):
        self.logger.debug("Checking mandatory FParameters")
        is_valid = True
        invalid_fparam = []
        valid_msg = "FParameter:{0} value:{1} is VALID"
        invalid_msg = "FParameter:{0} value:{1} is INVALID"
        for param_key, param_value in mandatory_fparameter_dict.items():
            set_value = self.config.get(param_key, None)
            eval_value = None
            if set_value != None:
                try:
                    eval_value = eval(set_value)
                except Exception as ex:
                    pass
                if param_key == 'BBG_REQUEST_FIELDS_LIST_FILE':
                    if set_value.endswith('.txt'):
                        self.logger.info(valid_msg.format('BBG_REQUEST_FIELDS_LIST_FILE', set_value))
                    else:
                        self.logger.error(invalid_msg.format('BBG_REQUEST_FIELDS_LIST_FILE', set_value))
                        is_valid = False
                        invalid_fparam.append(param_key)
                elif param_value == 'file_path':
                    if os.path.exists(set_value):
                        self.logger.info(valid_msg.format(param_key, set_value))
                        is_valid = True
                    else:
                        self.logger.error(invalid_msg.format(param_key, set_value))
                        is_valid = False
                        invalid_fparam.append(param_key)
                elif type(param_value) == list:
                    if type(set_value) == list and (set_value[0] in param_value):
                        self.logger.info(valid_msg.format(param_key, set_value))
                        is_valid = True
                    elif set_value in param_value:
                        self.logger.info(valid_msg.format(param_key, set_value))
                    else:
                        self.logger.error(invalid_msg.format(param_key, set_value))
                        is_valid = False
                        invalid_fparam.append(param_key)
                elif type(set_value) == param_value:
                    self.logger.info(valid_msg.format(param_key, set_value))
                    is_valid = True
                elif type(eval_value) == param_value:
                    self.logger.info(valid_msg.format(param_key, set_value))
                    is_valid = True
                else:
                    self.logger.error(invalid_msg.format(param_key, set_value))
                    is_valid = False
                    invalid_fparam.append(param_key)
            else:
                self.logger.info("Mandatory FParameter {0} not exist".format(param_key))
                invalid_fparam.append(param_key)
                
        if not invalid_fparam:
            return True
        else:
            error_msg = "Invalid value set for FParameters {}".format(invalid_fparam)
            self.logger.error(error_msg)
            return error_msg


    def check_state_chart(self):
        self.logger.debug("Checking state chart")
        is_exist = False
        try:
            chartName = 'DataLoaderInstrumentUpload'
            state_chart = acm.FStateChart[chartName]
            if state_chart:
                self.logger.info("State Chart {} already exist".format(chartName))
                is_exist = True
            else:
                self.logger.info("State Chart {} not exist.".format(chartName))
        except Exception as ex:
            self.logger.info("State Chart {0} not exist: {1}".format(chartName, str(ex)))
        if is_exist:
            return is_exist
        else:
            return "State Chart {} not exist.".format(chartName)
        

    def check_version_compatibility(self, supported_version_module_dict, installed_version_dict):
        result= True;
        version_string = ''
        error_msg = ''
        incompatible_list = []
        from distutils.version import StrictVersion 
        for supported_module, supported_version in supported_version_module_dict.items():
            for installed_module, installed_version in installed_version_dict.items():
                if installed_module == supported_module:
                    if StrictVersion(supported_version) <= StrictVersion(installed_version):
                        version_string = "{0} - Supported Version:{1}(Current Version:{2}) - Versions are compatible.".format(installed_module, supported_version, installed_version)
                        self.logger.info(version_string)
                    else:
                        version_string = "{0} - Supported Version:{1}(Current Version:{2}) - Versions are incompatible.".format(installed_module, supported_version, installed_version)
                        self.logger.error(version_string)
                        incompatible_list.append(installed_module)
                        result= False
                
        if result:
            return result
        else:
            error_msg = "{} Versions are incompatible ".format(incompatible_list)
            self.logger.error(error_msg)
            return error_msg
            
            
