locals {
  name = "${var.project}-${var.environment}"

  # Tagging standard: every resource carries these (via provider default_tags)
  common_tags = merge(var.extra_tags, {
    Project     = var.project
    Environment = var.environment
    Owner       = var.owner
    ManagedBy   = "terraform"
    Repository  = "M-a-web179/SokoSmart-Group-7-"
  })
}

module "network" {
  source = "./modules/network"

  name                = local.name
  vpc_cidr            = var.vpc_cidr
  public_subnet_count = var.public_subnet_count
}

module "security" {
  source = "./modules/security"

  name              = local.name
  vpc_id            = module.network.vpc_id
  ssh_allowed_cidrs = var.ssh_allowed_cidrs
  app_allowed_cidrs = var.app_allowed_cidrs
  app_port          = var.app_port
}

module "compute" {
  source = "./modules/compute"

  name               = local.name
  instance_type      = var.instance_type
  subnet_id          = module.network.public_subnet_ids[0]
  security_group_ids = [module.security.security_group_id]
  ssh_public_key     = file(pathexpand(var.ssh_public_key_path))
  root_volume_size   = var.root_volume_size
}
