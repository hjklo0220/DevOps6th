terraform {
  required_providers {
    ncloud = {
      source = "NaverCloudPlatform/ncloud"
    }
  }
  required_version = ">= 0.13"
}

// Configure the ncloud provider
provider "ncloud" {
  access_key = var.NCP_ACCESS_KEY
  secret_key = var.NCP_SECRET_KEY
  region = "KR"
  site = "PUBLIC"
  support_vpc = true
}

# vpc
resource "ncloud_vpc" "lion-vpc" {
  ipv4_cidr_block = "10.1.0.0/16"
  name = "lion-tf-${var.env}"
}

