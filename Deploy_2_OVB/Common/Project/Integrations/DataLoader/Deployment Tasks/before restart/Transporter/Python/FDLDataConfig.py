"""-------------------------------------------------------------------
MODULE
    FDLDataConfig - DataPrep script

DESCRIPTION
    Data preparation script to create required setup for DataLoader

--------------------------------------------------------------------"""

import acm, ael, amb
import FIntegrationUtils
import FDLConfigSingleton
import FDLAddBusinessCentres
import FDLSemanticMigration
import FDLFileOperations
import FDLUtils

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

class DataloaderSetup():

    def  __init__(self, logger, provider, config_variables_obj):
        self.config = config_variables_obj.config_data()
        self.logger = logger
        self.provider = provider
        self.file_ops_obj = FDLFileOperations.FDLFileHandlingOps(config_variables_obj)

    def set_additional_info_specs(self, additional_info_specs):
        """ Set instrument additional info specs """
        for addinfo in additional_info_specs:
            is_created = True
            try:
                utils_obj.create_additional_info_spec(addinfo)
                self.logger.LOG("Created additional info {} for Instrument".format(addinfo['FieldName']))
            except FIntegrationUtils.AddInfoSpecAlreadyExits as e:
                self.logger.LOG(str(e))
            except Exception as e:
                self.logger.ELOG("Exception in set_instrument_additional_info_specs : %s"%str(e))
                is_created = False
        return is_created

    def set_instrument_alias_type(self, instrument_alias_type):
        """ Set instrument alias type """
        is_created = True
        for alias in instrument_alias_type:
            try:
                utils_obj.create_alias_type(alias.get('Table'), alias.get('Description'), alias.get('FieldName'), alias.get('FieldName'))
                self.logger.LOG("Created Alias type {} for Instrument".format(alias.get('FieldName')))
            except FIntegrationUtils.AliasTypeAlreadyExist as e:
                self.logger.LOG(str(e))
            except Exception as e:
                self.logger.ELOG("Exception in set_instrument_alias_type : %s"%str(e))
                is_created = False
        return is_created

    def set_party_alias_type(self, party_alias_type):
        """ Set party alias type """
        is_created = True
        for alias in party_alias_type:
            try:
                utils_obj.create_alias_type(alias.get('Table'), alias.get('Description'), alias.get('FieldName'), alias.get('FieldName'))
                self.logger.LOG("Created Alias type {} for Party".format(alias.get('FieldName')))
            except FIntegrationUtils.AliasTypeAlreadyExist as e:
                self.logger.LOG(str(e))
            except Exception as e:
                self.logger.ELOG("Exception in set_party_alias_type {}: {}".format(alias.get('FieldName'), str(e)))
                is_created = False
        return is_created

    def create_information_queries_trade(self):
        """ Cretae information queries for external objects on trades"""
        is_created = True
        try:
            s_query = acm.FSQL['DataLoader_ExternalObjects_Trade']
            if not s_query:
                s_query = acm.FSQL('')
                s_query.Name = 'DataLoader_ExternalObjects_Trade'
                s_query.Text = """
        /* Select external objects and display the missing security id and id type */
        select
        seqnbr,
        external_ref,
        creat_time,
        updat_time,
        integration_subtype,
        integration_type,
        ael_s(,'FDLProfile.get_sec_idtype_from_external_obj', seqnbr) 'Security IDType',
        ael_s(,'FDLProfile.get_sec_id_from_external_obj', seqnbr) 'Security ID'
    
        from
        ExternalObject
    
        where
        integration_subtype = 'Trade'
        and integration_type = 'DL_Complementor'"""
                s_query.Commit()
                self.logger.LOG("Created information query for Trade")
            else:
                self.logger.LOG("Information query for Trade already exist")
        except Exception as e:
            self.logger.ELOG("Exception in create_information_queries_trade : %s"%str(e))
            is_created = False
        return is_created

    def create_information_queries_instrument(self):
        """ Cretae information queries for external objects on instrument """
        is_created = True
        try:
            s_query = acm.FSQL['DataLoader_ExternalObjects_Instrument']
            if not s_query:
                s_query = acm.FSQL('')
                s_query.Name = 'DataLoader_ExternalObjects_Instrument'
                s_query.Text = """
        /* Select external objects and display the missing security id and id type */
        select
        seqnbr,
        external_ref,
        creat_time,
        updat_time,
        integration_subtype,
        integration_type,
        ael_s(,'DL_Query.get_sec_idtype_from_external_obj', seqnbr) 'Security IDType',
        ael_s(,'DL_Query.get_sec_id_from_external_obj', seqnbr) 'Security ID'
    
        from
        ExternalObject
    
        where
        integration_subtype = 'Instrument'
        and integration_type = 'DL_Complementor'"""
                s_query.Commit()
                self.logger.LOG("Created information query for Instrument")
            else:
                self.logger.LOG("Information query for Instrument already exist")
        except Exception as e:
            self.logger.ELOG("Exception in create_information_queries_instrument : %s"%str(e))
            is_created = False
        return is_created

    def create_information_queries(self):
        """ Cretae information queries for external objects """
        res_trade = self.create_information_queries_trade()
        res_ins = self.create_information_queries_instrument()
        return res_trade and res_ins

    def create_price_semantic(self):
        self.logger.debug("Creating price semantic from xml lookup")
        semantic_res = True
        semantic_val_list = self.file_ops_obj.semantics_from_xml_lookup(provider=self.provider)
        for semantic in semantic_val_list:
            try:
                self.logger.debug("Creating price semantic {}".format(semantic))
                FDLSemanticMigration.create_semantic_from_template(semantic, self.provider)

                # semantic_res = utils_obj.create_price_semantic(fparam_semantic, self.provider)
                self.logger.info("Created price semantics")
            except Exception as ex:
                self.logger.error("Error creating price semantic {0} : {1}".format(semantic, str(ex)))
                semantic_res = False
        return semantic_res

    def create_price_distributor(self):
        """Creating price distributor"""
        dist_res = True
        fparam_distributor = self.config.get('PRICE_DISTRIBUTOR_ex', '')
        if fparam_distributor:
            self.logger.debug("Creating price distributor: {}.".format(fparam_distributor))
            try:
                dist_res = utils_obj.create_distributor(fparam_distributor, self.provider)
                self.logger.info("Created price distributor: {}.".format(fparam_distributor))
            except FIntegrationUtils.AlreadyExist as ex:
                self.logger.error(str(ex))
            except Exception as ex:
                self.logger.error("Error creating price distributor : {}".format(str(ex)))
                dist_res = False
        else:
            self.logger.error("FParameter {} value is not set".format('PRICE_DISTRIBUTOR_ex'))
            dist_res = False
        return dist_res

    def create_market_place(self):
        """Creating Market Place"""
        market_res = True
        fparam_market = self.config.get('MARKET_UPLOAD_ex')
        if fparam_market:
            self.logger.debug("Creating Market Place : {}.".format(fparam_market))
            try:
                market_res = utils_obj.create_marketplace(fparam_market)
                self.logger.info("Created Market Place : {}.".format(fparam_market))
            except FIntegrationUtils.AlreadyExist as ex:
                self.logger.error(str(ex))
            except Exception as ex:
                self.logger.error("Error creating Market Place : {}".format(str(ex)))
                market_res = False
        else:
            self.logger.error("FParameter {} value is not set".format('MARKET_UPLOAD_ex'))
            market_res = False
        return market_res

    def add_calendar_business_center(self):
        FDLAddBusinessCentres.logger = self.logger
        res = FDLAddBusinessCentres.setBusinessCentres()
        if res:
            self.logger.info("Added business centers to calendars")
        return res

    def create_ratings(self):
        ratings_choicelist = ['Moodys', 'S&P', 'OurRate']
        is_created = True
        for rating in ratings_choicelist:
            try:
                utils_obj.insert_element_in_choice_list('MASTER', rating, '')
                self.logger.LOG("Created rating choice list {}".format(rating))
            except FIntegrationUtils.ChoiceListAlreadyExist as e:
                self.logger.LOG("Choice List {} already exists".format(rating))
            except Exception as e:
                self.logger.ELOG("Exception in create_ratings : %s" % str(e))
                is_created = False
        return is_created

    def amb_connect(self):
        is_connected = False
        amb_address = self.config.get("MESSAGE_BROKER_ex")
        provider = self.config.get("PROVIDER_ex")
        try:
            application_name = FDLUtils.get_application_name(provider)
            is_connected = utils_obj.connect_amb(application_name, amb_address)
            msg_broker_val = FDLUtils.split_amb_details(amb_address)
            if len(msg_broker_val) >= 1 and is_connected :
                self.logger.info("Successfully Connected to AMB {}".format(msg_broker_val[0]))
            
        except Exception as ex:
            self.logger.error(
                "Unable to connect to AMB with {0} details set in FParameter {1}".format(amb_address, "MESSAGE_BROKER_ex"))
        return is_connected

    def create_amb_channels(self, component):
        dl_amb_channels = ['{}_SENDER'.format(self.config['MESSAGE_GROUP'].strip()),
                           '{}_REQUEST_SND'.format(self.config['MESSAGE_GROUP'].strip()),
                           'NOTIFY_SENDER', '{}_REQUEST_RCV'.format(self.config['MESSAGE_GROUP'].strip()),
                           'NOTIFY_{}'.format(acm.UserName())]
        channel_list = []
        channel_created = True
        if self.amb_connect():
            if component == 'DataLoader':
                channel_list = dl_amb_channels
            elif component == 'Autolink':
                channel_list = ['Autolink_Reader']
            for channel in channel_list:
                try:
                    res = self.create_channel_in_amb_db(channel)
                    if res:
                        self.logger.LOG("Channel {} is created".format(channel))
                except Exception as e:
                    self.logger.ELOG("Exception in creating channel : %s" % str(e))
                    channel_created = False
        else:
            channel_created = False
        return channel_created

    def create_channel_in_amb_db(self, channel_name):
        """ Create channels in the AMB
        :param channel_name: name of the channel to be created
        :return: True if created else False
        """
        channel_created = False
        if not self.is_channel_present(channel_name):
            try:
                amb.mb_add_system(channel_name)
                channel_created = True
            except Exception as ex:
                raise Exception(ex)
        return channel_created


    def is_channel_present(self, channel_name):
        """ Check if channel is present in the AMB
        :param channel_name: Name of the channel to check into DB
        :return: bool: True if present else False
        """
        channel_exists = False
        try:
            amb.mb_queue_init_writer(channel_name, event_cb_amb, None)
            channel_exists = True
            self.logger.LOG("Channel <%s> found in AMB" % channel_name)
        except Exception as error:
            self.logger.debug("Channel <%s> not found in AMB" % channel_name)
        return channel_exists

