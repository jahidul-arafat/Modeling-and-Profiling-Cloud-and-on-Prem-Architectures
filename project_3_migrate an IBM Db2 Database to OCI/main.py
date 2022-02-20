#!/usr/bin/env python3
from pytm import (
    TM,
    Boundary,
    Process,
    Datastore,
    DatastoreType,
    Classification,
    Data,
    Dataflow,
    Element,
    ExternalEntity
)

# Step-0: Setting up the Threat Model
tm=TM("Modeling Migrate an IBM Db2 Database to Oracle Cloud Architecture")
tm.description="""
Convert an IBM Db2 (LUW - Linux, Unix & Windows) database to Oracle Autonomous Data Warehouse (ADW) in 
Oracle Cloud Infrastructure to take advantage of the expanded capabilities offered with Oracle PL/SQl and an 
Autonomous Database.An ADB scales elastically and delivers fast query performance without high-overhead database administration.

<b>Several Core Components of this Threat Modeling Migration Architecture includes:</b><br>
<b>@on-prem</b> <br>
(a) A CPE (Customer-premises equipement) endpoint for the VPN Connect or OCI FastConnect interconnection between the on-prem data center and the VCN in OCI
(b) An Opn-premises Data Center having IBM Db2 (RDBMS)
(c) Several RDBMS database administration and export tools including:
    - Oracle SQL Developer: which is a migration platform for moving IBM Db2 (3rd party) database to OCI
    - SQL*Loader: Loads data from external file to Oracle Database. It uses the <FIELD SPECIFICATIONS> in <CONTROL FILES> 
    to interprete the format of the datafiles, parse and populate the <BIND ARRAY> that corresponds to SQL INSERT statement.
    Oracle Database accepts the data abd executes the <INSERT> statement to store the data in the database.
    - Export utility: Its an export program utility that bulk copies data between IBM Db2 Database instance and a data file in user-specified format

@OCI
(a) Region, AD, FD, Compartments
(b) VCN (Non-overlapping with Other Networks in OCI, on-prem or anyother cloud provider to which you intend to setup the private connection),
 Subnets, DRG, Service Gateway, RT, SL, Bastion Service/host
(c) Cloud Guard @ tenancy level - Detectors recipe (use Managed List Features),Responder recipe
(d) Autonomous Database (ADB)
(e) Object Storage
"""

tm.isOrdered = True
tm.mergeResponses = True

tm.highlights = [
    "one",
    "two",
    "three"
]

tm.assumptions = [
    "01: Data and Metadata are migrated from an on-prem IBM Db2 Database deployment to an OCI Autonomous Database Warehouse",
    "02: IPSec VPN or OCI FastConnect securely connects CPE at on-prem DC to DRG at OCI",
    "03: @on-prem DC, SQL Developer is used as a migration platform for moving IBM Db2 database to OCI ADB",
    "04: @on-prem DC, SQL*Loader loads data from external file into tabkes of an Oracle Database. User defined the field specifications in a control file to interprete the format of the datafile",
    "05: @on-prem DC, Export utility is used to export metadata(i.e. table of tables in a db, their size + #rows in each table; table of columns in each database + type of data store in each column + which tables used those columns) to ADB directly",
    "06: @on-prem DC, Export utility is used to export data to OSS @OCI [if DB Size < 1TB] which then export the data to ADB",
    "07: @on-prem DC, IF DBSIZE > 1TB, then use FSS @OCI and (NFS) mount  it at on-prem DC to export the data using export utility instead of OSS@OCI",
    "08: VCN in OCI is non-overlapping with Network @on-prem DC",
    "09: @OCI ADB is configured with 2x OCPUS and 1TB storage with autoscaling enabled for optimum price and performance",
    "10: @OCI CloudGuard is enabled at tenancy level with Managed List Features to apply certain configurations at detector to maintain and monitor the security of your resources in OCI ",
    "11: DRG is used @OCI to provide a private path between OCI VCN and on-prem DC",
    "12: Service Gateway is used to connect to Object Storage Service from the VCN so that traffic never traverses the internet",
    "13: Bastion Service instead of Bastion host @privateSubnet of OCI VCN is used to connect to the private compute instance or ADB in OCI with a session duration is 3hrs",
    "14: If Bastion Host is used instead of Bastion Service, it is assumed that you put this in a DMZ, which cant be access publicly as set in a private subnet",
    "14: Route Tables is properly configured with rules to route traffic from subnets to destinations outside a VCN, typically through gateways i.e. DRG and Service Gateway.",
    "15: Security Lists are properly configured for SSH, NFS access in both ingress and egress settings",
    "16: Manual ADB backup is not enabled and OCI handles all the backing up, patching, upgrading and tuning the database"
]

