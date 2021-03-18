#!/bin/bash

sudo yum update -y
sudo yum install jq -y
sudo yum install python37 -y

curl -s https://rpm.nodesource.com/setup_12.x | bash
sudo yum -y install nodejs

# Setup C9
sudo yum -y groupinstall "Development Tools"
su ec2-user -c "curl -L https://raw.githubusercontent.com/c9/install/master/install.sh | bash"

# Additional setup
sudo yum install -y amazon-linux-extras
amazon-linux-extras enable php7.4
sudo yum clean metadata
sudo yum install -y php php-{pear,cgi,common,curl,mbstring,gd,mysqlnd,gettext,bcmath,json,xml,fpm,intl,zip,imap} 

# @todo : Create a C9 environment and use the key 
echo "ssh-rsa ZhckQoqweRdMIqAG+6m5l1Of+Ga//C6Z72IwTfIfONsQ6gSfOcwRTg23jN+IW23JSerp1bSOPNEk28KL77Vwi/UFgzA19pWY5mUPXjcn+029twut1CNVywqweBZlpo02jGfMrXnQkuWrlw7eXQ+hLBIq8oFM5EgdVeDLPbmmDWxl8bWIZX70HYwzHzg2CEHG00N75XZp1lNMMPf3b1xc0tnT5eRuMHfQsMVCyOSVWeVb9uJO7S03as71/yOM+TZiwEvb7/jmk5vCddF9qjaSMfMcBbaM6CqW78Rae+fqqcl5SUtDlv9oVvO5W8NQolvaydk7YYbGTLAMuAuTfjWxarwpicdmMGKd519rdx4P1joU3bfQUW8zWJqBUbwQ36L2yYcjhOqQXTFQmHXR7qrIrQSeF7ik5/fipVJG9N2y4fRlFFQ45FpB/wnjvt2V2Q1NHdcznEwFkZ3lxg6rIOEJKKNan6ZEc1qqsAEiIl3i7A6PZNwt2KoEM4DL+Aejlj/7zdZlhc7RQGEg7b679+m9EU7dQnkowbTsOXR91jYXcZQI/Lv3NygacgALTGF6DAdXf+oAH8q/GY1zetTRnWyyg+q+T5hRPK9Bzitt1Kq4sgwR/ifl996VWgNAQ== bob+123455431432@cloud9.amazon.com" >> /home/ec2-user/.ssh/authorized_keys
