/* update_method=0 */
select
usr.userid 'UserID'
, usr.name 'NIP / Nama Lengkap'
, grp.grpid 'Role'
, ai.value 'Unit Kerja'
, usr.inactive 'Inactive'
, usr.email 'User Email'
, usr.creat_time 'Created Date'
, max(usl.creat_time) 'Last Login'
from user usr, userlog usl , front.group grp, AdditionalInfo ai, AdditionalInfoSpec ais
where usr.usrnbr *= usl.creat_usrnbr
and usr.grpnbr = grp.grpnbr
and ai.recaddr =* usr.usrnbr
and ai.addinf_specnbr =* ais.specnbr and ais.field_name = 'Group'
and grp.grpid ~= 'INTERFACES'
group by usr.userid