# Sep-1: Define and design the System Components
# by default all components are inScope of threat profiling. If you want to keep a component out of consideration, simply use below
# componenetName.inScope = False
# 1A. CORE Components @on-prem Data Center

# A1. 1x CPE as Process
# CPE generally refers to devices such as telephones, routers, network switches, residential gateways (RG), set-top boxes,
# fixed mobile convergence products, home networking adapters and Internet access gateways that
# enable consumers to access providers' communication services
cpe = Process("CPE")
cpe.OS = "unix"
cpe.implementsCommunicationProtocol = True
cpe.tracksExecutionFlow = True
cpe.environment = "On-Prem Data Center"
cpe.allowsClientSideScripting = True

# A2. IBM Db2 Database
ibm_db2 = Datastore("IBM Db2")
ibm_db2.type = DatastoreType.SQL
ibm_db2.onPrem = True
ibm_db2.onOCI = False
ibm_db2.onADB = False
ibm_db2.controls.isHardened = True
#ibm_db2.inScope = True
ibm_db2.hasWriteAccess = True
ibm_db2.storesSensitiveData = True
ibm_db2.controls.isEncryptedAtRest = True
ibm_db2.maxClassification = Classification.RESTRICTED

# A3. SQl Development Environment
sql_dev_env = ExternalEntity("SQL Developer, SQL*Loader, Export Utility")
sql_dev_env.onPrem = True
sql_dev_env.controls.implementsAuthenticationScheme = True
sql_dev_env.protocol = "REST API"

# 1B. Core Components @OCI
# B1. DRG - Dynamic Routing Gateway
drg = Process("DRG")
drg.environment = "OCI"

# B2. SGW - Service Gateway
sgw = Process("Service Gateway")
sgw.environment = "OCI"

# B3. Bastion Host/service
# If Bastion Host, then we have to choose the type Server
bastion = Process("Bastion Service")
bastion.environment = "OCI"

# B4. Autonomous Database
adb = Datastore("Autonomous Database")
adb.type = DatastoreType.SQL
adb.onOCI = True
adb.onADB = True
adb.controls.isHardened = True
adb.controls.isEncryptedAtRest = True
adb.hasWriteAccess = True
adb.storesSensitiveData=True
#adb.inScope = True
adb.controls.isResilient=True
adb.maxClassification = Classification.RESTRICTED

# B5. Object Storage
oss = Datastore("Object Storage")
oss.type = DatastoreType.OCI_OSS
oss.onOCI = True
oss.storesLogData = True
oss.controls.isHardened = True
oss.controls.isEncryptedAtRest = True
oss.controls.isResilient = True

# B6. RT-Pvt
rt_pvt = Element("Route Table 1")
rt_pvt.environment = "OCI"

# B7. SL-Pvt
sl_pvt = Element("Security List 1")
sl_pvt.environment = "OCI"

# B8. RT-Pvt
rt_pub = Element("Route Table 2")
rt_pub.environment = "OCI"

# B9. SL-Pvt
sl_pub = Element("Security List 2")
sl_pub.environment = "OCI"

# B10. Cloud Guard
cloud_guard = Process("Cloud Guard")
cloud_guard.environment = "OCI"

