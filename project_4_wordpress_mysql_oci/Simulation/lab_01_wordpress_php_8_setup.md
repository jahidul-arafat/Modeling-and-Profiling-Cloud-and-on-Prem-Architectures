# Install WordPress CMS on Oracle Linux with MySQL database
By Jahidul Arafat
## Prerequisite
- [x] VCN Setup: 10.0.0.0/16
- [x] 2x Subnet: 1 Public Subnet (10.0.0.0/24), 1 Private Subnet (10.0.1.0/24)
- [x] Security List:
    - [x] Default: 0.0.0.0/0 80 TCP
      - [x] Pvt instance:  
        - 10.0.0.0/24 3306  TCP 
        - 10.0.0.0/24 33060 TCP
- [x] MySQL Database setup at Oracle cloud/ under the above vcn in private subnet
    - this DB will be accessed from a bastion server/ webserver in public subnet
    - make sure you can connect to your OCI MySQL DB using <mysqlsh> command
    - mak sure you have tested the mysql db connection with <MySQL WorkBench with TCP/IP SSH Connection setup>
- [x] 1x OCI Compute Instances with Oracle Linux 8 (in public subnet) which will act as your webserver and bastion host to connect to remote mysql database at OCI.

---
## Existing Wordpress Installation as Suggested by OCI in their lab
#### https://docs.oracle.com/en/learn/wrdprs_mysqldbs_wrkshp/index.html#introduction
#### https://github.com/oracle-quickstart/oci-arch-wordpress-mds/blob/master/modules/wordpress/scripts/install_php74.sh
#### Problems in the existing setup:
- [x] PHP Version used: 7.2
- [x] RPM used: epel-7 and remi-7 which leads to a conflicts and corrupts the **yum update** and **dnf update** operations
- [x] and this begins when you try to enable remi-php74 as suggested in the oci lab above
- [x] this results in **yum update** and **dnf update** operations are breaking
- [x] also you can't find the intended module named **php-mcrypt** and leads you to error
- [x] Let's check the PHP setup in the OCI Lab for wordpress setup which is leading to all these troubles

```shell
# Setup leading to trouble
> sudo yum -y install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
> sudo yum -y install https://rpms.remirepo.net/enterprise/remi-release-7.rpm
> sudo yum-config-manager --enable remi-php74
```
###  What if you have executed these three commands and don't know how to clean it up ? 
#### You can't proceed without cleaning it !!!!
Cleaning this setup is even more complicated if you already installed php packages from it as this will lead you to the **php:remi-7.2** stream and you
have to reset it first if you want to install **php8.1** from **php:remi-8.1 stream**, else this will lead you to a conflict.
How to clean up this broken repos and modules:
```shell
> cat /etc/os-release
> sudo rm -rf /etc/yum.repos.d/remi*
> sudo rm -rf /etc/yum.repos.d/epel*
> sudo yum update
> sudo rpm -qa|grep remi
> sudo rpm -e remi-release-7.9-3.el7.remi.noarch
> sudo rpm -qa|grep epel
> sudo rpm -e epel-release-7-14.noarch
> sudo yum update
> rpm -qa |grep php
> sudo yum -y remove php*
> php --version   # php and all its modules will be uninstalled by now. But still there is a problem as the earlier php was from remi-7.2 stream. we have to reset it now.
> sudo dnf reset remi-7.2  # reset the php remi stream as we will go for the stream php:remi-8.1
```

---


## Now follow the clean PHP-8.1 installation from **REMI** repository with **mysqlsh** agent and WordPress Latest Version

#### Step-0. SSH to your bastion host/webserver
> ssh -i <your_private_key> opc@<public_ip_address_of_your_bastion_or_webserver>

#### Inside the Compute Instance of OCI as user: <opc>
#### Step-1. Update your repos
```shell
sudo dnf update
sudo yum update
```


#### Step-2. Install mysql 8 repos and mysqlsh agent to connect to the remote MySQL DB at OCI
```shell
sudo yum -y install https://dev.mysql.com/get/mysql80-community-release-el7-3.noarch.rpm
sudo yum -y install mysql-shell
mysqlsh --sql -uadmin -p -h<private_endpoint/ip_of_your_mysql_db>  # this is the private endpoint of my mysql database
    ----
    > show databases;
    ----
```

#### Step-3. Install Apache Webserver and enable the service
```shel
sudo yum install httpd -y
sudo systemctl enable httpd --nowl
```

#### Step-4. Configure your webserver firewall
```shell
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --reload
sudo firewall-cmd --list-all
```

#### Step-5. PHP-8 Setup, creating a info.php page and start the httpd service to check if the page is loading in browser
```shell
sudo dnf install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm
sudo dnf install -y https://rpms.remirepo.net/enterprise/remi-release-8.rpm
sudo dnf module list php
sudo dnf module enable php:remi-8.1 -y
sudo yum repolist enabled
sudo dnf install php php-cli php-common php-zip php-gd php-mcrypt php-mbstring php-xml php-json php-mysqlnd
php --version
httpd -M |grep php
sudo vim /var/www/html/info.php
    ---
    <?php
        phpinfo();
    ?>
    ---
sudo systemctl restart httpd
# now got the browser http://<you-public-ip-address>/info.php
```

### Step-6. Wordpress CMS Setup
```shell
curl -O https://wordpress.org/latest.tar.gz
sudo tar zxf latest.tar.gz -C /var/www/html/ --strip 1
id apache
sudo chown apache. -R /var/www/html/
ll /var/www/
ll /var/www/html/
sudo mkdir /var/www/html/wp-content/uploads
sudo chown apache:apache /var/www/html/wp-content/uploads
ll -d  /var/www/html/wp-content/uploads
```

#### Step-7. SELINUX Setup and  Let Apache server to connect to remote MySQL Database at Oracle Cloud
```shell
sudo chcon -t httpd_sys_rw_content_t /var/www/html -R
sudo setsebool -P httpd_can_network_connect_db 1
```

### Step-8. Create a database named "wordpress" with user named "wordpress" and grant all privileges to <user> to deal with <database>
```shell
mysqlsh --sql -uadmin -h10.0.1.84
    ---
    > create database wordpress;
    > create user wordpress IDENTIFIED BY 'ComplexPass0rd!';
    > GRANT ALL PRIVILEGES ON wordpress.* To wordPress;
    (Press) CTRL+D (to exit)
    ---
```

### Step-9. Let's configure the wordpress setup-config.php
- [x] From a browser access http://instance public IP/wp-admin/setup-config.php.
- [x] Click Let's Go.
- [x] Fill the following information:
    - [x] Database Name: wordpress
    - [x] Username: wordpress
    - [x] Password: ComplexPass0rd!
    - [x] Database Host: MySQL Database Service IP address
    - [x] Table Prefix: leave as is.
- [x] Click Run the installation.
- [x] Fill the following information in the welcome screen:
    - [x] Site Title: WordPress Setup in Oracle Cloud Infrastructure by Jahidul Arafat
    - [x] Username: admin
    - [x] Password: ComplexPass0rd!
    - [x] Your Email: jahidularafat@yahoo.com
- [x] Click Install WordPress.
- [x] From a browser access http://instance public IP/wp-login.php and star managing your new WordPress installation.

