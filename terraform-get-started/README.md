# Tutorial 

https://learn.hashicorp.com/tutorials/terraform/install-cli?in=terraform/aws-get-started

```
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://rpm.releases.hashicorp.com/RHEL/hashicorp.repo
sudo yum -y install terraform
terraform -install-autocomplete
```


# Create a tf file
```
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.27"
    }
  }
}

provider "aws" {
  profile = "default"a
  region  = "us-west-2"
}
```

```
$ teraform init
```

```
$ teraform plan
```

```
$ teraform apply
```


## Code samples

https://github.com/terraform-aws-modules/terraform-aws-vpc