# B11. OCI DB Operations tools
db_action = Process("Database Action")
db_action.environment = "OCI"
db_action.onOCI = True

# Step-2: Define the Boundaries and Boundary Mapping
# On-prem boundaries - Creating
on_prem_dc = Boundary("On-Premises Data Center")

# On-prem Boundary-to-Boundary Mapping
#sql_dev_env.inBoundary = on_prem_dc

# on-prem Component-to-Boundary Mapping
# sql_dev.inBoundary = sql_dev_env
# sql_loader.inBoundary = sql_dev_env
# exp_util.inBoundary = sql_dev_env
ibm_db2.inBoundary = on_prem_dc
cpe.inBoundary =on_prem_dc

# OCI Boundaries- Creating
oci_region = Boundary("Oracle Cloud Infrastructure Region")
oci_compartment = Boundary("Compartment-@AD1")
oci_vcn = Boundary("VCN 10.0.0.0/16-@AD1/FD1")
oci_subnetA_pub = Boundary("Regional Public Subnet A 10.0.30.0/24-@AD1/FD1")
oci_subnetB_pvt = Boundary("Regional Private Subnet B 10.0.18.0/24-@AD1/FD1")

# OCI Boundary-to-Boundary Mapping
oci_subnetA_pub.inBoundary = oci_vcn
oci_subnetB_pvt.inBoundary = oci_vcn
oci_vcn.inBoundary = oci_compartment
oci_compartment.inBoundary = oci_region

# OCI Component-to-Boundary Mapping
# Public subnet-A: 10.0.30/0
bastion.inBoundary = oci_subnetA_pub
rt_pub.inBoundary = oci_subnetA_pub
sl_pub.inBoundary = oci_subnetA_pub

# Private subnet-B: 10.0.18.0/24
adb.inBoundary = oci_subnetB_pvt
db_action.inBoundary = oci_subnetB_pvt
rt_pvt.inBoundary = oci_subnetB_pvt
sl_pvt.inBoundary = oci_subnetB_pvt

# VCN
sgw.inBoundary = oci_vcn

# Compartment
drg.inBoundary = oci_compartment
cloud_guard.inBoundary = oci_compartment
oss.inBoundary = oci_compartment


# Step-3: Define the Dataflows between Components
# 3.1 Create the tunneling using CPE, fast-connect and DRG
# a. CPE << >> DRG
cpe_to_drg = Dataflow(cpe,drg,"Interconnection between on-prem DC and OCI-VCN via IPSec VPN/FastConnect-1Gbps")
cpe_to_drg.protocol = "BGP"
cpe_to_drg.data = Data("Private ASN, Your ASN", classification=Classification.SENSITIVE,
                       description="Using BGP to prefer routes from Oracle to your on-premises network")

drg_to_cpe = Dataflow(drg,cpe,"Interconnection between on-prem DC and OCI-VCN via IPSec VPN/FastConnect-1Gbps")
drg_to_cpe.protocol = "BGP"
drg_to_cpe.data = Data("Private ASN, Your ASN", classification=Classification.SENSITIVE,
                       description="Using BGP to prefer routes from Oracle to your on-premises network")
drg_to_cpe.responseTo = cpe_to_drg

# ERROR_01: Component to Boundary Mapping is not Possible
# 3.2 IBM Db2 >> sql_dev_environment
ibm_db2_to_sql_dev_environment = Dataflow(ibm_db2,sql_dev_env,"DB Operations using SQL Developer tools")
ibm_db2_to_sql_dev_environment.protocol = "SQL"
ibm_db2_to_sql_dev_environment.dstPort = 1521
ibm_db2_to_sql_dev_environment.data = Data("cwallet.sso,ewallet.p12,keystroke,jks,ojdbc.preperties,"
                                           "sqlnet.ora,tnsnames.ora,truststore.jks", classification=Classification.RESTRICTED,
                                           description="Credential of IBM Db2 for a new connection setup in SQL Developer Environment")

# ERROR_02: Component to Boundary Mapping is not Possible
# 3.3 sql_dev_environment >> OCI ADB
sql_dev_env_to_adb = Dataflow(sql_dev_env,adb,"Export and Storing Metadata in OCI ADB")
sql_dev_env_to_adb.protocol = "SQL"
sql_dev_env_to_adb.dstPort = 1522
sql_dev_env_to_adb.data = Data("Metadata", classification=Classification.RESTRICTED,
                               description="Information about the structures that contain the actual data which will be stored in ADB")

# ERROR_03: Component to Boundary Mapping is not Possible
# 3.4 sql_dev_environment >> OCI OSS
sql_dev_env_to_oss = Dataflow(sql_dev_env,oss,"Exporting and storing DATA to OCI Object Storage")
sql_dev_env_to_oss.protocol = "HTTPS"
sql_dev_env_to_oss.dstPort = 443
sql_dev_env_to_oss.data = Data("Data", classification=Classification.RESTRICTED,
                               description="Actual Data which will be stored in Object Storage Bucket. However if Database size > 1TB, File System Storage is preferable")

# 3.5 OSS << >> SGW
# If service gateway, no IGW or NGW is needed as traffic never travels internet
# Resources in your on-premises network that is connected to the service gateway's VCN with FastConnect or Site-to-Site VPN can also use the service gateway
oss_to_sgw = Dataflow(oss,sgw,"Importing/Exporting data from/to OSS to ADB via SGW")
oss_to_sgw.protocol = "HTTP/TCP/IP/Rest API"
oss_to_sgw.data = Data("CIDR label, Route Rules", classification=Classification.PUBLIC,
                       description="Object Storage Bucket CIDR and Route rules for the Service Gateway for VCN to OCI service connectivity, not traversing the internet")


sgw_to_oss = Dataflow(sgw,oss,"Importing/Exporting data from/to OSS to ADB via SGW")
sgw_to_oss.protocol = "HTTP/TCP/IP/Rest API"
sgw_to_oss.data = Data("CIDR label, Route Rules", classification=Classification.PUBLIC,
                       description="Object Storage Bucket CIDR and Route rules for the Service Gateway for VCN to OCI service connectivity, not traversing the internet")

sgw_to_oss.responseTo = oss_to_sgw

# 3.6 SGW << >> ADB
sgw_to_adb = Dataflow(sgw,adb,"Importing/Exporting data from/to OSS to ADB via SGW")
sgw_to_adb.protocol = "HTTP/TCP/IP/Rest API"
sgw_to_adb.data = Data("CIDR label, Route Rules", classification=Classification.PUBLIC,
                       description="Object Storage Bucket CIDR and Route rules for the Service Gateway for VCN to OCI service connectivity, not traversing the internet")

adb_to_sgw = Dataflow(adb,sgw,"Importing/Exporting data from/to OSS to ADB via SGW")
adb_to_sgw.protocol = "HTTP/TCP/IP/Rest API"
adb_to_sgw.data = Data("CIDR label, Route Rules", classification=Classification.PUBLIC,
                       description="Object Storage Bucket CIDR and Route rules for the Service Gateway for VCN to OCI service connectivity, not traversing the internet")
adb_to_sgw.responseTo = sgw_to_adb

# 3.7 Bastion service >> ADB
bastion_to_adb = Dataflow(bastion,adb,"Restricted and time-limit secure access to ADB")
bastion_to_adb.protocol = "SSH"
bastion_to_adb.dstPort = 22
bastion_to_adb.data = Data("Authentication, Symmetric Key", classification=Classification.RESTRICTED,
                           description="Secure SSH Connection to OCI ADB in private subnet")

# 3.8 db_action >> adb
adb_to_db_action = Dataflow(adb, db_action, "Execute queries and scripts and create database scripts")
adb_to_db_action.protocol = "SQL"
adb_to_db_action.data = Data("SQL Queries and Scripts", classification=Classification.RESTRICTED,
                             description="Oracle Database Action SQL Workspace")

if __name__ == "__main__":
    tm.process()













